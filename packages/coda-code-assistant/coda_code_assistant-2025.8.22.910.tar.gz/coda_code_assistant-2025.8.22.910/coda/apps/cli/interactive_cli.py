"""Interactive CLI with prompt-toolkit for enhanced user experience."""

import asyncio
from collections.abc import Callable
from pathlib import Path
from threading import Event

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from rich.console import Console

from .completers import CodaCompleter
from .constants import HISTORY_FILE
from .session_commands import SessionCommands
from .shared import CommandHandler, CommandResult, DeveloperMode

# Import moved to where it's used to avoid circular imports


class SlashCommand:
    """Represents a slash command with its handler and help text."""

    def __init__(
        self, name: str, handler: Callable, help_text: str, aliases: list[str] | None = None
    ):
        self.name = name
        self.handler = handler
        self.help_text = help_text
        self.aliases = aliases or []
        self._autocomplete_options = None

    def get_autocomplete_options(self) -> list[str]:
        """Get autocomplete options for this command."""
        if self._autocomplete_options is None:
            # Load options from command registry
            from .command_registry import CommandRegistry

            options = CommandRegistry.get_autocomplete_options()
            self._autocomplete_options = [opt[0] for opt in options.get(self.name, [])]
        return self._autocomplete_options


class InteractiveCLI(CommandHandler):
    """Interactive CLI with advanced prompt features using prompt-toolkit."""

    def __init__(self, console: Console = None) -> None:
        # Get config service once
        from coda.services.config import get_config_service

        config_service = get_config_service()

        if console:
            super().__init__(console)
        else:
            # Get themed console from config service
            super().__init__(config_service.theme_manager.get_console())

        # Get theme for styling
        self.theme = config_service.theme_manager.get_console_theme()

        self.session = None
        self.config = None  # Will be set by interactive.py
        self.provider = None  # Will be set by interactive.py
        self.commands = self._init_commands()
        self.style = self._create_style()

        # For interrupt handling
        self.interrupt_event = Event()
        self.last_escape_time = 0
        self.escape_count = 0
        self.last_ctrl_c_time = 0
        self.ctrl_c_count = 0

        # Initialize session management
        self.session_commands = SessionCommands()

        # Track terminal dimensions
        self._last_terminal_width = None

        # Initialize semantic search manager (singleton)
        self._search_manager = None

        # Initialize session with all features
        self._init_session()

    async def _check_and_warn_stale_cache(self, manager) -> None:
        """Check if cache is stale and show user-friendly warnings."""
        try:
            cache_status = await manager.check_cache_dirty()
            if cache_status["is_dirty"]:
                dirty_count = len(cache_status["dirty_files"]) + len(cache_status["missing_files"])
                if dirty_count > 0:
                    self.console.print(
                        f"[{self.theme.warning}]⚠️  Search index may be outdated ({dirty_count} files changed). "
                        f"Run '/search index .' to update.[/{self.theme.warning}]"
                    )
        except Exception:
            # Silently ignore cache check errors to not disrupt search
            pass

    def _get_current_provider(self):
        """Get current provider for model completion."""
        return self.provider

    def _get_available_themes(self):
        """Get available theme names."""
        from coda.base.theme import THEMES

        return THEMES

    def _get_available_models(self):
        """Get available model names from current provider."""
        provider = self._get_current_provider()
        if not provider:
            return []
        try:
            return provider.list_models()
        except Exception:
            return []

    def _init_commands(self) -> dict[str, SlashCommand]:
        """Initialize slash commands from the command registry."""
        from .command_registry import CommandRegistry

        # Map command names to their handlers
        handler_map = {
            "help": self._cmd_help,
            "model": self._cmd_model,
            "provider": self._cmd_provider,
            "mode": self._cmd_mode,
            "session": self._cmd_session,
            "export": self._cmd_export,
            "theme": self._cmd_theme,
            "clear": self._cmd_clear,
            "exit": self._cmd_exit,
            "map": self._cmd_map,
            "observability": self._cmd_observability,
        }

        # Add handlers for commands not yet implemented
        placeholder_handlers = {
            "tools": self._cmd_tools,
            "mcp": self._cmd_mcp,
            "search": self._cmd_search,
        }
        handler_map.update(placeholder_handlers)

        commands = {}
        for cmd_def in CommandRegistry.COMMANDS:
            if cmd_def.name in handler_map:
                commands[cmd_def.name] = SlashCommand(
                    name=cmd_def.name,
                    handler=handler_map[cmd_def.name],
                    help_text=cmd_def.description,
                    aliases=cmd_def.aliases,
                )

        return commands

    def _create_style(self) -> Style:
        """Create custom style for the prompt."""
        # Get theme-based style and extend it with additional styles
        from coda.services.config import get_config_service

        config_service = get_config_service()
        theme_manager = config_service.theme_manager
        theme_style = theme_manager.current_theme.prompt.to_dict()

        # Get the base style dictionary and add custom styles
        combined_styles = {}

        # Add theme styles (theme_style is already a dict from to_dict())
        combined_styles.update(theme_style)

        # Add custom additions
        # Get theme colors for consistent styling
        prompt_theme = theme_manager.current_theme.prompt

        combined_styles.update(
            {
                # Input field styling - THIS MAKES THEMES DISTINCTIVE!
                "": prompt_theme.input_field,  # Default style for input area
                # Additional prompt-specific styles
                "prompt.mode": prompt_theme.continuation,
                # Completion menu enhancements
                "completion-menu": prompt_theme.completion,
                "completion-menu.completion": prompt_theme.completion,
                "completion-menu.completion.current": prompt_theme.completion_selected,
                "completion-menu.meta.completion": prompt_theme.completion_meta,
                "completion-menu.meta.completion.current": prompt_theme.completion_selected,
                # Scrollbar
                "scrollbar.background": prompt_theme.toolbar,
                "scrollbar.button": prompt_theme.continuation,  # Use a muted color from prompt theme
                # Search styling
                "search": prompt_theme.search,
                "search.current": prompt_theme.search_match,
            }
        )

        return Style.from_dict(combined_styles)

    def _init_session(self):
        """Initialize the prompt session with all features."""
        # Get history file path from config
        if self.config:
            history_file_path = self.config.get_config_dir() / HISTORY_FILE
        else:
            # Fallback if config not available yet
            history_file_path = Path.home() / ".config" / "coda" / HISTORY_FILE

        # Create history directory if it doesn't exist
        history_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create key bindings
        kb = KeyBindings()

        # Note: We handle interrupts via signal handler during AI responses
        # Double escape is not reliable with prompt-toolkit during streaming

        # Create enhanced completer with all features
        completer = CodaCompleter(
            slash_commands=self.commands,
            get_provider_func=self._get_current_provider,
            session_commands=self.session_commands,
            get_themes_func=self._get_available_themes,
        )

        self.session = PromptSession(
            history=FileHistory(str(history_file_path)),
            auto_suggest=None,  # Disable auto-suggestions from history
            completer=completer,
            style=self.style,
            multiline=False,  # We'll handle multiline manually
            enable_history_search=True,
            vi_mode=False,  # Can be toggled later
            mouse_support=False,  # Disable to preserve terminal scrollback
            complete_while_typing=False,  # Only show completions on Tab
            complete_in_thread=True,  # Better performance
            complete_style="MULTI_COLUMN",  # Show completions in columns
            wrap_lines=True,
            key_bindings=kb,
        )

    def _get_mode_panel_config(self) -> dict:
        """Get mode-specific panel configuration with title and styling."""
        # Get theme for consistent color choices
        from coda.services.config import get_config_service

        config = get_config_service()
        theme = config.theme_manager.get_console_theme()

        mode_configs = {
            DeveloperMode.GENERAL: {
                "title": "💬 General Chat",
                "border_style": theme.panel_border,
                "title_style": theme.panel_title,
            },
            DeveloperMode.CODE: {
                "title": "⚡ Code Mode",
                "border_style": theme.success,
                "title_style": theme.success + " bold",
            },
            DeveloperMode.DEBUG: {
                "title": "🔍 Debug Mode",
                "border_style": theme.warning,
                "title_style": theme.warning + " bold",
            },
            DeveloperMode.EXPLAIN: {
                "title": "📚 Explain Mode",
                "border_style": theme.info,
                "title_style": theme.info + " bold",
            },
            DeveloperMode.REVIEW: {
                "title": "🔎 Review Mode",
                "border_style": theme.assistant_message,
                "title_style": theme.assistant_message + " bold",
            },
            DeveloperMode.REFACTOR: {
                "title": "🔄 Refactor Mode",
                "border_style": theme.panel_border,
                "title_style": theme.panel_title,
            },
            DeveloperMode.PLAN: {
                "title": "📋 Plan Mode",
                "border_style": theme.error,
                "title_style": theme.error + " bold",
            },
        }
        return mode_configs.get(self.current_mode, mode_configs[DeveloperMode.GENERAL])

    def _get_safe_terminal_width(self) -> int:
        """Get terminal width with minimum constraint to prevent squashing."""
        min_width = 40  # Minimum width to prevent ugly squashing
        max_width = 60  # Reduced max width for cleaner look

        try:
            width = self.console.size.width
            # Clamp between min and max
            return max(min_width, min(width, max_width))
        except Exception:
            # Fallback if console size detection fails
            return 60

    def _render_input_separator(self) -> None:
        """Render just the mode title without separator lines."""
        config = self._get_mode_panel_config()

        # Just print the mode title without any lines
        title = config["title"]

        # Print the title with mode-specific color
        self.console.print(f"[{config['title_style']}]{title}[/{config['title_style']}]")

    def _render_bottom_separator(self) -> None:
        """Render a minimal bottom separator line after input."""
        config = self._get_mode_panel_config()

        # Just print a simple, short separator line
        # This provides a subtle visual break without being too prominent
        separator = "─" * 30  # Fixed 30 character width, left-aligned

        # Left-align the separator (no padding)
        self.console.print(f"[{config['border_style']}]{separator}[/{config['border_style']}]")

    def _get_prompt(self) -> HTML:
        """Generate the prompt with mode indicator."""
        # Map Rich color names to prompt-toolkit compatible colors
        color_map = {
            "bright_cyan": "ansicyan",
            "bright_green": "ansigreen",
            "bright_yellow": "ansiyellow",
            "bright_blue": "ansiblue",
            "bright_red": "ansired",
            "blue": "ansiblue",
            "green": "ansigreen",
            "yellow": "ansiyellow",
            "red": "ansired",
            "cyan": "ansicyan",
        }

        # Get theme color for current mode
        theme_color = {
            DeveloperMode.GENERAL: self.theme.info,
            DeveloperMode.CODE: self.theme.success,
            DeveloperMode.DEBUG: self.theme.warning,
            DeveloperMode.EXPLAIN: self.theme.info,
            DeveloperMode.REVIEW: self.theme.assistant_message,
            DeveloperMode.REFACTOR: self.theme.panel_border,
            DeveloperMode.PLAN: self.theme.error,
        }.get(self.current_mode, self.theme.info)

        # Convert Rich color to prompt-toolkit color
        mode_color = color_map.get(theme_color, "ansiwhite")

        # Use prompt theme styling for the arrow
        return HTML(f"<{mode_color}>❯</{mode_color}> ")

    async def get_input(self, multiline: bool = False) -> str:
        """Get input from user with rich features."""
        # Render top separator with mode title
        self._render_input_separator()

        if multiline:
            self.console.print(
                f"[{self.theme.dim}]Enter multiple lines. Press [Meta+Enter] or [Esc] followed by [Enter] to submit.[/{self.theme.dim}]"
            )
            # Temporarily enable multiline mode
            self.session.default_buffer.multiline = True

        try:
            text = await self.session.prompt_async(
                self._get_prompt(),
                multiline=multiline,
            )
            # Reset Ctrl+C count on successful input
            self.ctrl_c_count = 0

            # Render bottom separator
            self._render_bottom_separator()

            return text.strip()
        except EOFError:
            # Still render bottom separator on EOF
            self._render_bottom_separator()
            return "/exit"
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            # Still render bottom separator
            self._render_bottom_separator()
            self.console.print()  # New line for cleaner display
            return ""
        finally:
            # Reset multiline mode
            if multiline:
                self.session.default_buffer.multiline = False

    async def process_slash_command(self, command_text: str) -> bool:
        """Process a slash command. Returns True if handled, False otherwise."""
        parts = command_text[1:].split(maxsplit=1)
        if not parts:
            return False

        cmd_name = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        # Check direct command match
        if cmd_name in self.commands:
            handler = self.commands[cmd_name].handler
            await self._execute_command_handler(handler, args)
            return True

        # Check aliases
        for _name, cmd in self.commands.items():
            if cmd_name in cmd.aliases:
                await self._execute_command_handler(cmd.handler, args)
                return True

        self.console.print(f"[{self.theme.error}]Unknown command: /{cmd_name}[/{self.theme.error}]")
        self.console.print("Type /help for available commands")
        return True

    # Command handlers
    def show_help(self) -> CommandResult:
        """Show help for commands - interactive mode specific."""
        from .shared import (
            print_command_help,
            print_developer_modes,
            print_interactive_keyboard_shortcuts,
            print_interactive_only_commands,
        )

        print_command_help(self.console, "Interactive Mode")
        print_interactive_only_commands(self.console)
        print_developer_modes(self.console)
        print_interactive_keyboard_shortcuts(self.console)

        self.console.print(
            f"[{self.theme.dim}]Type any command without arguments to see its options[/{self.theme.dim}]"
        )
        return CommandResult.HANDLED

    def _cmd_help(self, args: str):
        """Wrapper for show_help to maintain compatibility."""
        self.show_help()

    async def _cmd_model(self, args: str):
        """Switch AI model - enhanced for interactive mode."""
        if not self.available_models:
            self.console.print(
                f"[{self.theme.warning}]No models available. Please connect to a provider first.[/{self.theme.warning}]"
            )
            return

        if not args:
            # Show interactive model selector
            from .completion_selector import CompletionModelSelector

            selector = CompletionModelSelector(self.available_models, self.console)

            new_model = await selector.select_interactive()
            if new_model:
                self.current_model = new_model
                self.console.print(
                    f"\n[{self.theme.success}]Switched to model: {new_model}[/{self.theme.success}]"
                )

            else:
                self.console.print(
                    f"\n[{self.theme.warning}]Current model: {self.current_model}[/{self.theme.warning}]"
                )
        else:
            # Use the shared model switching logic
            self.switch_model(args)

    def _cmd_provider(self, args: str):
        """Switch provider."""
        self.show_provider_info(args)

    async def _cmd_mode(self, args: str):
        """Change developer mode."""
        if not args:
            # Use generic command selector
            from .command_registry import CommandRegistry
            from .generic_command_selector import create_command_selector

            selector = create_command_selector("mode", CommandRegistry.COMMANDS, self.console)
            if selector:
                mode_choice = await selector.select_interactive()
                if mode_choice:
                    self.switch_mode(mode_choice)
                else:
                    # Show current mode if cancelled
                    self.console.print(
                        f"[{self.theme.warning}]Current mode: {self.current_mode.value}[/{self.theme.warning}]"
                    )
            else:
                # Fallback
                self.console.print(
                    f"[{self.theme.warning}]Current mode: {self.current_mode.value}[/{self.theme.warning}]"
                )
        else:
            self.switch_mode(args)

    def _show_coming_soon_command(
        self, command_name: str, title: str, options: list[tuple[str, str]], usage: str
    ):
        """Helper to show coming soon commands with consistent formatting."""
        self.console.print(
            f"\n[{self.theme.bold}]{title}[/{self.theme.bold}] [{self.theme.warning}](Coming soon)[/{self.theme.warning}]"
        )
        self.console.print(
            f"\n[{self.theme.bold}]Planned {('subcommands' if 'subcommand' in usage else 'options')}:[/{self.theme.bold}]"
        )
        for option, description in options:
            self.console.print(f"  [{self.theme.info}]{option}[/{self.theme.info}] - {description}")
        self.console.print(f"\n[{self.theme.dim}]Usage: {usage}[/{self.theme.dim}]")

    async def _apply_theme_change(self, theme_name: str) -> None:
        """Apply theme change and update all necessary components."""
        from coda.services.config import get_config_service

        config_service = get_config_service()

        # Update theme in theme manager
        config_service.theme_manager.set_theme(theme_name)

        # Update config and save
        config_service.set("ui.theme", theme_name)
        config_service.save()

        # Update console from the config service's theme manager
        self.console = config_service.theme_manager.get_console()
        self.style = self._create_style()

        # Reinitialize the prompt session with new theme
        if hasattr(self, "session") and self.session:
            # Reinitialize session with new style
            self._init_session()

            # The new session will have the updated style

        self.console.print(
            f"[{self.theme.success}]✓[/{self.theme.success}] Theme changed to '[{self.theme.info}]{theme_name}[/{self.theme.info}]'"
        )
        if self.config:
            self.console.print(
                f"[{self.theme.dim}]Theme preference saved to configuration[/{self.theme.dim}]"
            )

    def _list_available_themes(self) -> None:
        """List all available themes with current selection indicator."""
        from coda.base.theme import THEMES
        from coda.services.config import get_config_service

        config_service = get_config_service()
        theme_manager = config_service.theme_manager
        self.console.print(f"\n[{self.theme.bold}]Available themes:[/{self.theme.bold}]")
        for theme_name, theme in THEMES.items():
            status = (
                f"[{self.theme.success}]●[/{self.theme.success}]"
                if theme_name == theme_manager.current_theme_name
                else f"[{self.theme.dim}]○[/{self.theme.dim}]"
            )
            self.console.print(
                f"  {status} [{self.theme.info}]{theme_name}[/{self.theme.info}] - {theme.description}"
            )

    def _show_current_theme(self) -> None:
        """Display the current theme and its description."""
        from coda.services.config import get_config_service

        config_service = get_config_service()
        theme_manager = config_service.theme_manager
        self.console.print(
            f"\n[{self.theme.bold}]Current theme:[/{self.theme.bold}] {theme_manager.current_theme_name}"
        )
        self.console.print(
            f"[{self.theme.bold}]Description:[/{self.theme.bold}] {theme_manager.current_theme.description}"
        )

    async def _execute_command_handler(self, handler: Callable, args: str) -> None:
        """Execute command handler with proper async handling."""
        if asyncio.iscoroutinefunction(handler):
            await handler(args)
        else:
            handler(args)

    async def _cmd_session(self, args: str):
        """Manage sessions."""
        if not args:
            # Use generic command selector
            from .command_registry import CommandRegistry
            from .generic_command_selector import create_command_selector

            selector = create_command_selector("session", CommandRegistry.COMMANDS, self.console)
            if selector:
                cmd_choice = await selector.select_interactive()
                if cmd_choice:
                    # Execute selected command
                    result = self.session_commands.handle_session_command([cmd_choice])
                    if result:
                        self.console.print(result)
                else:
                    # Show available commands if cancelled
                    self.console.print(
                        f"[{self.theme.warning}]Session command cancelled[/{self.theme.warning}]"
                    )
            else:
                # Fallback
                self.console.print(
                    f"[{self.theme.error}]Could not create session selector[/{self.theme.error}]"
                )
        else:
            # Pass the arguments to session commands handler
            result = self.session_commands.handle_session_command(args.split() if args else [])
            if result:
                self.console.print(result)

    async def _cmd_theme(self, args: str):
        """Change UI theme."""
        from coda.services.config import get_config_service

        config_service = get_config_service()
        theme_manager = config_service.theme_manager

        if not args:
            # Show interactive theme selector
            from .completion_selector import CompletionThemeSelector

            selector = CompletionThemeSelector(self.console)
            new_theme = await selector.select_interactive()

            if new_theme:
                try:
                    await self._apply_theme_change(new_theme)
                except ValueError as e:
                    self.console.print(f"[{self.theme.error}]Error:[/{self.theme.error}] {e}")
            else:
                # Show current theme if no selection was made
                self.console.print(
                    f"\n[{self.theme.warning}]Current theme:[/{self.theme.warning}] {theme_manager.current_theme_name}"
                )
            return

        # Handle subcommands
        if args == "list":
            self._list_available_themes()
            return

        elif args == "current":
            self._show_current_theme()
            return

        elif args == "reset":
            # Reset to default theme
            from coda.base.theme.constants import DARK

            args = DARK

        # Set the theme
        try:
            await self._apply_theme_change(args)
        except ValueError as e:
            self.console.print(f"[{self.theme.error}]Error:[/{self.theme.error}] {e}")

    async def _cmd_export(self, args: str):
        """Export conversation."""
        if not args:
            # Use generic command selector
            from .command_registry import CommandRegistry
            from .generic_command_selector import create_command_selector

            selector = create_command_selector("export", CommandRegistry.COMMANDS, self.console)
            if selector:
                format_choice = await selector.select_interactive()
                if format_choice:
                    # Export with selected format
                    result = self.session_commands.handle_export_command([format_choice])
                    if result:
                        self.console.print(result)
                else:
                    self.console.print(
                        f"[{self.theme.warning}]Export cancelled[/{self.theme.warning}]"
                    )
            else:
                # Fallback if selector creation fails
                self.console.print(
                    f"[{self.theme.error}]Could not create export selector[/{self.theme.error}]"
                )
        else:
            # Pass the arguments to session commands handler for export
            result = self.session_commands.handle_export_command(args.split() if args else [])
            if result:
                self.console.print(result)

    def _cmd_tools(self, args: str):
        """Manage MCP tools."""
        # Use the shared command handler
        result = self.handle_tools_command(args)
        return result

    def _cmd_mcp(self, args: str):
        """Manage MCP servers."""
        # Use the shared command handler
        result = self.handle_mcp_command(args)
        return result

    def _cmd_map(self, args: str):
        """Handle codebase intelligence and mapping commands."""
        from coda.base.search.cli import IntelligenceCommands

        if not hasattr(self, "_intelligence_commands"):
            self._intelligence_commands = IntelligenceCommands()

        if not args:
            # Show help for intelligence commands
            help_text = self._intelligence_commands.get_help()
            self.console.print(help_text)
            return

        # Parse the subcommand and arguments
        parts = args.split(maxsplit=1)
        subcommand = parts[0]
        subargs = parts[1].split() if len(parts) > 1 else []

        try:
            result = self._intelligence_commands.handle_command(subcommand, subargs)
            if result:
                self.console.print(result)
        except Exception as e:
            self.console.print(
                f"[{self.theme.error}]Error executing intelligence command: {e}[/{self.theme.error}]"
            )

    async def _cmd_search(self, args: str):
        """Semantic search commands."""
        parts = args.split(maxsplit=1)
        subcommand = parts[0] if parts else ""
        query = parts[1] if len(parts) > 1 else ""

        if not subcommand:
            from rich.table import Table

            from coda.services.config import get_config_service

            config = get_config_service()
            theme = config.theme_manager.get_console_theme()

            table = Table(
                title=f"[{theme.table_header}]Semantic Search Commands[/{theme.table_header}]",
                box=None,
                row_styles=[theme.table_row_odd, theme.table_row_even],
            )
            table.add_column("Command", style=theme.command, no_wrap=True)
            table.add_column("Description", style=theme.dim)

            table.add_row(
                "/search semantic <query>", "Search indexed content using semantic similarity"
            )
            table.add_row(
                "/search code <query>", "Search code files with language-aware formatting"
            )
            table.add_row("/search index [path]", "Index files or directories for search")
            table.add_row("/search status", "Show search index statistics")
            table.add_row("/search reset", "Reset search manager and clear index")

            self.console.print()
            self.console.print(table)
            self.console.print(
                f"\n[{self.theme.dim}]Tip: Try '/search index demo' to get started[/{self.theme.dim}]"
            )
            return

        # Import semantic search components
        try:
            from coda.base.search.vector_search.embeddings.mock import MockEmbeddingProvider
            from coda.base.search.vector_search.manager import SemanticSearchManager
            from coda.services.search import create_semantic_search_manager

            from .search_display import (
                IndexingProgress,
                SearchResultDisplay,
                create_search_stats_display,
            )
        except ImportError as e:
            self.console.print(
                f"[{self.theme.error}]Error loading semantic search: {e}[/{self.theme.error}]"
            )
            self.console.print(
                f"[{self.theme.warning}]Make sure to install: uv sync --extra embeddings[/{self.theme.warning}]"
            )
            return

        # Initialize display helpers
        result_display = SearchResultDisplay(self.console)
        indexing_progress = IndexingProgress(self.console)

        # Initialize search manager once (singleton pattern) or reinitialize if needed
        force_reinit = False
        if self._search_manager is None or force_reinit:
            try:
                # Try to use configured provider first
                self._search_manager = create_semantic_search_manager()
                # Get provider info
                provider_info = self._search_manager.embedding_provider.get_model_info()
                self.console.print(
                    f"[{self.theme.success}]Using {provider_info.get('provider', 'configured')} embeddings[/{self.theme.success}]"
                )
            except Exception as e:
                # Fall back to mock provider
                self.console.print(
                    f"[{self.theme.warning}]Failed to initialize configured provider: {str(e)}[/{self.theme.warning}]"
                )
                self.console.print(
                    f"[{self.theme.warning}]Using mock embeddings for demo purposes[/{self.theme.warning}]"
                )
                provider = MockEmbeddingProvider(dimension=768)
                self._search_manager = SemanticSearchManager(embedding_provider=provider)

        manager = self._search_manager

        # Check and warn about stale cache for search operations
        if subcommand in ["semantic", "code"]:
            await self._check_and_warn_stale_cache(manager)

        if subcommand == "semantic":
            if not query:
                self.console.print(
                    f"[{self.theme.error}]Please provide a search query[/{self.theme.error}]"
                )
                return

            try:
                # Show searching indicator
                with self.console.status(
                    f"[{self.theme.info}]Searching for: '{query}'...[/{self.theme.info}]"
                ):
                    results = await manager.search(query, k=5)

                # Display results with enhanced formatting
                result_display.display_results(results, query)

            except Exception as e:
                import traceback

                self.console.print(f"[{self.theme.error}]Search error: {e}[/{self.theme.error}]")
                self.console.print(f"[{self.theme.dim}]{traceback.format_exc()}[/{self.theme.dim}]")

        elif subcommand == "code":
            if not query:
                self.console.print(
                    f"[{self.theme.error}]Please provide a search query[/{self.theme.error}]"
                )
                return

            try:
                # Show searching indicator
                with self.console.status(
                    f"[{self.theme.info}]Searching code for: '{query}'...[/{self.theme.info}]"
                ):
                    # Add code-specific metadata to results
                    results = await manager.search(query, k=5)

                    # Enhance results with code metadata (temporary until proper implementation)
                    for result in results:
                        if not result.metadata:
                            result.metadata = {}
                        result.metadata["type"] = "code"
                        # Try to detect language from content
                        if "python" in result.text.lower() or "def " in result.text:
                            result.metadata["language"] = "python"
                        elif "javascript" in result.text.lower() or "function " in result.text:
                            result.metadata["language"] = "javascript"

                # Display results with code formatting
                result_display.display_results(results, query, show_metadata=True)

            except Exception as e:
                import traceback

                self.console.print(
                    f"[{self.theme.error}]Code search error: {e}[/{self.theme.error}]"
                )
                self.console.print(f"[{self.theme.dim}]{traceback.format_exc()}[/{self.theme.dim}]")

        elif subcommand == "index":
            if query == "demo":
                # Index some demo content with progress
                demo_docs = [
                    "Python is great for data science and machine learning",
                    "JavaScript is the language of the web and runs in browsers",
                    "Rust provides memory safety without garbage collection",
                    "Go is designed for concurrent programming and microservices",
                    "TypeScript adds static typing to JavaScript",
                    "Docker containers help with application deployment",
                    "Kubernetes orchestrates containerized applications",
                    "Git is essential for version control",
                    "React is a popular frontend framework",
                    "FastAPI is great for building Python APIs",
                ]

                try:
                    with indexing_progress.start_indexing(len(demo_docs)) as progress:
                        indexed_ids = []
                        for _i, doc in enumerate(demo_docs):
                            # Index one at a time to show progress
                            doc_id = await manager.index_content([doc])
                            indexed_ids.extend(doc_id)
                            progress.update(1, f"Indexing: {doc[:50]}...")

                    self.console.print(
                        f"\n[{self.theme.success}]✓ Successfully indexed {len(indexed_ids)} demo documents[/{self.theme.success}]"
                    )
                except Exception as e:
                    self.console.print(
                        f"[{self.theme.error}]Indexing error: {e}[/{self.theme.error}]"
                    )
            else:
                # Index files in the specified path
                path = Path(query or ".")

                try:
                    # Get list of files to index
                    if path.is_file():
                        # Single file
                        files = [path]
                        self.console.print(
                            f"[{self.theme.info}]Indexing file: {path}[/{self.theme.info}]"
                        )
                    else:
                        # Directory - find all code files
                        import glob

                        # Common code file extensions
                        extensions = [
                            "*.py",
                            "*.js",
                            "*.ts",
                            "*.jsx",
                            "*.tsx",
                            "*.java",
                            "*.cpp",
                            "*.c",
                            "*.h",
                            "*.hpp",
                            "*.go",
                            "*.rs",
                            "*.rb",
                            "*.php",
                            "*.swift",
                            "*.kt",
                            "*.scala",
                            "*.r",
                            "*.m",
                            "*.cs",
                            "*.sh",
                            "*.bash",
                            "*.zsh",
                            "*.fish",
                            "*.md",
                            "*.txt",
                            "*.json",
                            "*.yaml",
                            "*.yml",
                            "*.toml",
                        ]

                        files = []
                        for ext in extensions:
                            pattern = str(path / "**" / ext)
                            files.extend(Path(p) for p in glob.glob(pattern, recursive=True))

                        # Remove duplicates and sort
                        files = sorted(set(files))

                        if not files:
                            self.console.print(
                                f"[{self.theme.warning}]No code files found in {path}[/{self.theme.warning}]"
                            )
                            return

                        self.console.print(
                            f"[{self.theme.info}]Found {len(files)} files to index in {path}[/{self.theme.info}]"
                        )

                    # Ensure index is loaded before checking what files are already indexed
                    await manager._ensure_default_index_loaded()

                    # Separate already-indexed files from new files
                    indexed_files_info = getattr(manager.vector_store, "indexed_files", {})
                    already_indexed = [str(f) for f in files if str(f) in indexed_files_info]
                    new_files_to_index = [f for f in files if str(f) not in indexed_files_info]

                    # Check cache status for only the already-indexed files
                    update_needed = False
                    if already_indexed:
                        cache_status = await manager.check_cache_dirty(already_indexed)
                        stale_count = len(cache_status["dirty_files"]) + len(
                            cache_status["missing_files"]
                        )
                        if stale_count > 0:
                            update_needed = True
                            self.console.print(
                                f"[{self.theme.warning}]Found {stale_count} indexed files that need updating[/{self.theme.warning}]"
                            )

                    # Report on new files
                    if new_files_to_index:
                        self.console.print(
                            f"[{self.theme.info}]Found {len(new_files_to_index)} new files to index[/{self.theme.info}]"
                        )
                        update_needed = True

                    if update_needed:
                        # Use smart update for everything
                        with self.console.status(
                            f"[{self.theme.info}]Updating index...[/{self.theme.info}]"
                        ):
                            update_result = await manager.update_dirty_files(
                                [str(f) for f in files]
                            )

                        if update_result["updated"]:
                            self.console.print(
                                f"[{self.theme.success}]✓ Index updated:[/{self.theme.success}]"
                            )
                            if update_result["removed_chunks"] > 0:
                                self.console.print(
                                    f"  - Removed: {update_result['removed_chunks']} stale chunks"
                                )
                            if update_result["indexed_files"] > 0:
                                self.console.print(
                                    f"  - Indexed: {update_result['indexed_files']} files ({update_result['indexed_chunks']} chunks)"
                                )
                        else:
                            self.console.print(
                                f"[{self.theme.success}]{update_result['reason']}[/{self.theme.success}]"
                            )
                    else:
                        # No changes needed
                        self.console.print(
                            f"[{self.theme.success}]✓ All {len(files)} files are already up to date[/{self.theme.success}]"
                        )

                    # Show some stats
                    stats = await manager.get_stats()
                    self.console.print(
                        f"[{self.theme.dim}]Total vectors in index: {stats['vector_count']}[/{self.theme.dim}]"
                    )

                except Exception as e:
                    import traceback

                    self.console.print(
                        f"[{self.theme.error}]Indexing error: {e}[/{self.theme.error}]"
                    )
                    self.console.print(
                        f"[{self.theme.dim}]{traceback.format_exc()}[/{self.theme.dim}]"
                    )

        elif subcommand == "status":
            try:
                stats = await manager.get_stats()
                create_search_stats_display(stats, self.console)
            except Exception as e:
                self.console.print(
                    f"[{self.theme.error}]Error getting status: {e}[/{self.theme.error}]"
                )

        elif subcommand == "reset":
            # Reset the search manager and clear index files
            if self._search_manager:
                try:
                    # Clear the in-memory index
                    cleared_count = await self._search_manager.clear_index()

                    # Also delete the index files from disk
                    import shutil

                    index_dir = self._search_manager.index_dir
                    if index_dir.exists():
                        shutil.rmtree(index_dir)
                        index_dir.mkdir(parents=True, exist_ok=True)

                    self.console.print(
                        f"[{self.theme.success}]✓ Search index cleared ({cleared_count} vectors removed)[/{self.theme.success}]"
                    )
                except Exception as e:
                    self.console.print(
                        f"[{self.theme.error}]Error clearing index: {e}[/{self.theme.error}]"
                    )

            # Reset the search manager instance
            self._search_manager = None
            self.console.print(
                f"[{self.theme.warning}]Search manager reset. A new provider will be selected on next use.[/{self.theme.warning}]"
            )

        else:
            self.console.print(
                f"[{self.theme.error}]Unknown search subcommand: {subcommand}[/{self.theme.error}]"
            )

    def _cmd_clear(self, args: str):
        """Clear conversation."""
        # Clear session manager's conversation
        self.session_commands.clear_conversation()
        self.console.print(f"[{self.theme.success}]Conversation cleared[/{self.theme.success}]")
        # Note: Actual clearing is handled by the caller

    def _cmd_observability(self, args: str):
        """Manage observability and telemetry settings."""
        from coda.base.observability.commands import ObservabilityCommands
        from coda.base.observability.manager import ObservabilityManager
        from coda.services.config import get_config_service

        # Initialize observability manager if not already available
        if not hasattr(self, "observability_manager"):
            # Get the global ConfigService instance which has loaded the config files
            config_service = get_config_service()
            self.observability_manager = ObservabilityManager(config_service.config)

        # Initialize observability commands
        obs_commands = ObservabilityCommands(self.observability_manager, self.console)

        # Parse command and arguments
        args = args.strip()
        if not args:
            # Show status if no arguments
            obs_commands.show_status()
            return

        parts = args.split(None, 1)
        subcommand = parts[0].lower()
        sub_args = parts[1] if len(parts) > 1 else ""

        try:
            if subcommand in ["status", "stat"]:
                obs_commands.show_status()

            elif subcommand in ["metrics", "metric"]:
                # Check for --detailed flag
                detailed = "--detailed" in sub_args or "-d" in sub_args
                obs_commands.show_metrics(detailed=detailed)

            elif subcommand in ["health"]:
                # Extract component name if provided
                component = None
                if sub_args and not sub_args.startswith("--"):
                    component = sub_args.split()[0]
                obs_commands.show_health(component=component)

            elif subcommand in ["traces", "trace"]:
                # Parse limit parameter
                limit = 10  # default
                if "--limit" in sub_args:
                    try:
                        limit_parts = sub_args.split("--limit")
                        if len(limit_parts) > 1:
                            limit = int(limit_parts[1].strip().split()[0])
                    except (ValueError, IndexError):
                        self.console.print(
                            f"[{self.theme.error}]Invalid limit value[/{self.theme.error}]"
                        )
                        return
                obs_commands.show_traces(limit=limit)

            elif subcommand in ["export"]:
                # Parse export parameters
                format_type = "json"
                output_file = None

                if "--format" in sub_args:
                    try:
                        format_parts = sub_args.split("--format")
                        if len(format_parts) > 1:
                            format_type = format_parts[1].strip().split()[0]
                    except IndexError:
                        pass

                if "--output" in sub_args:
                    try:
                        output_parts = sub_args.split("--output")
                        if len(output_parts) > 1:
                            output_file = output_parts[1].strip().split()[0]
                    except IndexError:
                        pass

                obs_commands.export_data(format=format_type, output_file=output_file)

            elif subcommand in ["errors", "error"]:
                # Parse error command parameters
                limit = 20  # default
                days = 7  # default

                if "--limit" in sub_args:
                    try:
                        limit_parts = sub_args.split("--limit")
                        if len(limit_parts) > 1:
                            limit = int(limit_parts[1].strip().split()[0])
                    except (ValueError, IndexError):
                        self.console.print(
                            f"[{self.theme.error}]Invalid limit value[/{self.theme.error}]"
                        )
                        return

                if "--days" in sub_args:
                    try:
                        days_parts = sub_args.split("--days")
                        if len(days_parts) > 1:
                            days = int(days_parts[1].strip().split()[0])
                    except (ValueError, IndexError):
                        self.console.print(
                            f"[{self.theme.error}]Invalid days value[/{self.theme.error}]"
                        )
                        return

                obs_commands.show_errors(limit=limit, days=days)

            elif subcommand in ["performance", "perf", "profile"]:
                # Parse performance command parameters
                limit = 20  # default

                if "--limit" in sub_args:
                    try:
                        limit_parts = sub_args.split("--limit")
                        if len(limit_parts) > 1:
                            limit = int(limit_parts[1].strip().split()[0])
                    except (ValueError, IndexError):
                        self.console.print(
                            f"[{self.theme.error}]Invalid limit value[/{self.theme.error}]"
                        )
                        return

                obs_commands.show_performance(limit=limit)

            else:
                self.console.print(
                    f"[{self.theme.error}]Unknown observability subcommand: {subcommand}[/{self.theme.error}]"
                )
                self.console.print(
                    "Available subcommands: status, metrics, health, traces, export, errors, performance"
                )
                self.console.print(
                    f"Use [{self.theme.info}]/help observability[/{self.theme.info}] for more details"
                )

        except Exception as e:
            self.console.print(
                f"[{self.theme.error}]Error executing observability command: {e}[/{self.theme.error}]"
            )

    def _cmd_exit(self, args: str):
        """Exit the application."""
        self.console.print(f"[{self.theme.dim}]Goodbye![/{self.theme.dim}]")
        raise SystemExit(0)

    def reset_interrupt(self):
        """Reset the interrupt state."""
        self.interrupt_event.clear()
        self.escape_count = 0
        self.ctrl_c_count = 0

    def start_interrupt_listener(self):
        """Start signal handler for Ctrl+C during AI response."""
        import signal

        def interrupt_handler(signum, frame):
            """Handle Ctrl+C during AI response."""
            self.interrupt_event.set()

        # Store the old handler
        self.old_sigint_handler = signal.signal(signal.SIGINT, interrupt_handler)

    def stop_interrupt_listener(self):
        """Restore original signal handler."""
        import signal

        if hasattr(self, "old_sigint_handler"):
            signal.signal(signal.SIGINT, self.old_sigint_handler)
