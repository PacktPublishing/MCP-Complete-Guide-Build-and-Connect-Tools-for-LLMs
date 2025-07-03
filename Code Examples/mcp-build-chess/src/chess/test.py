from mcp.server.fastmcp import FastMCP

mcp = FastMCP('Chess.com')

from .chess_api import get_player_profile, get_player_stats

def test_get_player_profile():
    username = "hikaru"
    profile = get_player_profile(username)
    print("Profile:", profile)

def test_get_player_stats():
    username = "hikaru"
    stats = get_player_stats(username)
    print("Stats:", stats)

def main():
    test_get_player_profile()
    test_get_player_stats()
if __name__ == "__main__":
    main()