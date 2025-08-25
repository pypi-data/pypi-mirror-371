import argparse
import asyncio
import logging
from typing import Any

import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent

logger = logging.getLogger("sonarr-mcp")

server = Server("sonarr-mcp")

# Configuration - will be set from command line args
SONARR_URL = ""
SONARR_API_KEY = ""


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available Sonarr tools."""
    return [
        Tool(
            name="search_series",
            description="Search for TV series in Sonarr",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "TV series title to search for"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="add_series",
            description="Add a TV series to Sonarr",
            inputSchema={
                "type": "object", 
                "properties": {
                    "tvdb_id": {
                        "type": "integer",
                        "description": "TVDB ID of the series"
                    },
                    "quality_profile_id": {
                        "type": "integer",
                        "description": "Quality profile ID (use get_quality_profiles to see available options)"
                    },
                    "root_folder_path": {
                        "type": "string",
                        "description": "Root folder path for the series",
                        "default": "/tv"
                    },
                    "season_folder": {
                        "type": "boolean",
                        "description": "Whether to use season folders",
                        "default": True
                    },
                    "monitor_type": {
                        "type": "string",
                        "description": "Which episodes to monitor: 'all' (all episodes), 'future' (future episodes only), 'missing' (missing episodes), 'existing' (existing episodes), 'recent' (recent episodes), 'first' (first season), 'latest' (latest season), 'none' (no episodes), 'season_specific' (monitor specific seasons only - requires monitor_seasons)",
                        "enum": ["all", "future", "missing", "existing", "recent", "first", "latest", "none", "season_specific"]
                    },
                    "monitor_seasons": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Specific season numbers to monitor (only used with monitor_type: 'season_specific'). Example: [1, 3, 5]"
                    },
                    "search_for_missing_episodes": {
                        "type": "boolean",
                        "description": "Whether to automatically search for missing episodes after adding",
                        "default": False
                    }
                },
                "required": ["tvdb_id", "quality_profile_id", "monitor_type"]
            }
        ),
        Tool(
            name="list_series",
            description="Get all TV series from Sonarr",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_series",
            description="Get detailed information about a specific TV series",
            inputSchema={
                "type": "object",
                "properties": {
                    "series_id": {
                        "type": "integer",
                        "description": "Sonarr series ID (use the ID from list_series output)"
                    }
                },
                "required": ["series_id"]
            }
        ),
        Tool(
            name="get_quality_profiles",
            description="Get all quality profiles from Sonarr",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="interactive_search",
            description="Search for available releases for a TV series episode",
            inputSchema={
                "type": "object",
                "properties": {
                    "series_id": {
                        "type": "integer",
                        "description": "Sonarr series ID (use the ID from list_series output)"
                    },
                    "season_number": {
                        "type": "integer",
                        "description": "Season number (optional, searches all seasons if not provided)"
                    },
                    "episode_number": {
                        "type": "integer",
                        "description": "Episode number (optional, searches all episodes if not provided)"
                    }
                },
                "required": ["series_id"]
            }
        ),
        Tool(
            name="update_series",
            description="Update series settings (quality profile, monitoring, search)",
            inputSchema={
                "type": "object",
                "properties": {
                    "series_id": {
                        "type": "integer",
                        "description": "Sonarr series ID (use the ID from list_series output)"
                    },
                    "quality_profile_id": {
                        "type": "integer",
                        "description": "New quality profile ID (optional, use get_quality_profiles to see options)"
                    },
                    "monitor_type": {
                        "type": "string",
                        "description": "Which episodes to monitor: 'all', 'future', 'missing', 'existing', 'recent', 'first', 'latest', 'none'",
                        "enum": ["all", "future", "missing", "existing", "recent", "first", "latest", "none"]
                    },
                    "monitor_seasons": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Specific season numbers to monitor (overrides monitor_type if provided). Example: [1, 3, 5]"
                    },
                    "start_search": {
                        "type": "boolean",
                        "description": "Whether to search for missing episodes in monitored seasons after update",
                        "default": False
                    }
                },
                "required": ["series_id"]
            }
        ),
        Tool(
            name="delete_series",
            description="Delete a TV series or specific seasons from Sonarr",
            inputSchema={
                "type": "object",
                "properties": {
                    "series_id": {
                        "type": "integer",
                        "description": "Sonarr series ID (use the ID from list_series output)"
                    },
                    "delete_seasons": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Specific season numbers to delete (if not provided, deletes entire series). Example: [2, 4]"
                    },
                    "delete_files": {
                        "type": "boolean",
                        "description": "Whether to delete files from disk (applies to entire series or specific seasons)",
                        "default": False
                    }
                },
                "required": ["series_id"]
            }
        ),
        Tool(
            name="download_release",
            description="Download a specific release for an episode",
            inputSchema={
                "type": "object",
                "properties": {
                    "release_guid": {
                        "type": "string",
                        "description": "Release GUID from interactive_search results"
                    },
                    "series_id": {
                        "type": "integer",
                        "description": "Sonarr series ID"
                    }
                },
                "required": ["release_guid", "series_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """Handle tool calls."""
    if not SONARR_URL or not SONARR_API_KEY:
        return [TextContent(type="text", text="Error: Sonarr URL and API key must be configured")]
    
    if arguments is None:
        arguments = {}
    
    async with httpx.AsyncClient() as client:
        headers = {"X-Api-Key": SONARR_API_KEY}
        
        if name == "search_series":
            query = arguments.get("query", "")
            url = f"{SONARR_URL}/api/v3/series/lookup"
            params = {"term": query}
            
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                series_list = response.json()
                
                if not series_list:
                    return [TextContent(type="text", text=f"No TV series found for '{query}'")]
                
                result = "Found TV series:\n"
                for series in series_list[:5]:  # Limit to first 5 results
                    title = series.get("title", "Unknown")
                    year = series.get("year", "Unknown")
                    tvdb_id = series.get("tvdbId", "Unknown")
                    overview = series.get("overview", "No overview available")[:100] + "..."
                    result += f"\n• {title} ({year}) [TVDB: {tvdb_id}]\n  {overview}\n"
                
                return [TextContent(type="text", text=result)]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error searching TV series: {e}")]
        
        elif name == "list_series":
            url = f"{SONARR_URL}/api/v3/series"
            
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                series_list = response.json()
                
                if not series_list:
                    return [TextContent(type="text", text="No TV series in Sonarr library")]
                
                result = f"Sonarr library ({len(series_list)} TV series):\n"
                for series in series_list:
                    title = series.get("title", "Unknown")
                    year = series.get("year", "Unknown")
                    series_id = series.get("id", "Unknown")
                    # For TV series, we check episode statistics instead of hasFile
                    statistics = series.get("statistics", {})
                    episode_file_count = statistics.get("episodeFileCount", 0)
                    episode_count = statistics.get("episodeCount", 0)
                    status = f"{episode_file_count}/{episode_count} episodes"
                    result += f"• ID {series_id} - {title} ({year}) - {status}\n"
                
                return [TextContent(type="text", text=result)]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error getting TV series: {e}")]
        
        elif name == "get_series":
            series_id = arguments.get("series_id")
            
            try:
                # Get series details
                series_url = f"{SONARR_URL}/api/v3/series/{series_id}"
                response = await client.get(series_url, headers=headers)
                response.raise_for_status()
                series = response.json()
                
                # Get quality profile name
                quality_profile_id = series.get("qualityProfileId")
                quality_profiles_url = f"{SONARR_URL}/api/v3/qualityprofile"
                profiles_response = await client.get(quality_profiles_url, headers=headers)
                profiles_response.raise_for_status()
                profiles = profiles_response.json()
                quality_profile_name = "Unknown"
                for profile in profiles:
                    if profile.get("id") == quality_profile_id:
                        quality_profile_name = profile.get("name", "Unknown")
                        break
                
                # Check for active downloads/queue items
                queue_url = f"{SONARR_URL}/api/v3/queue"
                queue_response = await client.get(queue_url, headers=headers)
                queue_response.raise_for_status()
                queue_items = queue_response.json().get("records", [])
                
                # Find any downloads for this series
                active_downloads = []
                for item in queue_items:
                    if item.get("seriesId") == series_id:
                        active_downloads.append({
                            "episode": item.get("episode", {}).get("title", "Unknown Episode"),
                            "status": item.get("status", "Unknown"),
                            "progress": item.get("sizeleft", 0),
                            "total_size": item.get("size", 0),
                            "eta": item.get("timeleft", "Unknown")
                        })
                
                # Build detailed result
                title = series.get("title", "Unknown")
                year = series.get("year", "Unknown")
                overview = series.get("overview", "No overview available")
                status = series.get("status", "Unknown")
                monitored = series.get("monitored", False)
                
                # Episode statistics
                statistics = series.get("statistics", {})
                episode_file_count = statistics.get("episodeFileCount", 0)
                episode_count = statistics.get("episodeCount", 0)
                total_episode_count = statistics.get("totalEpisodeCount", 0)
                size_on_disk = statistics.get("sizeOnDisk", 0)
                size_gb = round(size_on_disk / (1024**3), 2) if size_on_disk else 0
                
                # External IDs
                tvdb_id = series.get("tvdbId", "Unknown")
                imdb_id = series.get("imdbId", "Unknown")
                
                result = f"📺 {title} ({year})\n"
                result += f"ID: {series_id} | TVDB: {tvdb_id} | IMDb: {imdb_id}\n"
                result += f"Status: {status} | Monitored: {'Yes' if monitored else 'No'}\n"
                result += f"Quality Profile: {quality_profile_name} (ID: {quality_profile_id})\n"
                result += f"Episodes: {episode_file_count}/{episode_count} downloaded"
                if total_episode_count != episode_count:
                    result += f" ({total_episode_count} total)\n"
                else:
                    result += "\n"
                result += f"Size on disk: {size_gb} GB\n\n"
                
                if active_downloads:
                    result += "⬇️ Active Downloads:\n"
                    for download in active_downloads:
                        progress_percent = 0
                        if download["total_size"] > 0:
                            progress_percent = round(((download["total_size"] - download["progress"]) / download["total_size"]) * 100, 1)
                        result += f"   • {download['episode']}\n"
                        result += f"     Status: {download['status']} | Progress: {progress_percent}% | ETA: {download['eta']}\n"
                    result += "\n"
                
                result += f"📝 Overview:\n{overview}"
                
                return [TextContent(type="text", text=result)]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error getting series details: {e}")]
        
        elif name == "add_series":
            tvdb_id = arguments.get("tvdb_id")
            quality_profile_id = arguments.get("quality_profile_id")
            root_folder_path = arguments.get("root_folder_path", "/tv")
            season_folder = arguments.get("season_folder", True)
            monitor_type = arguments.get("monitor_type")  # Now required, no default
            monitor_seasons = arguments.get("monitor_seasons")
            search_for_missing_episodes = arguments.get("search_for_missing_episodes", False)
            
            # Validation rules
            if monitor_type == "season_specific":
                if not monitor_seasons:
                    return [TextContent(type="text", text="Error: monitor_seasons array required when monitor_type is 'season_specific'")]
            else:
                if monitor_seasons:
                    return [TextContent(type="text", text="Error: monitor_seasons can only be used with monitor_type: 'season_specific'")]
            
            # First lookup the series details
            lookup_url = f"{SONARR_URL}/api/v3/series/lookup"
            params = {"term": f"tvdb:{tvdb_id}"}
            
            try:
                response = await client.get(lookup_url, headers=headers, params=params)
                response.raise_for_status()
                lookup_results = response.json()
                
                if not lookup_results:
                    return [TextContent(type="text", text=f"No series found with TVDB ID {tvdb_id}")]
                
                series_data = lookup_results[0]  # Take the first result
                
                # Handle season monitoring
                if monitor_type == "season_specific":
                    # Set specific seasons to monitor (monitor_seasons is guaranteed to exist due to validation)
                    for season in series_data.get("seasons", []):
                        season["monitored"] = season.get("seasonNumber") in monitor_seasons
                elif monitor_type == "first":
                    # Monitor only first season
                    for season in series_data.get("seasons", []):
                        season["monitored"] = season.get("seasonNumber") == 1
                elif monitor_type == "latest":
                    # Monitor only latest season
                    seasons = series_data.get("seasons", [])
                    if seasons:
                        latest_season_num = max(s.get("seasonNumber", 0) for s in seasons if s.get("seasonNumber", 0) > 0)
                        for season in seasons:
                            season["monitored"] = season.get("seasonNumber") == latest_season_num
                elif monitor_type == "none":
                    # Monitor no seasons
                    for season in series_data.get("seasons", []):
                        season["monitored"] = False
                else:
                    # Monitor all seasons for other types (all, future, missing, existing, recent)
                    for season in series_data.get("seasons", []):
                        season["monitored"] = True
                
                # Prepare series for adding
                series_data.update({
                    "qualityProfileId": quality_profile_id,
                    "rootFolderPath": root_folder_path,
                    "seasonFolder": season_folder,
                    "monitored": True,
                    "addOptions": {
                        "searchForMissingEpisodes": search_for_missing_episodes,
                        "monitor": "none" if monitor_type == "season_specific" else monitor_type
                    }
                })
                
                # Add the series
                add_url = f"{SONARR_URL}/api/v3/series"
                response = await client.post(add_url, headers=headers, json=series_data)
                response.raise_for_status()
                
                added_series = response.json()
                title = added_series.get("title", "Unknown")
                year = added_series.get("year", "Unknown")
                series_id = added_series.get("id")
                
                # If using season_specific monitoring, update the series after a brief delay
                if monitor_type == "season_specific" and series_id:
                    # Wait for Sonarr to fully process the series and populate seasons
                    await asyncio.sleep(2)
                    
                    # Get the added series data to ensure we have the correct season structure
                    get_url = f"{SONARR_URL}/api/v3/series/{series_id}"
                    get_response = await client.get(get_url, headers=headers)
                    get_response.raise_for_status()
                    current_series_data = get_response.json()
                    
                    # Set season monitoring on the actual series data from Sonarr
                    for season in current_series_data.get("seasons", []):
                        season["monitored"] = season.get("seasonNumber") in monitor_seasons
                    
                    # Update the series with correct season monitoring
                    put_url = f"{SONARR_URL}/api/v3/series/{series_id}"
                    put_response = await client.put(put_url, headers=headers, json=current_series_data)
                    put_response.raise_for_status()
                
                monitor_msg = ""
                if monitor_type == "season_specific":
                    monitor_msg = f" (monitoring seasons: {', '.join(map(str, monitor_seasons))})"
                else:
                    monitor_msg = f" (monitor type: {monitor_type})"
                
                return [TextContent(type="text", text=f"Successfully added '{title} ({year})' to Sonarr{monitor_msg}")]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error adding series: {e}")]
        
        elif name == "get_quality_profiles":
            url = f"{SONARR_URL}/api/v3/qualityprofile"
            
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
            series_id = arguments.get("series_id")
            season_number = arguments.get("season_number")
            episode_number = arguments.get("episode_number")
            
            try:
                # If we have specific season/episode, search for that episode
                if season_number is not None and episode_number is not None:
                    # Get episode ID first
                    episodes_url = f"{SONARR_URL}/api/v3/episode"
                    episodes_params = {"seriesId": series_id}
                    episodes_response = await client.get(episodes_url, headers=headers, params=episodes_params)
                    episodes_response.raise_for_status()
                    episodes = episodes_response.json()
                    
                    target_episode = None
                    for episode in episodes:
                        if episode.get("seasonNumber") == season_number and episode.get("episodeNumber") == episode_number:
                            target_episode = episode
                            break
                    
                    if not target_episode:
                        return [TextContent(type="text", text=f"Episode S{season_number:02d}E{episode_number:02d} not found for series ID {series_id}")]
                    
                    url = f"{SONARR_URL}/api/v3/release"
                    params = {"episodeId": target_episode["id"]}
                    search_description = f"episode S{season_number:02d}E{episode_number:02d}"
                else:
                    # Search for all missing episodes in the series
                    url = f"{SONARR_URL}/api/v3/release"
                    params = {"seriesId": series_id}
                    search_description = f"series ID {series_id}"
                
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                releases = response.json()
                
                if not releases:
                    return [TextContent(type="text", text=f"No releases found for {search_description}")]
                
                # Sort by seeders (highest first), treating None/missing as 0
                releases.sort(key=lambda x: x.get("seeders", 0) or 0, reverse=True)
                
                result = f"Available releases for {search_description} (sorted by seeders):\n\n"
                
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
                    
                    # Release identification
                    guid = release.get("guid", "Unknown")
                    
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
                    
                    # Add GUID for download_release tool
                    result += f"   Release ID: {guid}\n"
                    
                    result += "\n"
                
                if len(releases) > 20:
                    result += f"... and {len(releases) - 20} more releases available"
                
                return [TextContent(type="text", text=result)]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error searching releases: {e}")]
        
        elif name == "update_series":
            series_id = arguments.get("series_id")
            quality_profile_id = arguments.get("quality_profile_id")
            monitor_type = arguments.get("monitor_type")
            monitor_seasons = arguments.get("monitor_seasons")
            start_search = arguments.get("start_search", False)
            
            try:
                # First get the current series data
                get_url = f"{SONARR_URL}/api/v3/series/{series_id}"
                response = await client.get(get_url, headers=headers)
                response.raise_for_status()
                series_data = response.json()
                
                # Update quality profile if provided
                if quality_profile_id:
                    series_data["qualityProfileId"] = quality_profile_id
                
                # Update monitoring if provided
                if monitor_seasons:
                    # Set specific seasons to monitor
                    for season in series_data.get("seasons", []):
                        season["monitored"] = season.get("seasonNumber") in monitor_seasons
                elif monitor_type:
                    # Use monitor_type for all seasons
                    if monitor_type == "first":
                        # Monitor only first season
                        for season in series_data.get("seasons", []):
                            season["monitored"] = season.get("seasonNumber") == 1
                    elif monitor_type == "latest":
                        # Monitor only latest season
                        seasons = series_data.get("seasons", [])
                        if seasons:
                            latest_season_num = max(s.get("seasonNumber", 0) for s in seasons if s.get("seasonNumber", 0) > 0)
                            for season in seasons:
                                season["monitored"] = season.get("seasonNumber") == latest_season_num
                    elif monitor_type == "none":
                        # Monitor no seasons
                        for season in series_data.get("seasons", []):
                            season["monitored"] = False
                    else:
                        # Monitor all seasons for other types (all, future, missing, existing, recent)
                        for season in series_data.get("seasons", []):
                            season["monitored"] = True
                
                # Update the series
                put_url = f"{SONARR_URL}/api/v3/series/{series_id}"
                response = await client.put(put_url, headers=headers, json=series_data)
                response.raise_for_status()
                
                updated_series = response.json()
                title = updated_series.get("title", "Unknown")
                
                result_msg = f"Successfully updated '{title}'"
                
                # Add monitoring info to result
                if monitor_seasons:
                    result_msg += f" (now monitoring seasons: {', '.join(map(str, monitor_seasons))})"
                elif monitor_type:
                    result_msg += f" (monitor type: {monitor_type})"
                
                # Start search if requested
                if start_search:
                    search_url = f"{SONARR_URL}/api/v3/command"
                    search_command = {
                        "name": "SeriesSearch",
                        "seriesId": series_id
                    }
                    search_response = await client.post(search_url, headers=headers, json=search_command)
                    search_response.raise_for_status()
                    result_msg += " and started search for missing episodes in monitored seasons"
                
                return [TextContent(type="text", text=result_msg)]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error updating series: {e}")]
        
        elif name == "delete_series":
            series_id = arguments.get("series_id")
            delete_seasons = arguments.get("delete_seasons")
            delete_files = arguments.get("delete_files", False)
            
            try:
                # First get series info for confirmation message
                get_url = f"{SONARR_URL}/api/v3/series/{series_id}"
                response = await client.get(get_url, headers=headers)
                response.raise_for_status()
                series_data = response.json()
                title = series_data.get("title", "Unknown")
                
                if delete_seasons:
                    # Delete specific seasons by unmonitoring them and optionally deleting files
                    for season in series_data.get("seasons", []):
                        if season.get("seasonNumber") in delete_seasons:
                            season["monitored"] = False
                    
                    # Update the series with unmonitored seasons
                    put_url = f"{SONARR_URL}/api/v3/series/{series_id}"
                    response = await client.put(put_url, headers=headers, json=series_data)
                    response.raise_for_status()
                    
                    result_msg = f"Successfully unmonitored seasons {', '.join(map(str, delete_seasons))} for '{title}'"
                    
                    # If delete_files is True, delete episode files for those seasons
                    if delete_files:
                        episodes_url = f"{SONARR_URL}/api/v3/episode"
                        episodes_params = {"seriesId": series_id}
                        episodes_response = await client.get(episodes_url, headers=headers, params=episodes_params)
                        episodes_response.raise_for_status()
                        episodes = episodes_response.json()
                        
                        # Find episode files for the seasons to delete
                        episode_file_ids = []
                        for episode in episodes:
                            if (episode.get("seasonNumber") in delete_seasons and 
                                episode.get("hasFile", False) and 
                                episode.get("episodeFileId")):
                                episode_file_ids.append(episode["episodeFileId"])
                        
                        # Delete the episode files
                        if episode_file_ids:
                            for file_id in set(episode_file_ids):  # Remove duplicates
                                file_delete_url = f"{SONARR_URL}/api/v3/episodefile/{file_id}"
                                await client.delete(file_delete_url, headers=headers)
                            
                            result_msg += f" and deleted {len(set(episode_file_ids))} episode files from disk"
                    
                else:
                    # Delete the entire series
                    delete_url = f"{SONARR_URL}/api/v3/series/{series_id}"
                    params = {"deleteFiles": str(delete_files).lower()}
                    response = await client.delete(delete_url, headers=headers, params=params)
                    response.raise_for_status()
                    
                    result_msg = f"Successfully deleted '{title}' from Sonarr"
                    if delete_files:
                        result_msg += " (including files from disk)"
                
                return [TextContent(type="text", text=result_msg)]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error deleting series/seasons: {e}")]
        
        elif name == "download_torrent":
            release_guid = arguments.get("release_guid")
            movie_id = arguments.get("movie_id")
            
            try:
                # First, get the original release data by searching again
                search_url = f"{SONARR_URL}/api/v3/release"
                search_params = {"movieId": movie_id}
                search_response = await client.get(search_url, headers=headers, params=search_params)
                search_response.raise_for_status()
                releases = search_response.json()
                
                # Find the specific release by GUID
                target_release = None
                for release in releases:
                    if release.get("guid") == release_guid:
                        target_release = release
                        break
                
                if not target_release:
                    return [TextContent(type="text", text=f"Release with GUID {release_guid} not found")]
                
                # Send the complete release data to download
                download_url = f"{SONARR_URL}/api/v3/release"
                response = await client.post(download_url, headers=headers, json=target_release)
                response.raise_for_status()
                
                # Get movie title for response
                movie_url = f"{SONARR_URL}/api/v3/movie/{movie_id}"
                movie_response = await client.get(movie_url, headers=headers)
                movie_response.raise_for_status()
                movie_data = movie_response.json()
                movie_title = movie_data.get("title", "Unknown")
                
                return [TextContent(type="text", text=f"Successfully started download for '{movie_title}' (Release ID: {release_guid})")]
                
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=f"Error downloading torrent: {e}")]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def run_server():
    """Run the MCP server."""
    global SONARR_URL, SONARR_API_KEY
    
    logger.debug(f"Starting Sonarr MCP server for {SONARR_URL}")
    
    
    # Run the server using stdin/stdout streams
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sonarr-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

def main():
    """Main entry point for the server."""
    parser = argparse.ArgumentParser(description="Sonarr MCP Server")
    parser.add_argument("--url", required=True, help="Sonarr base URL (e.g., http://localhost:8989)")
    parser.add_argument("--api-token", required=True, help="Sonarr API token")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Configure logging based on debug flag
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("httpx").setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)
        logging.getLogger("httpx").setLevel(logging.ERROR)
    
    global SONARR_URL, SONARR_API_KEY
    SONARR_URL = args.url.rstrip('/')  # Remove trailing slash if present
    SONARR_API_KEY = args.api_token
    
    asyncio.run(run_server())

if __name__ == "__main__":
    main()
