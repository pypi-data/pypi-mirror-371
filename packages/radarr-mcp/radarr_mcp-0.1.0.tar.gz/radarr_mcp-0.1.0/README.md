# Radarr MCP Server

A Model Context Protocol (MCP) server for [Radarr](https://radarr.video/), enabling AI assistants to manage your movie collection through natural language interactions.

## Features

- = **Search Movies** - Find movies to add to your collection
- ? **Add Movies** - Add movies with quality profiles and search options
- =? **List Movies** - View your entire movie library
- <? **Movie Details** - Get detailed information including download status
- ? **Update Movies** - Change quality profiles and trigger searches
- =? **Delete Movies** - Remove movies (with optional file deletion)
- = **Interactive Search** - Browse available releases with seeders/leechers info
- =? **Quality Profiles** - View available quality settings

## Installation

### From PyPI (Recommended)

```bash
pip install radarr-mcp
```

### From Source

```bash
git clone https://github.com/MichaelReubenDev/radarr-mcp.git
cd radarr-mcp
uv sync
```

## Usage

### Command Line

```bash
# Using uvx (if installed from PyPI)
uvx radarr-mcp --url http://localhost:7878 --api-token YOUR_API_TOKEN

# Using uv run (from source)
uv run radarr-mcp --url http://localhost:7878 --api-token YOUR_API_TOKEN

# With debug logging
uv run radarr-mcp --url http://localhost:7878 --api-token YOUR_API_TOKEN --debug
```

### With Claude Desktop

Add this to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "radarr": {
      "command": "uvx",
      "args": [
        "radarr-mcp",
        "--url", "http://localhost:7878",
        "--api-token", "YOUR_API_TOKEN"
      ]
    }
  }
}
```

### With MCP Inspector

For testing and development:

```bash
npx @modelcontextprotocol/inspector uv run radarr-mcp --url http://localhost:7878 --api-token YOUR_API_TOKEN
```

## Configuration

### Required Parameters

- `--url`: Your Radarr base URL (e.g., `http://localhost:7878`)
- `--api-token`: Your Radarr API token (found in Settings ? General ? Security)

### Optional Parameters

- `--debug`: Enable debug logging

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `search_movies` | Search for movies to add | `query` (string) |
| `add_movie` | Add a movie to Radarr | `tmdb_id` (int), `quality_profile_id` (int), `root_folder_path` (string, default: "/movies"), `search_for_movie` (bool, default: false) |
| `get_movies` | List all movies in library | None |
| `get_movie` | Get detailed movie information | `movie_id` (int) |
| `update_movie` | Update movie settings | `movie_id` (int), `quality_profile_id` (int, optional), `start_search` (bool, default: false) |
| `delete_movie` | Delete a movie | `movie_id` (int), `delete_files` (bool, default: false) |
| `interactive_search` | Browse available releases | `movie_id` (int) |
| `get_quality_profiles` | List available quality profiles | None |

## Example Workflows

### Adding a Movie

1. Search for movies: "Search for The Matrix movies"
2. Add movie: "Add The Matrix (1999) with HD-1080p quality"
3. Check status: "Show me details for The Matrix"

### Managing Your Collection

1. List movies: "Show me all my movies"
2. Update quality: "Change movie ID 123 to 4K quality and start searching"
3. Browse releases: "Show me available torrents for movie ID 123"

### Finding Downloads

1. Get movie details: "Show me the status of Inception"
2. Interactive search: "What releases are available for Blade Runner 2049?"

## Requirements

- Python 3.13+
- Radarr v3+ with API access
- Network access to your Radarr instance

## Development

```bash
# Clone the repository
git clone https://github.com/MichaelReubenDev/radarr-mcp.git
cd radarr-mcp

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run with debug logging
uv run radarr-mcp --url http://localhost:7878 --api-token YOUR_TOKEN --debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Radarr](https://radarr.video/) - The amazing movie collection manager
- [Model Context Protocol](https://modelcontextprotocol.io/) - For enabling AI tool integration
- [Anthropic](https://www.anthropic.com/) - For Claude and MCP development

## Support

- = [Report Issues](https://github.com/MichaelReubenDev/radarr-mcp/issues)
- =? [Discussions](https://github.com/MichaelReubenDev/radarr-mcp/discussions)
- =? [Radarr API Documentation](https://radarr.video/docs/api/)

---
