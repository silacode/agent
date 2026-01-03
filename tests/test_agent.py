"""Tests for the agent module - parse_response and run_agent functions."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.agent import parse_response, run_agent


class TestParseResponse:
    """Tests for parse_response function."""

    def test_valid_thought_and_action(self):
        """Test extraction of thought and action from valid response."""
        response = """Thought: I need to get the weather for Paris.
Action: {"tool_name": "get_weather", "arguments": {"lat": 48.85, "lon": 2.35}}"""

        thought, action, answer = parse_response(response)

        assert thought == "I need to get the weather for Paris."
        assert action == {
            "tool_name": "get_weather",
            "arguments": {"lat": 48.85, "lon": 2.35},
        }
        assert answer is None

    def test_valid_thought_and_answer(self):
        """Test extraction of thought and final answer."""
        response = """Thought: I have all the information needed.
Answer: The weather in Paris is sunny with a temperature of 20°C."""

        thought, action, answer = parse_response(response)

        assert thought == "I have all the information needed."
        assert action is None
        assert answer == "The weather in Paris is sunny with a temperature of 20°C."

    def test_multiline_thought(self):
        """Test extraction of multiline thought content."""
        response = """Thought: I need to do several things:
1. Get the weather
2. Search for news
3. Combine the results
Action: {"tool_name": "get_weather", "arguments": {"lat": 40.71, "lon": -74.00}}"""

        thought, action, answer = parse_response(response)

        assert thought is not None
        assert "I need to do several things:" in thought
        assert "1. Get the weather" in thought
        assert action == {
            "tool_name": "get_weather",
            "arguments": {"lat": 40.71, "lon": -74.00},
        }

    def test_multiline_answer(self):
        """Test extraction of multiline answer."""
        response = """Thought: I have gathered all the data.
Answer: Here are the results:
- Paris: Sunny, 20°C
- London: Cloudy, 15°C
- Tokyo: Rainy, 18°C"""

        thought, action, answer = parse_response(response)

        assert thought == "I have gathered all the data."
        assert action is None
        assert answer is not None
        assert "Here are the results:" in answer
        assert "Paris: Sunny" in answer

    def test_malformed_json_in_action(self):
        """Test that malformed JSON in action returns None for action."""
        response = """Thought: I need to search.
Action: {"tool_name": "web_search", "arguments": {invalid json here}}"""

        thought, action, answer = parse_response(response)

        assert thought == "I need to search."
        assert action is None  # Malformed JSON should result in None
        assert answer is None

    def test_missing_thought_section(self):
        """Test response with missing thought section."""
        response = """Action: {"tool_name": "get_weather", "arguments": {"lat": 48.85, "lon": 2.35}}"""

        thought, action, answer = parse_response(response)

        assert thought is None
        assert action == {
            "tool_name": "get_weather",
            "arguments": {"lat": 48.85, "lon": 2.35},
        }
        assert answer is None

    def test_empty_input(self):
        """Test with empty input string."""
        thought, action, answer = parse_response("")

        assert thought is None
        assert action is None
        assert answer is None

    def test_only_answer_no_thought(self):
        """Test response with only answer, no thought."""
        response = "Answer: The result is 42."

        thought, action, answer = parse_response(response)

        assert thought is None
        assert action is None
        assert answer == "The result is 42."

    def test_action_with_nested_json(self):
        """Test action with nested JSON arguments."""
        response = """Thought: Searching with complex query.
Action: {"tool_name": "web_search", "arguments": {"query": "test", "filters": {"date": "2024"}}}"""

        thought, action, answer = parse_response(response)

        assert thought == "Searching with complex query."
        assert action is not None
        assert action["tool_name"] == "web_search"
        assert action["arguments"]["query"] == "test"

    def test_whitespace_handling(self):
        """Test that extra whitespace is handled correctly."""
        response = """Thought:    I need weather data.   
Action: {"tool_name": "get_weather", "arguments": {"lat": 0, "lon": 0}}"""

        thought, action, answer = parse_response(response)

        assert thought == "I need weather data."
        assert action is not None

    def test_answer_takes_precedence_over_action(self):
        """Test that when both Action and Answer are present, Answer is returned."""
        response = """Thought: Final answer time.
Action: {"tool_name": "get_weather", "arguments": {"lat": 0, "lon": 0}}
Answer: Here is my final answer."""

        thought, action, answer = parse_response(response)

        # Answer should take precedence
        assert answer == "Here is my final answer."
        assert action is None  # Should be None when answer is present


class TestRunAgent:
    """Integration tests for run_agent with mocked OpenAI API."""

    async def test_single_turn_immediate_answer(self):
        """Test agent returns immediately when model gives direct answer."""
        mock_response = MagicMock()
        mock_response.output_text = """Thought: This is a simple question.
Answer: The answer is 42."""

        with patch("src.agent.AsyncOpenAI") as mock_openai_class:
            mock_client = AsyncMock()
            mock_client.responses.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            result = await run_agent("What is the meaning of life?")

            assert result == "The answer is 42."
            # Should only call the API once for immediate answer
            assert mock_client.responses.create.call_count == 1

    async def test_multi_turn_with_tool_call(self, mock_weather_response):
        """Test agent handles tool call then provides answer."""
        # First response: tool call
        first_response = MagicMock()
        first_response.output_text = """Thought: I need to get the weather for Paris.
Action: {"tool_name": "get_weather", "arguments": {"lat": 48.85, "lon": 2.35}}"""

        # Second response: final answer
        second_response = MagicMock()
        second_response.output_text = """Thought: I have the weather data.
Answer: The weather in Paris is clear with 20°C."""

        with patch("src.agent.AsyncOpenAI") as mock_openai_class:
            mock_client = AsyncMock()
            mock_client.responses.create.side_effect = [first_response, second_response]
            mock_openai_class.return_value = mock_client

            with patch("src.agent.handle_tool_call") as mock_tool:
                mock_tool.return_value = mock_weather_response

                result = await run_agent("What's the weather in Paris?")

                assert result == "The weather in Paris is clear with 20°C."
                # Should call API twice (tool call + answer)
                assert mock_client.responses.create.call_count == 2
                # Tool should be called once
                mock_tool.assert_called_once_with(
                    "get_weather", {"lat": 48.85, "lon": 2.35}
                )

    async def test_max_iterations_reached(self):
        """Test that agent stops after max iterations."""
        # Response that never provides an answer (infinite loop scenario)
        loop_response = MagicMock()
        loop_response.output_text = """Thought: I need more information.
Action: {"tool_name": "web_search", "arguments": {"query": "something"}}"""

        with patch("src.agent.AsyncOpenAI") as mock_openai_class:
            mock_client = AsyncMock()
            mock_client.responses.create.return_value = loop_response
            mock_openai_class.return_value = mock_client

            with patch("src.agent.handle_tool_call") as mock_tool:
                mock_tool.return_value = {"results": []}

                result = await run_agent("Test query", max_iterations=3)

                assert (
                    result
                    == "Max iterations reached. Please try again with a simpler query."
                )
                # Should call API exactly max_iterations times
                assert mock_client.responses.create.call_count == 3

    async def test_tool_execution_error_handling(self):
        """Test that tool execution errors are handled gracefully."""
        # First response: tool call
        first_response = MagicMock()
        first_response.output_text = """Thought: I need to search.
Action: {"tool_name": "web_search", "arguments": {"query": "test"}}"""

        # Second response: answer after seeing error
        second_response = MagicMock()
        second_response.output_text = """Thought: The search failed, I'll provide what I know.
Answer: I couldn't search, but here's my best answer."""

        with patch("src.agent.AsyncOpenAI") as mock_openai_class:
            mock_client = AsyncMock()
            mock_client.responses.create.side_effect = [first_response, second_response]
            mock_openai_class.return_value = mock_client

            with patch("src.agent.handle_tool_call") as mock_tool:
                mock_tool.side_effect = Exception("API rate limit exceeded")

                result = await run_agent("Search for something")

                assert result == "I couldn't search, but here's my best answer."

    async def test_no_tool_name_in_action(self):
        """Test handling when action has no tool_name."""
        response = MagicMock()
        response.output_text = """Thought: I need to do something.
Action: {"arguments": {"query": "test"}}"""

        with patch("src.agent.AsyncOpenAI") as mock_openai_class:
            mock_client = AsyncMock()
            mock_client.responses.create.return_value = response
            mock_openai_class.return_value = mock_client

            result = await run_agent("Do something")

            assert result == "Error: No tool name specified in action."

    async def test_nudges_model_when_no_action_or_answer(self):
        """Test that agent nudges model to continue when response is incomplete."""
        # First response: incomplete (no action, no answer)
        incomplete_response = MagicMock()
        incomplete_response.output_text = """Thought: I'm thinking about this..."""

        # Second response: complete answer
        complete_response = MagicMock()
        complete_response.output_text = """Thought: Now I know the answer.
Answer: Here is the complete answer."""

        with patch("src.agent.AsyncOpenAI") as mock_openai_class:
            mock_client = AsyncMock()
            mock_client.responses.create.side_effect = [
                incomplete_response,
                complete_response,
            ]
            mock_openai_class.return_value = mock_client

            result = await run_agent("Ask something")

            assert result == "Here is the complete answer."
            assert mock_client.responses.create.call_count == 2
