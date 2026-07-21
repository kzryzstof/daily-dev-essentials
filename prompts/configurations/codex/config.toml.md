
# Codex MCP Servers Configuration

Place the `mcp_servers` blocks inside `~/.codex/config.toml` to register MCP servers for OpenAI Codex CLI.

## Servers

| Server | Transport | Description |
|--------|-----------|-------------|
| 🐙 **github** | `http` | GitHub repos, PRs, issues, Actions, and secret scanning via the GitHub Copilot remote MCP endpoint. Requires a `GITHUB_TOKEN` env var. |
| 🎭 **playwright** | `stdio` | Browser automation and web scraping via accessibility snapshots. Useful for fetching live documentation or interacting with web UIs. |
| 🗂️ **atlassian** | `http` | Jira issue tracking and Confluence wiki access via the official Atlassian remote MCP endpoint. Authentication is handled by Atlassian's OAuth flow. |
| 📓 **notes** | `stdio` | Personal notes workspace — reads and writes Markdown files under the local Notes vault via a local shell script. |

```toml
[mcp_servers.github]
url = "https://api.githubcopilot.com/mcp/"
bearer_token_env_var = "GITHUB_TOKEN"

[mcp_servers.playwright]
command = "npx"
args = ["-y", "@playwright/mcp@latest"]

[mcp_servers.atlassian]
url = "https://mcp.atlassian.com/v1/mcp/authv2"

[mcp_servers.notes]
type = "stdio"
command = "/Users/christophe/Notes/BoK/prompts/scripts/notes-mcp.sh"
args = []
```