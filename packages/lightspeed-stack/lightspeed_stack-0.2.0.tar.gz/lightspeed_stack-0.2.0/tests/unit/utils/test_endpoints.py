"""Unit tests for endpoints utility functions."""

import os
import pytest
from fastapi import HTTPException

import constants
from configuration import AppConfig
from tests.unit import config_dict

from models.requests import QueryRequest
from utils import endpoints
from utils.endpoints import get_agent

CONFIGURED_SYSTEM_PROMPT = "This is a configured system prompt"


@pytest.fixture(name="input_file")
def input_file_fixture(tmp_path):
    """Create file manually using the tmp_path fixture."""
    filename = os.path.join(tmp_path, "prompt.txt")
    with open(filename, "wt", encoding="utf-8") as fout:
        fout.write("this is prompt!")
    return filename


@pytest.fixture(name="config_without_system_prompt")
def config_without_system_prompt_fixture():
    """Configuration w/o custom system prompt set."""
    test_config = config_dict.copy()

    # no customization provided
    test_config["customization"] = None

    cfg = AppConfig()
    cfg.init_from_dict(test_config)

    return cfg


@pytest.fixture(name="config_with_custom_system_prompt")
def config_with_custom_system_prompt_fixture():
    """Configuration with custom system prompt set."""
    test_config = config_dict.copy()

    # system prompt is customized
    test_config["customization"] = {
        "system_prompt": CONFIGURED_SYSTEM_PROMPT,
    }
    cfg = AppConfig()
    cfg.init_from_dict(test_config)

    return cfg


@pytest.fixture(name="config_with_custom_system_prompt_and_disable_query_system_prompt")
def config_with_custom_system_prompt_and_disable_query_system_prompt_fixture():
    """Configuration with custom system prompt and disabled query system prompt set."""
    test_config = config_dict.copy()

    # system prompt is customized and query system prompt is disabled
    test_config["customization"] = {
        "system_prompt": CONFIGURED_SYSTEM_PROMPT,
        "disable_query_system_prompt": True,
    }
    cfg = AppConfig()
    cfg.init_from_dict(test_config)

    return cfg


@pytest.fixture(name="query_request_without_system_prompt")
def query_request_without_system_prompt_fixture():
    """Fixture for query request without system prompt."""
    return QueryRequest(query="query", system_prompt=None)


@pytest.fixture(name="query_request_with_system_prompt")
def query_request_with_system_prompt_fixture():
    """Fixture for query request with system prompt."""
    return QueryRequest(query="query", system_prompt="System prompt defined in query")


@pytest.fixture(name="setup_configuration")
def setup_configuration_fixture():
    """Set up configuration for tests."""
    test_config_dict = {
        "name": "test",
        "service": {
            "host": "localhost",
            "port": 8080,
            "auth_enabled": False,
            "workers": 1,
            "color_log": True,
            "access_log": True,
        },
        "llama_stack": {
            "api_key": "test-key",
            "url": "http://test.com:1234",
            "use_as_library_client": False,
        },
        "user_data_collection": {
            "transcripts_enabled": False,
        },
        "mcp_servers": [],
    }
    cfg = AppConfig()
    cfg.init_from_dict(test_config_dict)
    return cfg


def test_get_default_system_prompt(
    config_without_system_prompt, query_request_without_system_prompt
):
    """Test that default system prompt is returned when other prompts are not provided."""
    system_prompt = endpoints.get_system_prompt(
        query_request_without_system_prompt, config_without_system_prompt
    )
    assert system_prompt == constants.DEFAULT_SYSTEM_PROMPT


def test_get_customized_system_prompt(
    config_with_custom_system_prompt, query_request_without_system_prompt
):
    """Test that customized system prompt is used when system prompt is not provided in query."""
    system_prompt = endpoints.get_system_prompt(
        query_request_without_system_prompt, config_with_custom_system_prompt
    )
    assert system_prompt == CONFIGURED_SYSTEM_PROMPT


def test_get_query_system_prompt(
    config_without_system_prompt, query_request_with_system_prompt
):
    """Test that system prompt from query is returned."""
    system_prompt = endpoints.get_system_prompt(
        query_request_with_system_prompt, config_without_system_prompt
    )
    assert system_prompt == query_request_with_system_prompt.system_prompt


def test_get_query_system_prompt_not_customized_one(
    config_with_custom_system_prompt, query_request_with_system_prompt
):
    """Test that system prompt from query is returned even when customized one is specified."""
    system_prompt = endpoints.get_system_prompt(
        query_request_with_system_prompt, config_with_custom_system_prompt
    )
    assert system_prompt == query_request_with_system_prompt.system_prompt


def test_get_system_prompt_with_disable_query_system_prompt(
    config_with_custom_system_prompt_and_disable_query_system_prompt,
    query_request_with_system_prompt,
):
    """Test that query system prompt is disallowed when disable_query_system_prompt is True."""
    with pytest.raises(HTTPException) as exc_info:
        endpoints.get_system_prompt(
            query_request_with_system_prompt,
            config_with_custom_system_prompt_and_disable_query_system_prompt,
        )
    assert exc_info.value.status_code == 422


def test_get_system_prompt_with_disable_query_system_prompt_and_non_system_prompt_query(
    config_with_custom_system_prompt_and_disable_query_system_prompt,
    query_request_without_system_prompt,
):
    """Test that query without system prompt is allowed when disable_query_system_prompt is True."""
    system_prompt = endpoints.get_system_prompt(
        query_request_without_system_prompt,
        config_with_custom_system_prompt_and_disable_query_system_prompt,
    )
    assert system_prompt == CONFIGURED_SYSTEM_PROMPT


@pytest.mark.asyncio
async def test_get_agent_with_conversation_id(prepare_agent_mocks, mocker):
    """Test get_agent function when agent exists in llama stack."""
    mock_client, mock_agent = prepare_agent_mocks
    conversation_id = "test_conversation_id"

    # Mock existing agent retrieval
    mock_agent_response = mocker.Mock()
    mock_agent_response.agent_id = conversation_id
    mock_client.agents.retrieve.return_value = mock_agent_response

    mock_client.agents.session.list.return_value = mocker.Mock(
        data=[{"session_id": "test_session_id"}]
    )

    # Mock Agent class
    mocker.patch("utils.endpoints.AsyncAgent", return_value=mock_agent)

    result_agent, result_conversation_id, result_session_id = await get_agent(
        client=mock_client,
        model_id="test_model",
        system_prompt="test_prompt",
        available_input_shields=["shield1"],
        available_output_shields=["output_shield2"],
        conversation_id=conversation_id,
    )

    # Assert the same agent is returned and conversation_id is preserved
    assert result_agent == mock_agent
    assert result_conversation_id == conversation_id
    assert result_session_id == "test_session_id"


@pytest.mark.asyncio
async def test_get_agent_with_conversation_id_and_no_agent_in_llama_stack(
    setup_configuration, prepare_agent_mocks, mocker
):
    """Test get_agent function when conversation_id is provided."""
    mock_client, mock_agent = prepare_agent_mocks
    mock_client.agents.retrieve.side_effect = ValueError(
        "fake not finding existing agent"
    )
    mock_agent.create_session.return_value = "new_session_id"

    # Mock Agent class
    mock_agent_class = mocker.patch(
        "utils.endpoints.AsyncAgent", return_value=mock_agent
    )

    # Mock get_suid
    mocker.patch("utils.endpoints.get_suid", return_value="new_session_id")

    # Mock configuration
    mock_mcp_server = mocker.Mock()
    mock_mcp_server.name = "mcp_server_1"
    mocker.patch.object(
        type(setup_configuration),
        "mcp_servers",
        new_callable=mocker.PropertyMock,
        return_value=[mock_mcp_server],
    )
    mocker.patch("configuration.configuration", setup_configuration)
    conversation_id = "non_existent_conversation_id"
    # Call function with conversation_id
    result_agent, result_conversation_id, result_session_id = await get_agent(
        client=mock_client,
        model_id="test_model",
        system_prompt="test_prompt",
        available_input_shields=["shield1"],
        available_output_shields=["output_shield2"],
        conversation_id=conversation_id,
    )

    # Assert new agent is created
    assert result_agent == mock_agent
    assert result_conversation_id == result_agent.agent_id
    assert conversation_id != result_agent.agent_id
    assert result_session_id == "new_session_id"

    # Verify Agent was created with correct parameters
    mock_agent_class.assert_called_once_with(
        mock_client,
        model="test_model",
        instructions="test_prompt",
        input_shields=["shield1"],
        output_shields=["output_shield2"],
        tool_parser=None,
        enable_session_persistence=True,
    )


@pytest.mark.asyncio
async def test_get_agent_no_conversation_id(
    setup_configuration, prepare_agent_mocks, mocker
):
    """Test get_agent function when conversation_id is None."""
    mock_client, mock_agent = prepare_agent_mocks
    mock_agent.create_session.return_value = "new_session_id"

    # Mock Agent class
    mock_agent_class = mocker.patch(
        "utils.endpoints.AsyncAgent", return_value=mock_agent
    )

    # Mock get_suid
    mocker.patch("utils.endpoints.get_suid", return_value="new_session_id")

    # Mock configuration
    mock_mcp_server = mocker.Mock()
    mock_mcp_server.name = "mcp_server_1"
    mocker.patch.object(
        type(setup_configuration),
        "mcp_servers",
        new_callable=mocker.PropertyMock,
        return_value=[mock_mcp_server],
    )
    mocker.patch("configuration.configuration", setup_configuration)

    # Call function with None conversation_id
    result_agent, result_conversation_id, result_session_id = await get_agent(
        client=mock_client,
        model_id="test_model",
        system_prompt="test_prompt",
        available_input_shields=["shield1"],
        available_output_shields=["output_shield2"],
        conversation_id=None,
    )

    # Assert new agent is created
    assert result_agent == mock_agent
    assert result_conversation_id == result_agent.agent_id
    assert result_session_id == "new_session_id"

    # Verify Agent was created with correct parameters
    mock_agent_class.assert_called_once_with(
        mock_client,
        model="test_model",
        instructions="test_prompt",
        input_shields=["shield1"],
        output_shields=["output_shield2"],
        tool_parser=None,
        enable_session_persistence=True,
    )


@pytest.mark.asyncio
async def test_get_agent_empty_shields(
    setup_configuration, prepare_agent_mocks, mocker
):
    """Test get_agent function with empty shields list."""
    mock_client, mock_agent = prepare_agent_mocks
    mock_agent.create_session.return_value = "new_session_id"

    # Mock Agent class
    mock_agent_class = mocker.patch(
        "utils.endpoints.AsyncAgent", return_value=mock_agent
    )

    # Mock get_suid
    mocker.patch("utils.endpoints.get_suid", return_value="new_session_id")

    # Mock configuration
    mock_mcp_server = mocker.Mock()
    mock_mcp_server.name = "mcp_server_1"
    mocker.patch.object(
        type(setup_configuration),
        "mcp_servers",
        new_callable=mocker.PropertyMock,
        return_value=[mock_mcp_server],
    )
    mocker.patch("configuration.configuration", setup_configuration)

    # Call function with empty shields list
    result_agent, result_conversation_id, result_session_id = await get_agent(
        client=mock_client,
        model_id="test_model",
        system_prompt="test_prompt",
        available_input_shields=[],
        available_output_shields=[],
        conversation_id=None,
    )

    # Assert new agent is created
    assert result_agent == mock_agent
    assert result_conversation_id == result_agent.agent_id
    assert result_session_id == "new_session_id"

    # Verify Agent was created with empty shields
    mock_agent_class.assert_called_once_with(
        mock_client,
        model="test_model",
        instructions="test_prompt",
        input_shields=[],
        output_shields=[],
        tool_parser=None,
        enable_session_persistence=True,
    )


@pytest.mark.asyncio
async def test_get_agent_multiple_mcp_servers(
    setup_configuration, prepare_agent_mocks, mocker
):
    """Test get_agent function with multiple MCP servers."""
    mock_client, mock_agent = prepare_agent_mocks
    mock_agent.create_session.return_value = "new_session_id"

    # Mock Agent class
    mock_agent_class = mocker.patch(
        "utils.endpoints.AsyncAgent", return_value=mock_agent
    )

    # Mock get_suid
    mocker.patch("utils.endpoints.get_suid", return_value="new_session_id")

    # Mock configuration with multiple MCP servers
    mock_mcp_server1 = mocker.Mock()
    mock_mcp_server1.name = "mcp_server_1"
    mock_mcp_server2 = mocker.Mock()
    mock_mcp_server2.name = "mcp_server_2"
    mocker.patch.object(
        type(setup_configuration),
        "mcp_servers",
        new_callable=mocker.PropertyMock,
        return_value=[mock_mcp_server1, mock_mcp_server2],
    )
    mocker.patch("configuration.configuration", setup_configuration)

    # Call function
    result_agent, result_conversation_id, result_session_id = await get_agent(
        client=mock_client,
        model_id="test_model",
        system_prompt="test_prompt",
        available_input_shields=["shield1", "shield2"],
        available_output_shields=["output_shield3", "output_shield4"],
        conversation_id=None,
    )

    # Assert new agent is created
    assert result_agent == mock_agent
    assert result_conversation_id == result_agent.agent_id
    assert result_session_id == "new_session_id"

    # Verify Agent was created with tools from both MCP servers
    mock_agent_class.assert_called_once_with(
        mock_client,
        model="test_model",
        instructions="test_prompt",
        input_shields=["shield1", "shield2"],
        output_shields=["output_shield3", "output_shield4"],
        tool_parser=None,
        enable_session_persistence=True,
    )


@pytest.mark.asyncio
async def test_get_agent_session_persistence_enabled(
    setup_configuration, prepare_agent_mocks, mocker
):
    """Test get_agent function ensures session persistence is enabled."""
    mock_client, mock_agent = prepare_agent_mocks
    mock_agent.create_session.return_value = "new_session_id"

    # Mock Agent class
    mock_agent_class = mocker.patch(
        "utils.endpoints.AsyncAgent", return_value=mock_agent
    )

    # Mock get_suid
    mocker.patch("utils.endpoints.get_suid", return_value="new_session_id")

    # Mock configuration
    mock_mcp_server = mocker.Mock()
    mock_mcp_server.name = "mcp_server_1"
    mocker.patch.object(
        type(setup_configuration),
        "mcp_servers",
        new_callable=mocker.PropertyMock,
        return_value=[mock_mcp_server],
    )
    mocker.patch("configuration.configuration", setup_configuration)

    # Call function
    await get_agent(
        client=mock_client,
        model_id="test_model",
        system_prompt="test_prompt",
        available_input_shields=["shield1"],
        available_output_shields=["output_shield2"],
        conversation_id=None,
    )

    # Verify Agent was created with session persistence enabled
    mock_agent_class.assert_called_once_with(
        mock_client,
        model="test_model",
        instructions="test_prompt",
        input_shields=["shield1"],
        output_shields=["output_shield2"],
        tool_parser=None,
        enable_session_persistence=True,
    )


@pytest.mark.asyncio
async def test_get_agent_no_tools_no_parser(
    setup_configuration, prepare_agent_mocks, mocker
):
    """Test get_agent function sets tool_parser=None when no_tools=True."""
    mock_client, mock_agent = prepare_agent_mocks
    mock_agent.create_session.return_value = "new_session_id"

    # Mock Agent class
    mock_agent_class = mocker.patch(
        "utils.endpoints.AsyncAgent", return_value=mock_agent
    )

    # Mock get_suid
    mocker.patch("utils.endpoints.get_suid", return_value="new_session_id")

    # Mock configuration
    mock_mcp_server = mocker.Mock()
    mock_mcp_server.name = "mcp_server_1"
    mocker.patch.object(
        type(setup_configuration),
        "mcp_servers",
        new_callable=mocker.PropertyMock,
        return_value=[mock_mcp_server],
    )
    mocker.patch("configuration.configuration", setup_configuration)

    # Call function with no_tools=True
    result_agent, result_conversation_id, result_session_id = await get_agent(
        client=mock_client,
        model_id="test_model",
        system_prompt="test_prompt",
        available_input_shields=["shield1"],
        available_output_shields=["output_shield2"],
        conversation_id=None,
        no_tools=True,
    )

    # Assert new agent is created
    assert result_agent == mock_agent
    assert result_conversation_id == result_agent.agent_id
    assert result_session_id == "new_session_id"

    # Verify Agent was created with tool_parser=None
    mock_agent_class.assert_called_once_with(
        mock_client,
        model="test_model",
        instructions="test_prompt",
        input_shields=["shield1"],
        output_shields=["output_shield2"],
        tool_parser=None,
        enable_session_persistence=True,
    )


@pytest.mark.asyncio
async def test_get_agent_no_tools_false_preserves_parser(
    setup_configuration, prepare_agent_mocks, mocker
):
    """Test get_agent function preserves tool_parser when no_tools=False."""
    mock_client, mock_agent = prepare_agent_mocks
    mock_agent.create_session.return_value = "new_session_id"

    # Mock Agent class
    mock_agent_class = mocker.patch(
        "utils.endpoints.AsyncAgent", return_value=mock_agent
    )

    # Mock get_suid
    mocker.patch("utils.endpoints.get_suid", return_value="new_session_id")

    # Mock GraniteToolParser
    mock_parser = mocker.Mock()
    mock_granite_parser = mocker.patch("utils.endpoints.GraniteToolParser")
    mock_granite_parser.get_parser.return_value = mock_parser

    # Mock configuration
    mock_mcp_server = mocker.Mock()
    mock_mcp_server.name = "mcp_server_1"
    mocker.patch.object(
        type(setup_configuration),
        "mcp_servers",
        new_callable=mocker.PropertyMock,
        return_value=[mock_mcp_server],
    )
    mocker.patch("configuration.configuration", setup_configuration)

    # Call function with no_tools=False
    result_agent, result_conversation_id, result_session_id = await get_agent(
        client=mock_client,
        model_id="test_model",
        system_prompt="test_prompt",
        available_input_shields=["shield1"],
        available_output_shields=["output_shield2"],
        conversation_id=None,
        no_tools=False,
    )

    # Assert new agent is created
    assert result_agent == mock_agent
    assert result_conversation_id == result_agent.agent_id
    assert result_session_id == "new_session_id"

    # Verify Agent was created with the proper tool_parser
    mock_agent_class.assert_called_once_with(
        mock_client,
        model="test_model",
        instructions="test_prompt",
        input_shields=["shield1"],
        output_shields=["output_shield2"],
        tool_parser=mock_parser,
        enable_session_persistence=True,
    )
