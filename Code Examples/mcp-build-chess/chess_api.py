# Chess.com API wrapper for MCP server
# This file provides helper functions to interact with the Chess.com public API.
import requests

CHESS_API_BASE = "https://api.chess.com/pub"

def get_player_profile(username):
    url = f"{CHESS_API_BASE}/player/{username}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_player_stats(username):
    url = f"{CHESS_API_BASE}/player/{username}/stats"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_player_is_online(username):
    url = f"{CHESS_API_BASE}/player/{username}/is-online"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_player_current_games(username):
    url = f"{CHESS_API_BASE}/player/{username}/games"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
