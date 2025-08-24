# example prompt in agent
I wanna change the database structure. How would Vincent say that?
I’m taking some time off next month. How would Vincent say that?


# build

git clone https://gitlab.com/jiechau/jiechau_mcp_vincent_says.git
cd jiechau_mcp_vincent_says/
uv init . --package -p 3.13
uv add mcp[cli]
uv build
uv publish --token <pypi token>


# vscode copilot

.vscode/mcp.json
{
	"servers": {
		"my-mcp-server-vincent-says": {
			"type": "stdio",
			"command": "uvx",
			"args": [
				"jiechau-mcp-vincent-says"
			]
		}
	},
	"inputs": []
}


# claude code

.claude/settings.local.json
{
  "enabledMcpjsonServers": [
    "my-mcp-server-vincent-says"
  ],
  "enableAllProjectMcpServers": true
}

.mcp.json
{
  "mcpServers": {
    "my-mcp-server-vincent-says": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "jiechau-mcp-vincent-says"
      ],
      "env": {}
    }
  }
}

