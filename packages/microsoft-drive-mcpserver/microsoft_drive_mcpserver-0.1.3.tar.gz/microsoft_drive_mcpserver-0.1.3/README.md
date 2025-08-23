# Microsoft OneDrive MCP

A Model Context Protocol (MCP) server that provides access to Microsoft OneDrive files and folders.


[API DOC](https://learn.microsoft.com/en-us/graph/api/driveitem-get?view=graph-rest-1.0&tabs=http)

```json

{
  "mcpServers": {
    "microsoft-drive": {
      "env": {
        "MS_CLIENT_ID": "MS_CLIENT_ID",
        "MS_CLIENT_SECRET": "MS_CLIENT_SECRET",
        "MS_ACCESS_TOKEN": "MS_ACCESS_TOKEN",
        "MS_REFRESH_TOKEN": "MS_REFRESH_TOKEN"
      },
      "command": "uvx",
      "args": [
        "microsoft-drive-mcpserver"
      ]
    }
  }
}
```