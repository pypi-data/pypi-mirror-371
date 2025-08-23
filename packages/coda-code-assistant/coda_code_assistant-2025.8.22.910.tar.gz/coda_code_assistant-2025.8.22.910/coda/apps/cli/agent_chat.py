"""Agent-based chat functionality for the CLI."""

from rich.console import Console

from coda.base.providers.base import BaseProvider, Message
from coda.services.agents import Agent
from coda.services.agents.builtin_tools import get_builtin_tools
from coda.services.agents.tool_adapter import MCPToolAdapter

from .agent_event_handler import CLIAgentEventHandler


class AgentChatHandler:
    """Handles AI chat using the agent system."""

    def __init__(self, provider_instance: BaseProvider, cli, console: Console):
        """Initialize the agent chat handler."""
        self.provider = provider_instance
        self.cli = cli
        self.console = console
        self.agent = None
        self.use_tools = True
        from coda.services.config import get_config_service

        config_service = get_config_service()
        self.theme_manager = config_service.theme_manager
        self.console_theme = self.theme_manager.get_console_theme()

    def should_use_agent(self, model: str) -> bool:
        """Check if we should use agent-based chat."""
        # Use agent for models that support function calling
        model_info = next((m for m in self.provider.list_models() if m.id == model), None)
        supports_tools = model_info and model_info.supports_functions

        return supports_tools and self.use_tools

    def get_available_tools(self):
        """Get all available tools for the agent."""
        tools = []

        # Add built-in tools
        tools.extend(get_builtin_tools())

        # Add adapted MCP tools
        mcp_tools = MCPToolAdapter.get_all_tools()
        tools.extend(mcp_tools)

        return tools

    async def chat_with_agent(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: str | None = None,
        status=None,  # Optional status indicator from interactive mode
    ) -> tuple[str, list[Message]]:
        """
        Handle a chat interaction using an agent.

        Returns:
            Tuple of (final_response, updated_messages)
        """
        # Create or update agent
        if self.agent is None or self.agent.model != model:
            tools = self.get_available_tools() if self.should_use_agent(model) else []

            # Create event handler
            event_handler = CLIAgentEventHandler(self.console, self.theme_manager)

            self.agent = Agent(
                provider=self.provider,
                model=model,
                instructions=system_prompt
                or """You are a helpful AI assistant with access to various tools.

IMPORTANT: Only use tools when they are necessary to complete the user's request. Many requests can be answered directly without tools:
- Writing (poems, stories, jokes, explanations)
- General knowledge questions
- Math calculations you can do mentally
- Coding questions and explanations
- Casual conversation

Use tools ONLY when you need to:
- Access files or directories
- Execute commands
- Fetch real-time information
- Perform operations you cannot do directly

Each user request should be evaluated independently. Previous tool usage does not mean future requests require tools.""",
                tools=tools,
                name="Coda Assistant",
                temperature=temperature,
                max_tokens=max_tokens,
                event_handler=event_handler,
            )

        # Extract user input from last message
        user_input = messages[-1].content if messages and messages[-1].role == "user" else ""

        # Run agent with streaming
        try:
            # Update status if provided
            if status:
                status.update(
                    f"[{self.console_theme.bold} {self.console_theme.info}]Thinking...[/{self.console_theme.bold} {self.console_theme.info}]"
                )

            # Create interrupt check function
            def check_interrupt():
                return (
                    self.cli is not None
                    and hasattr(self.cli, "interrupt_event")
                    and self.cli.interrupt_event.is_set()
                )

            response_content, updated_messages = await self.agent.run_async_streaming(
                input=user_input,
                messages=messages[:-1] if messages else None,  # Exclude last user message
                max_steps=5,
                status=status,  # Pass status to agent
                interrupt_check=check_interrupt,  # Pass interrupt check function
            )

            return response_content, updated_messages

        except Exception as e:
            error_msg = f"Error during agent chat: {str(e)}"
            self.console.print(
                f"[{self.console_theme.error}]{error_msg}[/{self.console_theme.error}]"
            )
            return error_msg, messages

    async def stream_chat_fallback(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Fallback streaming chat without agent/tools."""
        full_response = ""
        first_chunk = True

        try:
            stream = self.provider.chat_stream(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            for chunk in stream:
                if first_chunk:
                    self.console.print(
                        f"\n[{self.console_theme.bold} {self.console_theme.info}]Assistant:[/{self.console_theme.bold} {self.console_theme.info}] ",
                        end="",
                    )
                    first_chunk = False

                # Check for interrupt
                if hasattr(self.cli, "interrupt_event") and self.cli.interrupt_event.is_set():
                    self.console.print(
                        f"\n\n[{self.console_theme.warning}]Response interrupted by user[/{self.console_theme.warning}]"
                    )
                    break

                self.console.print(chunk.content, end="")
                full_response += chunk.content

            # Add newline after streaming
            if full_response:
                self.console.print()

        except Exception as e:
            self.console.print(
                f"\n[{self.console_theme.error}]Error during streaming: {str(e)}[/{self.console_theme.error}]"
            )

        return full_response

    def toggle_tools(self) -> bool:
        """Toggle tool usage on/off."""
        self.use_tools = not self.use_tools
        # Reset agent to force recreation with new tool settings
        self.agent = None
        return self.use_tools
