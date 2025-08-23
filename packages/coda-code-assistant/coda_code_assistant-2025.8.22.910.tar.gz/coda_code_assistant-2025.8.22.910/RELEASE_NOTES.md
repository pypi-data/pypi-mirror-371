## What's Changed

- fix(providers): implement Langchain-compatible OCI tool conversion (2040c91)
- refactor: remove pointless comments that add no value (f5c42d8)
- refactor(cli): simplify Rich console usage by removing defensive patterns (33c111d)
- refactor(providers): standardize error handling and reduce code duplication (1dd08e6)
- restore(cli): restore proper tool result display with safe Rich handling (d88439a)
- fix(docs): escape all Rich markup in CLAUDE.md to prevent parsing errors (110223a)
- fix(docs): escape Rich markup examples in CLAUDE.md to prevent parsing errors (c08d4d3)
- fix(cli): simplify tool result display to avoid Rich markup parsing issues (598a7b6)
- fix(tool_chat): use safe Text objects in _print_response to prevent Rich markup parsing (1e38929)
- fix(theme): escape Rich markup in tool execution display to prevent parsing errors (b9dc670)
- refactor(providers): consolidate tool conversion logic and eliminate duplication (c867472)
- feat(providers): implement graceful tool fallback with intelligent warnings (525c336)
- feat(providers): add OpenAI tool support to OCI GenAI provider (6d7e71d)
- feat(providers): implement tool calling support for Ollama (8a6fe97)

**Full Changelog**: https://github.com/djvolz/coda-code-assistant/compare/v2025.8.14.0002...v2025.8.22.0910
