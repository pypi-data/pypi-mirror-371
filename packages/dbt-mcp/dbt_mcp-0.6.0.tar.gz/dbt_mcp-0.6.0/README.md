# dbt MCP Server

This MCP (Model Context Protocol) server provides tools to interact with dbt. Read [this](https://docs.getdbt.com/blog/introducing-dbt-mcp-server) blog to learn more. Add comments or questions to GitHub Issues or join us in [the community Slack](https://www.getdbt.com/community/join-the-community) in the `#tools-dbt-mcp` channel.

## Architecture

![architecture diagram of the dbt MCP server](https://raw.githubusercontent.com/dbt-labs/dbt-mcp/refs/heads/main/docs/d2.png)

## Tools

### dbt CLI

* `build` - Executes models, tests, snapshots, and seeds in dependency order
* `compile` - Generates executable SQL from models, tests, and analyses without running them
* `docs` - Generates documentation for the dbt project
* `ls` (list) - Lists resources in the dbt project, such as models and tests
* `parse` - Parses and validates the project’s files for syntax correctness
* `run` -  Executes models to materialize them in the database
* `test` - Runs tests to validate data and model integrity
* `show` - Runs a query against the data warehouse

> Allowing your client to utilize dbt commands through this MCP tooling could modify your data models, sources, and warehouse objects. Proceed only if you trust the client and understand the potential impact.


### Semantic Layer

* `list_metrics` - Retrieves all defined metrics
* `get_dimensions` - Gets dimensions associated with specified metrics
* `get_entities` - Gets entities associated with specified metrics
* `query_metrics` - Queries metrics with optional grouping, ordering, filtering, and limiting
* `get_metrics_compiled_sql` - Gets and returns the compiled SQL that would be generated for specified metrics and groupings without executing the query


### Discovery
* `get_mart_models` - Gets all mart models
* `get_all_models` - Gets all models
* `get_model_details` - Gets details for a specific model
* `get_model_parents` - Gets parent nodes of a specific model
* `get_model_children` - Gets children models of a specific model
* `get_model_health` - Get health signals for a specific model

### SQL
⚠️ The SQL tools are implemented remotely. While MCP usage of the tools do not consume dbt Copilot credits, access to the tools will be impacted by dbt Copilot credit overages from direct usage of Copilot in dbt Platform. 
* `text_to_sql` - Generate SQL from natural language requests
* `execute_sql` - Execute SQL on dbt Cloud's backend infrastructure with support for Semantic Layer SQL syntax. Note: using a PAT instead of a service token for `DBT_TOKEN` is required for this tool.

### Admin API
* `list_jobs` - List all jobs in a dbt Cloud account
* `get_job_details` - Get detailed information for a specific job including configuration and settings  
* `trigger_job_run` - Trigger a job run with optional parameter overrides like Git branch, schema, or execution parameters
* `list_jobs_runs` - List runs in an account with optional filtering by job, status, or other criteria
* `get_job_run_details` - Get comprehensive run information including execution details, steps, artifacts, and debug logs
* `cancel_job_run` - Cancel a running job to stop execution
* `retry_job_run` - Retry a failed job run to attempt execution again
* `list_job_run_artifacts` - List all available artifacts for a job run (manifest.json, catalog.json, logs, etc.)
* `get_job_run_artifact` - Download specific artifact files from job runs for analysis or integration

## Setup

There are two ways to setup dbt MCP, [local](#local) and [remote](#remote). Local setup is best for dbt projects that you are developing in a local IDE. Remote setup is better for building custom applications.

### Local

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Copy the [`.env.example` file](https://github.com/dbt-labs/dbt-mcp/blob/main/.env.example) locally under a file called `.env` and set it with the following environment variable configuration:

#### Tools
| Name                     | Default | Description                                                                     |
| ------------------------ | ------- | ------------------------------------------------------------------------------- |
| `DISABLE_DBT_CLI`        | `false` | Set this to `true` to disable dbt Core, dbt Cloud CLI, and dbt Fusion MCP tools |
| `DISABLE_SEMANTIC_LAYER` | `false` | Set this to `true` to disable dbt Semantic Layer MCP tools                      |
| `DISABLE_DISCOVERY`      | `false` | Set this to `true` to disable dbt Discovery API MCP tools                       |
| `DISABLE_ADMIN_API`      | `false` | Set this to `true` to disable dbt Admin API MCP tools                           |
| `DISABLE_SQL`            | `true`  | Set this to `false` to enable SQL MCP tools                                     |
| `DISABLE_TOOLS`          | ""      | Set this to a list of tool names delimited by a `,` to disable certain tools    |


#### Configuration for Discovery, Semantic Layer, Admin API, and SQL Tools
| Name                       | Default            | Description                                                                                                                                                                                                                                  |
| -------------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DBT_HOST`                 | `cloud.getdbt.com` | Your dbt Cloud instance hostname. This will look like an `Access URL` found [here](https://docs.getdbt.com/docs/cloud/about-cloud/access-regions-ip-addresses). If you are using Multi-cell, do not include the `ACCOUNT_PREFIX` here        |
| `MULTICELL_ACCOUNT_PREFIX` | -                  | If you are using Multi-cell, set this to your `ACCOUNT_PREFIX`. If you are not using Multi-cell, do not set this environment variable. You can learn more [here](https://docs.getdbt.com/docs/cloud/about-cloud/access-regions-ip-addresses) |
| `DBT_TOKEN`                | -                  | Your personal access token or service token. Note: a service token is required when using the Semantic Layer and this service token should have at least `Semantic Layer Only`, `Metadata Only`, and `Developer` permissions.                |
| `DBT_PROD_ENV_ID`          | -                  | Your dbt Cloud production environment ID                                                                                                                                                                                                     |
| `DBT_ACCOUNT_ID`           | -                  | Your dbt Cloud account ID (required for Admin API tools)                                                                                                                                                                                     |

#### Configuration for SQL Tools
| Name             | Description                               |
| ---------------- | ----------------------------------------- |
| `DBT_DEV_ENV_ID` | Your dbt Cloud development environment ID |
| `DBT_USER_ID`    | Your dbt Cloud user ID                    |
|                  |                                           |

#### Configuration for dbt CLI
| Name              | Description                                                                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `DBT_PROJECT_DIR` | The path to where the repository of your dbt Project is hosted locally. This should look something like `/Users/firstnamelastname/reponame` |
| `DBT_PATH`        | The path to your dbt Core, dbt Cloud CLI, or dbt Fusion executable. You can find your dbt executable by running `which dbt`                 |
| `DBT_CLI_TIMEOUT` | Configure the number of seconds before your agent will timeout dbt CLI commands. Defaults to 10 seconds.                                    |

It is also possible to set any environment variable supported by your dbt executable (see [here](https://docs.getdbt.com/reference/global-configs/about-global-configs#available-flags) for the ones supported in dbt Core).

We automatically set `DBT_WARN_ERROR_OPTIONS='{"error": ["NoNodesForSelectionCriteria"]}'` so that the MCP server knows if no node is selected when running a dbt command.
You can overwrite it if needed but we believe that it provides a better experience when calling dbt from the MCP server, making sure that the tool is selecting valid nodes.

#### Using with MCP Clients

After going through the [Setup](#setup), you can use dbt-mcp with an MCP client.

Add this configuration to the respective client's config file. Be sure to replace the sections within `<>`:

```json
{
  "mcpServers": {
    "dbt-mcp": {
      "command": "uvx",
      "args": [
        "--env-file",
        "<path-to-.env-file>",
        "dbt-mcp"
      ]
    },
  }
}
```

`<path-to-.env-file>` is where you saved the `.env` file from the Setup step

#### Claude Code

Run the following command to add the MCP server to Claude Code:

```bash
claude mcp add dbt -- uvx --env-file <path-to-.env-file> dbt-mcp
```

By default the MCP server is installed in the "local" scope, meaning that it will be active for Claude Code sessions in the current directory for the user who installed it.

It is also possible to install the MCP server:
- in the "user" scope, to have it installed for all Claude Code sessions, independently of the directory used
- in the "project" scope, to create a config file that can be version controlled so that all developers of the same project can have the MCP server already installed

To install it in the project scope, run the following and and commit the `.mcp.json` file. Be sure to use an env var file path that is the same for all users.
```bash
claude mcp add dbt -s project -- uvx --env-file <path-to-.env-file> dbt-mcp
```

More info on scopes [here](https://docs.anthropic.com/en/docs/claude-code/mcp#understanding-mcp-server-scopes)

#### Claude Desktop

Follow [these](https://modelcontextprotocol.io/quickstart/user) instructions to create the `claude_desktop_config.json` file and connect.

For debugging, you can find the Claude Desktop logs at `~/Library/Logs/Claude` for Mac or `%APPDATA%\Claude\logs` for Windows.

#### Cursor

Note the configuration options [here](#configuration) and input your selections with this link:

<a href="https://cursor.com/install-mcp?name=dbt&config=eyJjb21tYW5kIjoidXZ4IGRidC1tY3AiLCJlbnYiOnsiREJUX0hPU1QiOiJjbG91ZC5nZXRkYnQuY29tIiwiTVVMVElDRUxMX0FDQ09VTlRfUFJFRklYIjoib3B0aW9uYWwtYWNjb3VudC1wcmVmaXgiLCJEQlRfVE9LRU4iOiJ5b3VyLXNlcnZpY2UtdG9rZW4iLCJEQlRfUFJPRF9FTlZfSUQiOiJ5b3VyLXByb2R1Y3Rpb24tZW52aXJvbm1lbnQtaWQiLCJEQlRfREVWX0VOVl9JRCI6InlvdXItZGV2ZWxvcG1lbnQtZW52aXJvbm1lbnQtaWQiLCJEQlRfVVNFUl9JRCI6InlvdXItdXNlci1pZCIsIkRCVF9QUk9KRUNUX0RJUiI6Ii9wYXRoL3RvL3lvdXIvZGJ0L3Byb2plY3QiLCJEQlRfUEFUSCI6Ii9wYXRoL3RvL3lvdXIvZGJ0L2V4ZWN1dGFibGUiLCJESVNBQkxFX0RCVF9DTEkiOiJmYWxzZSIsIkRJU0FCTEVfU0VNQU5USUNfTEFZRVIiOiJmYWxzZSIsIkRJU0FCTEVfRElTQ09WRVJZIjoiZmFsc2UiLCJESVNBQkxFX1JFTU9URSI6ImZhbHNlIn19"><img src="https://cursor.com/deeplink/mcp-install-dark.svg" alt="Add dbt MCP server to Cursor" height="32" /></a>

Cursor MCP docs [here](https://docs.cursor.com/context/model-context-protocol) for reference

#### VS Code

1. Open the Settings menu (Command + Comma) and select the correct tab atop the page for your use case
    - `Workspace` - configures the server in the context of your workspace
    - `User` - configures the server in the context of your user
    - **Note for WSL users**: If you're using VS Code with WSL, you'll need to configure WSL-specific settings. Run the **Preferences: Open Remote Settings** command from the Command Palette (F1) or select the **Remote** tab in the Settings editor. Local User settings are reused in WSL but can be overridden with WSL-specific settings. Configuring MCP servers in the local User settings will not work properly in a WSL environment.

2. Select Features → Chat

3. Ensure that "Mcp" is `Enabled`

![mcp-vscode-settings](https://github.com/user-attachments/assets/3d3fa853-2398-422a-8a6d-7f0a97120aba)

4. Open the command palette `Control/Command + Shift + P`, and select either "MCP: Open Workspace Folder MCP Configuration" or "MCP: Open User Configuration" depending on whether you want to install the MCP server for this workspace or for all workspaces for the user

5. Add your server configuration (`dbt`) to the provided `mcp.json` file as one of the servers:
```json
{
  "servers": {
    "dbt": {
      "command": "uvx",
      "args": [
        "--env-file",
        "<path-to-.env-file>",
        "dbt-mcp"
      ]
    }
  }
}
```

`<path-to-.env-file>` is where you saved the `.env` file from the Setup step

6. You can start, stop, and configure your MCP servers by:
- Running the `MCP: List Servers` command from the Command Palette (Control/Command + Shift + P) and selecting the server
- Utlizing the keywords inline within the `mcp.json` file

![inline-management](https://github.com/user-attachments/assets/d33d4083-5243-4b36-adab-72f12738c263)

VS Code MCP docs [here](https://code.visualstudio.com/docs/copilot/chat/mcp-servers) for reference

### Remote

The remote setup doesn't require running dbt MCP locally. Instead, an HTTP connection is made to dbt MCP running within dbt Cloud. Currently, only Semantic Layer & Discovery tools are supported. Note, the remote MCP server doesn't expend dbt Copilot credits but is impacted by dbt Copilot credit overages. To get started, ensure that you have [AI Features](https://docs.getdbt.com/docs/cloud/enable-dbt-copilot) turned on, and get the following information:

- dbt Cloud host: Use this to form the full URL. For example, replace `<host>` here: `https://<host>/api/ai/v1/mcp/`. It may look like: `https://cloud.getdbt.com/api/ai/v1/mcp/`.
- Production environment ID: This can be found on the `Orchestration` page of dbt Cloud. Use this to set a `x-dbt-prod-environment-id` header.
- Service token: To fully utilize Remote MCP, this needs to be configured for the dbt Semantic Layer by following [this](https://docs.getdbt.com/docs/use-dbt-semantic-layer/setup-sl#2-add-a-credential-and-create-service-tokens) guide and have `Developer` permissions. Add this as a `Authorization` header with a value like: `token <token>`. Be sure to replace `<token>` with the value of your token.

Then you can use these values to connect to the remote server with Streamable HTTP MCP transport. Use the example [here](https://github.com/dbt-labs/dbt-mcp/blob/76992ac51a905e9e0d2194774e7246ee288094b9/examples/remote_mcp/main.py) as a reference in Python. A similar implementation is possible with SDKs for many other languages.

You can also connect from MCP clients which support remote MCP with headers. For instance, you can connect Cursor to the remote server with the following configuration. Be sure to replace `<host>`, `<token>`, and `<prod-id>` with your information:

```
{
  "mcpServers": {
    "dbt": {
      "url": "https://<host>/api/ai/v1/mcp/",
      "headers": {
        "Authorization": "token <token>",
        "x-dbt-prod-environment-id": "<prod-id>",
      }
    }
  }
}
```

## Troubleshooting

- Some MCP clients may be unable to find `uvx` from the JSON config. If this happens, try finding the full path to `uvx` with `which uvx` on Unix systems and placing this full path in the JSON. For instance: `"command": "/the/full/path/to/uvx"`.

## Contributing

Read `CONTRIBUTING.md` for instructions on how to get involved!
