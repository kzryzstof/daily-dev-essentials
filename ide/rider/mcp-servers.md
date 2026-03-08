# 10 Microsoft MCP Servers for GitHub Copilot in Rider

> Source: [10 Microsoft MCP Servers to Accelerate Your Development Workflow](https://developer.microsoft.com/blog/10-microsoft-mcp-servers-to-accelerate-your-development-workflow)

## The Servers

| # | Server | Transport | What it does |
|---|--------|-----------|-------------|
| 1 | 📚 **Microsoft Learn Docs** | `http` ✅ | Real-time semantic search across Microsoft Learn, Azure & M365 docs |
| 2 | ☁️ **Azure MCP** | `stdio` (npx) | Full Azure ecosystem: resources, databases (PostgreSQL/SQL), Monitor, Cosmos DB, Storage, Containers |
| 3 | 🐙 **GitHub MCP** | `http` ✅ or `stdio` (Docker) | GitHub repos, Actions, PRs, issues, security scanning, notifications |
| 4 | 🔄 **Azure DevOps MCP** | `stdio` (npx) | Work items, build pipelines, sprint management, repositories |
| 5 | 📝 **MarkItDown MCP** | `stdio` (uvx) | Convert PDF, DOCX, PPTX, XLSX, images, audio → Markdown |
| 6 | 🗃️ **SQL Server MCP** | `stdio` (npx) | Natural language queries against SQL Server / Azure SQL / Fabric |
| 7 | 🎭 **Playwright MCP** | `stdio` (npx) | Browser automation & test generation via accessibility snapshots |
| 8 | 💻 **Dev Box MCP** | `stdio` (npx) | Create, configure and manage Microsoft Dev Box environments |
| 9 | 🤖 **Azure AI Foundry MCP** | `stdio` (npx) | Model catalog, deployments, Azure AI Search indexes, RAG, evaluation *(experimental)* |
| 10 | 🏢 **M365 Agents Toolkit MCP** | `stdio` (npx) | Schema validation, sample code & troubleshooting for M365 / Copilot agents |

---

## `mcp.json` for GitHub Copilot in Rider

Place this file at the root of your project (`.github/mcp.json`) or in your global Copilot config directory.

> **Prerequisites:** Node.js (`npx`), Python (`uvx` via `uv`) and the relevant Azure/GitHub CLI tools authenticated.
> Docker is **not** required — GitHub MCP uses its remote HTTP endpoint here.
>
> Only **2 out of 10** servers expose a public HTTP/SSE endpoint:
> `microsoft-docs` and `github`. All others run locally via `stdio`.

```json
{
  "servers": {
    "microsoft-docs": {
      "type": "http",
      "url": "https://learn.microsoft.com/api/mcp"
    },
    "azure": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start"]
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    },
    "azure-devops": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@microsoft/azure-devops-mcp@latest"],
      "env": {
        "AZURE_DEVOPS_ORG": "${AZURE_DEVOPS_ORG}",
        "AZURE_DEVOPS_PAT": "${AZURE_DEVOPS_PAT}"
      }
    },
    "markitdown": {
      "type": "stdio",
      "command": "uvx",
      "args": ["markitdown-mcp"]
    },
    "mssql": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@microsoft/mssql-mcp@latest"],
      "env": {
        "MSSQL_CONNECTION_STRING": "${MSSQL_CONNECTION_STRING}"
      }
    },
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "devbox": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@microsoft/devbox-mcp@latest"],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "${AZURE_SUBSCRIPTION_ID}"
      }
    },
    "azure-ai-foundry": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@azure/ai-foundry-mcp@latest"],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "${AZURE_SUBSCRIPTION_ID}",
        "AZURE_RESOURCE_GROUP": "${AZURE_RESOURCE_GROUP}"
      }
    },
    "m365-agents-toolkit": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@microsoft/m365-agents-mcp@latest"]
    }
  }
}
```

---

## Notes

### Authentication & Environment Variables

Set these in your shell profile (`~/.zshrc`) or via a `.env` file:

```bash
# GitHub
export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_..."

# Azure (shared by azure, devbox, azure-ai-foundry servers)
export AZURE_SUBSCRIPTION_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export AZURE_RESOURCE_GROUP="my-resource-group"

# Azure DevOps
export AZURE_DEVOPS_ORG="https://dev.azure.com/my-org"
export AZURE_DEVOPS_PAT="..."

# SQL Server
export MSSQL_CONNECTION_STRING="Server=myserver.database.windows.net;Database=mydb;..."
```

For Azure servers, `az login` (Azure CLI) is the recommended authentication method — `DefaultAzureCredential` will pick it up automatically.

### Registering the PAT outside of `mcp.json`

Hardcoding tokens in `mcp.json` is a security risk — especially when the file is committed to source control. Use one of the following approaches instead.

#### Option 1 — Shell profile (simplest)

Add the export to `~/.zshrc` (or `~/.bashrc`), then reload your shell:

```bash
echo 'export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_..."' >> ~/.zshrc
source ~/.zshrc
```

Rider and any terminal it spawns will inherit the variable automatically. The `mcp.json` then safely references it as `${GITHUB_PERSONAL_ACCESS_TOKEN}` without ever containing the raw value.

#### Option 2 — macOS Keychain (most secure)

Store the token in the system keychain so it is never written to disk as plain text:

```bash
# Store
security add-generic-password -a "$USER" -s GITHUB_PERSONAL_ACCESS_TOKEN -w "ghp_..."

# Retrieve (add this to ~/.zshrc)
export GITHUB_PERSONAL_ACCESS_TOKEN=$(security find-generic-password -a "$USER" -s GITHUB_PERSONAL_ACCESS_TOKEN -w)
```

Adding the retrieval line to `~/.zshrc` means the token is fetched from the Keychain at shell startup and exposed as a normal environment variable for the rest of the session.

#### Option 3 — Rider environment variables (IDE-scoped)

Rider lets you define environment variables that are injected into every process it launches (terminals, run configurations, MCP servers):

1. Open **Settings / Preferences → Tools → Terminal**
2. Under **Environment variables**, click **+** and add:
   `GITHUB_PERSONAL_ACCESS_TOKEN` = `ghp_...`
3. Click **OK** — no restart required.

This keeps the token inside the IDE and out of any file on disk.

#### Option 4 — `.env` file (project-scoped, gitignored)

Create a `.env` file at the project root and make sure it is listed in `.gitignore`:

```bash
# .env  (never commit this file)
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...
AZURE_DEVOPS_PAT=...
MSSQL_CONNECTION_STRING=Server=myserver.database.windows.net;...
```

```bash
# .gitignore
.env
```

Rider natively loads `.env` files for run configurations. For MCP servers started via `stdio`, combine this with a shell loader such as [`dotenv-shell`](https://github.com/gysan/dotenv-shell) or simply `source .env` in your terminal before starting Rider.

> **Tip:** Options 2 (Keychain) and 3 (Rider env vars) are the best combination for daily use on macOS — secrets stay off disk and out of version control entirely.

### GitHub MCP — Limit toolsets to reduce context size

The remote HTTP endpoint accepts a `toolsets` query parameter to restrict which capabilities are loaded:

```json
"github": {
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/?toolsets=repos,issues,pull_requests,actions",
  "headers": {
    "Authorization": "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"
  }
}
```

If you prefer the local Docker variant (e.g. for air-gapped environments), use:

```json
"github": {
  "type": "stdio",
  "command": "docker",
  "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
           "ghcr.io/github/github-mcp-server",
           "--toolsets", "repos,issues,pull_requests,actions"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
  }
}
```

### Microsoft Learn Docs — Prompt tip

Add this to your `.github/copilot-instructions.md` to encourage the model to use the docs server:

```
You have access to microsoft.docs.mcp — use this tool to search Microsoft's latest
official documentation when handling questions about Microsoft technologies like
C#, .NET, Azure, ASP.NET Core, or Entity Framework.
```

### Azure AI Foundry — Experimental

This server is under active development. APIs and features may change. Suitable for prototyping, validate stability before production use.

### MarkItDown — Python required

`markitdown-mcp` is a Python package. Install `uv` first (`brew install uv`) so that `uvx` can run it without a manual venv.

```bash
brew install uv
```

---

## Useful Links

- [MCP docs for VS Code](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)
- [Azure MCP repository](https://github.com/Azure/azure-mcp)
- [GitHub MCP Server repository](https://github.com/github/github-mcp-server)
- [Playwright MCP repository](https://github.com/microsoft/playwright-mcp)
- [MarkItDown repository](https://github.com/microsoft/markitdown)
- [Awesome GitHub Copilot Customizations](https://github.com/github/awesome-github-copilot-customizations)

