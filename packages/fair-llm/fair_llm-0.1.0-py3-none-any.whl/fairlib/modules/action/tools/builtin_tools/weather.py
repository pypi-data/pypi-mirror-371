# action/tools/builtin_tools/weather.py
"""
This module provides a built-in, simulated tool for fetching weather information.
"""
import re
from typing import Any

# The AbstractTool class defines the required interface for all tools.
from fairlib.core.interfaces.tools import AbstractTool


class WeatherTool(AbstractTool):
    """
    A simulated tool that provides a fake weather forecast for a given city.

    This tool demonstrates how to create a simple, regex-based tool. It does not
    make a real API call but instead returns a hardcoded weather string. It is
    designed to parse a city name from a natural language query.
    """
    # The 'name' attribute is a unique identifier for the tool that the planner uses.
    name: str = "weather"
    # The 'description' helps the planner understand what the tool does and when to use it.
    description: str = "Provides a simulated weather forecast for a given city. Use this to find the weather."

    def use(self, query: str) -> str:
        """
        Executes the weather tool's logic.

        This method attempts to parse a city name from the input query and
        returns a fixed, simulated weather forecast for that city.

        Args:
            query: The full natural language query from the user, e.g.,
                   "what is the weather like in London?".

        Returns:
            A string containing the simulated weather information.
        """
        # This regular expression looks for a city name following "in" or "at".
        # - (?:in|at): A non-capturing group to match either "in" or "at".
        # - \s+: Matches one or more whitespace characters.
        # - ([A-Z][a-zA-Z\s]+): A capturing group for the city name, which must
        #   start with a capital letter.
        match = re.search(r"(?:in|at)\s+([A-Z][a-zA-Z\s]+)", query)

        # If a city is found in the query, use it. Otherwise, default to a generic placeholder.
        city = match.group(1).strip() if match else "your city"

        # This is a hardcoded response for simulation purposes.
        # A real implementation would make an API call to a weather service here.
        return f"The weather in {city} is currently 22°C with scattered clouds."