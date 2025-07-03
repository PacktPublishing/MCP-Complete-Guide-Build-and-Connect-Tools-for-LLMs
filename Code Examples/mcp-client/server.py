from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
def get_weather(location: str) -> str:
    """
    Gets the weather given a location
    Args:
        location: location, can be city, country, state, etc.
    """
    return f"The weather in {location} is hot and dry"

@mcp.resource("weather://statement")
def get_weather_statement() -> str:
    """
    Returns the weather statement
    """
    return "This is an example weather statement"

@mcp.resource("weather://{city}/statement")
def get_weather_statement_from_city(city: str) -> str:
    """
    Returns the weather statement based on a particular city
    """
    return f"No special statements for this city: {city}"

@mcp.prompt()
def get_prompt(topic: str) -> str:
    """
    Returns a prompt related to asking for more information on weather concepts about {topic}
    Args:
        topic: the topic to do research on
    """
    return f"Describe the weather concept of {topic}"



if __name__ == "__main__":
    mcp.run()