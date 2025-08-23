import argparse
import asyncio
import logging
from typing import Any

import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent

logger = logging.getLogger("radarr-mcp")

server = Server("radarr-mcp")

# Configuration - will be set from command line args
RADARR_URL = ""
RADARR_API_KEY = ""


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available Radarr tools."""
    return [
        Tool(
            name="search_movies",
            description="Search for movies in Radarr",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Movie title to search for"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="add_movie",
            description="Add a movie to Radarr",
            inputSchema={
                "type": "object", 
                "properties": {
                    "tmdb_id": {
                        "type": "integer",
                        "description": "TMDB ID of the movie"
                    },
                    "quality_profile_id": {
                        "type": "integer",
                        "description": "Quality profile ID (use get_quality_profiles to see available options)"
                    },
                    "root_folder_path": {
                        "type": "string",
                        "description": "Root folder path for the movie",
                        "default": "/movies"
                    },
                    "search_for_movie": {
                        "type": "boolean",
                        "description": "Whether to automatically search for and download the movie",
                        "default": False
                    }
                },
                "required": ["tmdb_id", "quality_profile_id"]
            }
        ),
        Tool(
            name="get_movies",
            description="Get all movies from Radarr",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_movie",
            description="Get detailed information about a specific movie",
            inputSchema={
                "type": "object",
                "properties": {
                    "movie_id": {
                        "type": "integer",
                        "description": "Radarr movie ID (use the ID from get_movies output)"
                    }
                },
                "required": ["movie_id"]
            }
        ),
        Tool(
            name="get_quality_profiles",
            description="Get all quality profiles from Radarr",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="interactive_search",
            description="Search for available releases/torrents for a movie",
            inputSchema={
                "type": "object",
                "properties": {
                    "movie_id": {
                        "type": "integer",
                        "description": "Radarr movie ID (use the ID from get_movies output)"
                    }
                },
                "required": ["movie_id"]
            }
        ),
        Tool(
            name="update_movie",
            description="Update movie settings (quality profile, search)",
            inputSchema={
                "type": "object",
                "properties": {
                    "movie_id": {
                        "type": "integer",
                        "description": "Radarr movie ID (use the ID from get_movies output)"
                    },
                    "quality_profile_id": {
                        "type": "integer",
                        "description": "New quality profile ID (optional, use get_quality_profiles to see options)"
                    },
                    "start_search": {
                        "type": "boolean",
                        "description": "Whether to start searching for the movie after update",
                        "default": False
                    }
                },
                "required": ["movie_id"]
            }
        ),
        Tool(
            name="delete_movie",
            description="Delete a movie from Radarr",
            inputSchema={
                "type": "object",
                "properties": {
                    "movie_id": {
                        "type": "integer",
                        "description": "Radarr movie ID (use the ID from get_movies output)"
                    },
                    "delete_files": {
                        "type": "boolean",
                        "description": "Whether to delete movie files from disk",
                        "default": False
                    }
                },
                "required": ["movie_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """Handle tool calls."""
    if not RADARR_URL or not RADARR_API_KEY:
        return [TextContent(type="text", text="Error: Radarr URL and API key must be configured")]
    
    if arguments is None:
        arguments = {}
    
    async with httpx.AsyncClient() as client:
        headers = {"X-Api-Key": RADARR_API_KEY}
        
        if name == "search_movies":
            query = arguments.get("query", "")
            url = f"{RADARR_URL}/api/v3/movie/lookup"
            params = {"term": query}
            
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                movies = response.json()
                
                if not movies:
                    return [TextContent(type="text", text=f"No movies found for '{query}'")]
                
                result = "Found movies:\n"
                for movie in movies[:5]:  # Limit to first 5 results
                    title = movie.get("title", "Unknown")
                    year = movie.get("year", "Unknown")
                    tmdb_id = movie.get("tmdbId", "Unknown")
                    overview = movie.get("overview", "No overview available")[:100] + "..."
                    result += f"\n• {title} ({year}) [TMDB: {tmdb_id}]\n  {overview}\n"
                
                return [TextContent(type="text", text=result)]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error searching movies: {e}")]
        
        elif name == "get_movies":
            url = f"{RADARR_URL}/api/v3/movie"
            
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                movies = response.json()
                
                if not movies:
                    return [TextContent(type="text", text="No movies in Radarr library")]
                
                result = f"Radarr library ({len(movies)} movies):\n"
                for movie in movies:
                    title = movie.get("title", "Unknown")
                    year = movie.get("year", "Unknown")
                    movie_id = movie.get("id", "Unknown")
                    status = "Downloaded" if movie.get("hasFile", False) else "Missing"
                    result += f"• ID {movie_id} - {title} ({year}) - {status}\n"
                
                return [TextContent(type="text", text=result)]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error getting movies: {e}")]
        
        elif name == "get_movie":
            movie_id = arguments.get("movie_id")
            
            try:
                # Get movie details
                movie_url = f"{RADARR_URL}/api/v3/movie/{movie_id}"
                response = await client.get(movie_url, headers=headers)
                response.raise_for_status()
                movie = response.json()
                
                # Get quality profile name
                quality_profile_id = movie.get("qualityProfileId")
                quality_profiles_url = f"{RADARR_URL}/api/v3/qualityprofile"
                profiles_response = await client.get(quality_profiles_url, headers=headers)
                profiles_response.raise_for_status()
                profiles = profiles_response.json()
                quality_profile_name = "Unknown"
                for profile in profiles:
                    if profile.get("id") == quality_profile_id:
                        quality_profile_name = profile.get("name", "Unknown")
                        break
                
                # Check for active downloads/queue items
                queue_url = f"{RADARR_URL}/api/v3/queue"
                queue_response = await client.get(queue_url, headers=headers)
                queue_response.raise_for_status()
                queue_items = queue_response.json().get("records", [])
                
                download_info = None
                for item in queue_items:
                    if item.get("movieId") == movie_id:
                        download_info = {
                            "status": item.get("status", "Unknown"),
                            "title": item.get("title", "Unknown"),
                            "progress": item.get("sizeleft", 0),
                            "total_size": item.get("size", 0),
                            "eta": item.get("timeleft", "Unknown")
                        }
                        break
                
                # Build detailed result
                title = movie.get("title", "Unknown")
                year = movie.get("year", "Unknown")
                overview = movie.get("overview", "No overview available")
                status = movie.get("status", "Unknown")
                monitored = movie.get("monitored", False)
                has_file = movie.get("hasFile", False)
                file_size = movie.get("sizeOnDisk", 0)
                file_size_gb = round(file_size / (1024**3), 2) if file_size else 0
                tmdb_id = movie.get("tmdbId", "Unknown")
                imdb_id = movie.get("imdbId", "Unknown")
                runtime = movie.get("runtime", 0)
                
                result = f"🎬 {title} ({year})\n"
                result += f"ID: {movie_id} | TMDb: {tmdb_id} | IMDb: {imdb_id}\n"
                result += f"Status: {status} | Monitored: {'Yes' if monitored else 'No'}\n"
                result += f"Quality Profile: {quality_profile_name} (ID: {quality_profile_id})\n"
                result += f"Runtime: {runtime} minutes\n\n"
                
                if has_file:
                    result += f"✅ Downloaded ({file_size_gb} GB)\n"
                elif download_info:
                    progress_percent = 0
                    if download_info["total_size"] > 0:
                        progress_percent = round(((download_info["total_size"] - download_info["progress"]) / download_info["total_size"]) * 100, 1)
                    result += f"⬇️ Downloading: {download_info['title']}\n"
                    result += f"   Status: {download_info['status']} | Progress: {progress_percent}%\n"
                    result += f"   ETA: {download_info['eta']}\n"
                else:
                    result += "❌ Not downloaded\n"
                
                result += f"\n📝 Overview:\n{overview}"
                
                return [TextContent(type="text", text=result)]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error getting movie details: {e}")]
        
        elif name == "add_movie":
            tmdb_id = arguments.get("tmdb_id")
            quality_profile_id = arguments.get("quality_profile_id")
            root_folder_path = arguments.get("root_folder_path", "/movies")
            search_for_movie = arguments.get("search_for_movie", False)
            
            # First lookup the movie details
            lookup_url = f"{RADARR_URL}/api/v3/movie/lookup/tmdb"
            params = {"tmdbId": tmdb_id}
            
            try:
                response = await client.get(lookup_url, headers=headers, params=params)
                response.raise_for_status()
                movie_data = response.json()
                
                # Prepare movie for adding
                movie_data.update({
                    "qualityProfileId": quality_profile_id,
                    "rootFolderPath": root_folder_path,
                    "monitored": True,
                    "addOptions": {
                        "searchForMovie": search_for_movie
                    }
                })
                
                # Add the movie
                add_url = f"{RADARR_URL}/api/v3/movie"
                response = await client.post(add_url, headers=headers, json=movie_data)
                response.raise_for_status()
                
                added_movie = response.json()
                title = added_movie.get("title", "Unknown")
                year = added_movie.get("year", "Unknown")
                
                return [TextContent(type="text", text=f"Successfully added '{title} ({year})' to Radarr")]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error adding movie: {e}")]
        
        elif name == "get_quality_profiles":
            url = f"{RADARR_URL}/api/v3/qualityprofile"
            
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                profiles = response.json()
                
                if not profiles:
                    return [TextContent(type="text", text="No quality profiles found")]
                
                result = "Available quality profiles:\n"
                for profile in profiles:
                    profile_id = profile.get("id", "Unknown")
                    name = profile.get("name", "Unknown")
                    result += f"• {name} (ID: {profile_id})\n"
                
                return [TextContent(type="text", text=result)]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error getting quality profiles: {e}")]
        
        elif name == "interactive_search":
            movie_id = arguments.get("movie_id")
            url = f"{RADARR_URL}/api/v3/release"
            params = {"movieId": movie_id}
            
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                releases = response.json()
                
                if not releases:
                    return [TextContent(type="text", text=f"No releases found for movie ID {movie_id}")]
                
                # Sort by seeders (highest first), treating None/missing as 0
                releases.sort(key=lambda x: x.get("seeders", 0) or 0, reverse=True)
                
                result = f"Available releases for movie ID {movie_id} (sorted by seeders):\n\n"
                
                for release in releases[:20]:  # Show top 20 releases
                    title = release.get("title", "Unknown")
                    indexer = release.get("indexer", "Unknown")
                    size_bytes = release.get("size", 0)
                    size_gb = round(size_bytes / (1024**3), 2) if size_bytes else 0
                    
                    # Get protocol (torrent vs usenet)
                    protocol = release.get("protocol", "Unknown")
                    
                    # Torrent-specific info
                    seeders = release.get("seeders")
                    leechers = release.get("leechers") 
                    
                    # Quality info
                    quality = release.get("quality", {}).get("quality", {}).get("name", "Unknown")
                    
                    # Age
                    age_hours = release.get("ageHours", 0)
                    age_days = round(age_hours / 24, 1) if age_hours else 0
                    
                    result += f"📁 {title}\n"
                    result += f"   Quality: {quality} | Size: {size_gb} GB | Age: {age_days} days\n"
                    result += f"   Indexer: {indexer} ({protocol})\n"
                    
                    if protocol.lower() == "torrent" and (seeders is not None or leechers is not None):
                        result += f"   Seeds: {seeders or 0} | Leechers: {leechers or 0}\n"
                    
                    result += "\n"
                
                if len(releases) > 20:
                    result += f"... and {len(releases) - 20} more releases available"
                
                return [TextContent(type="text", text=result)]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error searching releases: {e}")]
        
        elif name == "update_movie":
            movie_id = arguments.get("movie_id")
            quality_profile_id = arguments.get("quality_profile_id")
            start_search = arguments.get("start_search", False)
            
            try:
                # First get the current movie data
                get_url = f"{RADARR_URL}/api/v3/movie/{movie_id}"
                response = await client.get(get_url, headers=headers)
                response.raise_for_status()
                movie_data = response.json()
                
                # Update quality profile if provided
                if quality_profile_id:
                    movie_data["qualityProfileId"] = quality_profile_id
                
                # Update the movie
                put_url = f"{RADARR_URL}/api/v3/movie/{movie_id}"
                response = await client.put(put_url, headers=headers, json=movie_data)
                response.raise_for_status()
                
                updated_movie = response.json()
                title = updated_movie.get("title", "Unknown")
                
                result_msg = f"Successfully updated '{title}'"
                
                # Start search if requested
                if start_search:
                    search_url = f"{RADARR_URL}/api/v3/command"
                    search_command = {
                        "name": "MoviesSearch",
                        "movieIds": [movie_id]
                    }
                    search_response = await client.post(search_url, headers=headers, json=search_command)
                    search_response.raise_for_status()
                    result_msg += " and started search"
                
                return [TextContent(type="text", text=result_msg)]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error updating movie: {e}")]
        
        elif name == "delete_movie":
            movie_id = arguments.get("movie_id")
            delete_files = arguments.get("delete_files", False)
            
            try:
                # First get movie info for confirmation message
                get_url = f"{RADARR_URL}/api/v3/movie/{movie_id}"
                response = await client.get(get_url, headers=headers)
                response.raise_for_status()
                movie_data = response.json()
                title = movie_data.get("title", "Unknown")
                
                # Delete the movie
                delete_url = f"{RADARR_URL}/api/v3/movie/{movie_id}"
                params = {"deleteFiles": str(delete_files).lower()}
                response = await client.delete(delete_url, headers=headers, params=params)
                response.raise_for_status()
                
                result_msg = f"Successfully deleted '{title}' from Radarr"
                if delete_files:
                    result_msg += " (including files from disk)"
                
                return [TextContent(type="text", text=result_msg)]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error deleting movie: {e}")]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def run_server():
    """Run the MCP server."""
    global RADARR_URL, RADARR_API_KEY
    
    logger.debug(f"Starting Radarr MCP server for {RADARR_URL}")
    
    
    # Run the server using stdin/stdout streams
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="radarr-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

def main():
    """Main entry point for the server."""
    parser = argparse.ArgumentParser(description="Radarr MCP Server")
    parser.add_argument("--url", required=True, help="Radarr base URL (e.g., http://localhost:7878)")
    parser.add_argument("--api-token", required=True, help="Radarr API token")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Configure logging based on debug flag
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("httpx").setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)
        logging.getLogger("httpx").setLevel(logging.ERROR)
    
    global RADARR_URL, RADARR_API_KEY
    RADARR_URL = args.url.rstrip('/')  # Remove trailing slash if present
    RADARR_API_KEY = args.api_token
    
    asyncio.run(run_server())

if __name__ == "__main__":
    main()
