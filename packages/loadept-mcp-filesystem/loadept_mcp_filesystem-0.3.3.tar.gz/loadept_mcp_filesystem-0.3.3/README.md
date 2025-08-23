# MCP File System Server

This MCP written in python interacts with the file system

# How to use
First you need to make sure you have uvx the python package and environment manager.
```sh
uv --version
```

If you don't have it, download it using:
```sh
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```
```sh
# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or visit the official website ofe uv at: [uv website](https://docs.astral.sh/uv/)

Then define the mcp Server in the different clients
### VSCode `$env:USERPROFILE\AppData\Roaming\Code\User\mcp.json`
```json
{
	"servers": {
		"loadept-mcp-filesystem": {
			"type": "stdio",
			"command": "uvx",
			"args": ["loadept-mcp-filesystem"],
			"env": {
				"BASE_PATH": "Path:\\To\\Base\\Dir"
			}
		}
	}
}
```

### Cursor AI `$env:USERPROFILE\.cursor\mcp.json`
```json
{
  "mcpServers": {
    "loadept-mcp-filesystem": {
      "command": "uvx",
      "args": ["loadept-mcp-filesystem"]
    }
  }
}
```

### Claude Desktop `$env:USERPROFILE\AppData\Roaming\Claude\claude_desktop_config.json`
```json
{
    "mcpServers": {
        "loadept-mcp-filesystem": {
            "command": "uvx",
            "args": ["loadept-mcp-filesystem"],
			"env": {
				"BASE_PATH": "Path:\\To\\Base\\Dir"
			}
        }
    }
}
```
