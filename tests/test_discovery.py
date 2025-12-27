import pytest
import json
from unittest.mock import patch, MagicMock
from arbitrage_os.discovery import ai_logic

@pytest.fixture
def mock_openai_client(mocker):
    """Fixture to mock the OpenAI client and its response."""
    mock_client_instance = MagicMock()
    mock_response = MagicMock()
    
    # The expected JSON output from the LLM
    expected_json_output = {
        "score": 9,
        "reasoning": "The listing mentions 'sterling' and 'heavy', indicating a high likelihood of valuable silver.",
        "address": "123 Silver St, Bullionville, USA",
        "weight_grams": 250.5,
        "purity": 0.925
    }
    
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(expected_json_output)
    
    mock_client_instance.chat.completions.create.return_value = mock_response
    
    # Patch the OpenAI class to return our mocked client instance
    return mocker.patch('arbitrage_os.discovery.ai_logic.OpenAI', return_value=mock_client_instance)

def test_analyze_description_positive_scenario(mock_openai_client, mocker):
    """
    Tests the analyze_description function with a positive scenario,
    ensuring it correctly parses the mocked LLM response.
    """
    # Arrange
    # Mock the environment variable
    mocker.patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    
    text_to_analyze = "This is a listing for a heavy sterling silver tea set. Pickup at 123 Silver St."

    # Act
    result = ai_logic.analyze_description(text_to_analyze)

    # Assert
    assert result['score'] == 9
    assert result['reasoning'] == "The listing mentions 'sterling' and 'heavy', indicating a high likelihood of valuable silver."
    assert result['address'] == "123 Silver St, Bullionville, USA"
    assert result['weight_grams'] == 250.5
    assert result['purity'] == 0.925

    # Verify that the OpenAI client was called correctly
    mock_openai_client().chat.completions.create.assert_called_once()
