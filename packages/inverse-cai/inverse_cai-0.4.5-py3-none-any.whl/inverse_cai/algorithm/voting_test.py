"""
Tests for the voting module.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from inverse_cai.algorithm.voting import (
    get_preference_vote_for_single_text,
    clean_vote_json,
    parse_individual_pref_vote,
)
from inverse_cai.experiment.core import ExpConfig


@patch("inverse_cai.algorithm.voting.inverse_cai.models.get_model")
@patch("inverse_cai.algorithm.voting.random.choice")
@pytest.mark.asyncio
async def test_get_preference_vote_for_single_text_flipped(
    mock_random_choice, mock_get_model
):
    """Test preference voting when the order of samples is flipped."""
    # outputs are always flipped
    mock_random_choice.return_value = True
    mock_model = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = '{0: "A", 1: "B"}'
    mock_model.ainvoke.return_value = mock_response
    mock_get_model.return_value = mock_model

    result = await get_preference_vote_for_single_text(
        prompt="prompt",
        preferred_sample="preferred_sample",
        rejected_sample="rejected_sample",
        principles=["p1", "p2"],
        config=ExpConfig(),
        model_name="openai/gpt-4o-mini-2024-07-18",
    )

    assert result == {"p1": False, "p2": True}


@patch("inverse_cai.algorithm.voting.inverse_cai.models.get_model")
@patch("inverse_cai.algorithm.voting.random.choice")
@pytest.mark.asyncio
async def test_get_preference_vote_for_single_text_not_flipped(
    mock_random_choice, mock_get_model
):
    """Test preference voting when the order of samples is not flipped."""
    mock_random_choice.return_value = False
    mock_model = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = '{0: "A", 1: "B"}'
    mock_model.ainvoke.return_value = mock_response
    mock_get_model.return_value = mock_model

    result = await get_preference_vote_for_single_text(
        prompt="prompt",
        preferred_sample="preferred_sample",
        rejected_sample="rejected_sample",
        principles=["p1", "p2"],
        config=ExpConfig(),
        model_name="openai/gpt-4o-mini-2024-07-18",
    )

    assert result == {"p1": True, "p2": False}


@patch("inverse_cai.algorithm.voting.inverse_cai.models.get_model")
@patch("inverse_cai.algorithm.voting.random.choice")
@pytest.mark.asyncio
async def test_get_preference_vote_for_single_text_invalid_vote(
    mock_random_choice, mock_get_model
):
    """Test preference voting when an invalid vote is returned by model."""
    mock_random_choice.return_value = False
    mock_model = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = '{"0": "C", "1": "None"}'
    mock_model.ainvoke.return_value = mock_response
    mock_get_model.return_value = mock_model

    return_val = await get_preference_vote_for_single_text(
        prompt="prompt",
        preferred_sample="preferred_sample",
        rejected_sample="rejected_sample",
        principles=["p1", "p2"],
        config=ExpConfig(),
        model_name="openai/gpt-4o-mini-2024-07-18",
    )
    assert return_val == {"p1": "invalid", "p2": None}


@patch("inverse_cai.algorithm.voting.inverse_cai.models.get_model")
@pytest.mark.asyncio
async def test_get_preference_vote_for_single_text_invalid_json(mock_get_model):
    """Test preference voting when invalid JSON is returned."""
    mock_model = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = "invalid_json"
    mock_model.ainvoke.return_value = mock_response
    mock_get_model.return_value = mock_model

    result = await get_preference_vote_for_single_text(
        prompt="prompt",
        preferred_sample="preferred_sample",
        rejected_sample="rejected_sample",
        principles=["p1", "p2"],
        config=ExpConfig(),
        model_name="openai/gpt-4o-mini-2024-07-18",
    )

    assert all(
        value == "invalid" for value in result.values()
    ), "Expected all votes to be 'invalid' due to invalid JSON"


@patch("inverse_cai.algorithm.voting.inverse_cai.models.get_model")
@pytest.mark.asyncio
async def test_get_preference_vote_for_single_text_all_keys_present(mock_get_model):
    """Test that all summary keys are present in the preference voting result."""
    mock_model = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = '{"0": "A", "1": "B", "2": "A"}'
    mock_model.ainvoke.return_value = mock_response
    mock_get_model.return_value = mock_model

    result = await get_preference_vote_for_single_text(
        prompt="prompt",
        preferred_sample="preferred_sample",
        rejected_sample="rejected_sample",
        principles=["p1", "p2", "p3"],
        config=ExpConfig(),
        model_name="openai/gpt-4o-mini-2024-07-18",
    )

    assert set(result.keys()) == {
        "p1",
        "p2",
        "p3",
    }, "Not all keys from summaries are present in the result"


def test_clean_vote_json():
    """Test cleaning and formatting of vote JSON strings."""
    vote_json = '{"1": "true", "2": "false", "3": "null", "4": "A", "5": "B"}'
    summaries = {1: "sum1", 2: "sum2", 3: "sum3", 4: "sum4", 5: "sum5"}

    cleaned_json = clean_vote_json(vote_json, len(summaries))
    expected_json = '{1:True,2:False,3:None,4:"A",5:"B"}'

    assert (
        cleaned_json == expected_json
    ), "The clean_vote_json function did not clean the JSON as expected"


@patch("inverse_cai.algorithm.voting.inverse_cai.models.get_model")
@pytest.mark.asyncio
async def test_get_preference_vote_for_single_text_unexpected_values(mock_get_model):
    """Test to ensure unexpected vote values are counted as invalid in preference voting."""
    mock_model = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = '{"0": "Z", "1": "Y"}'  # Unexpected values
    mock_model.ainvoke.return_value = mock_response
    mock_get_model.return_value = mock_model

    result = await get_preference_vote_for_single_text(
        prompt="prompt",
        preferred_sample="preferred_sample",
        rejected_sample="rejected_sample",
        principles=["p1", "p2"],
        config=ExpConfig(),
        model_name="openai/gpt-4o-mini-2024-07-18",
    )

    assert all(
        value == "invalid" for value in result.values()
    ), "Expected all votes to be counted as invalid due to unexpected values"


def test_parse_individual_pref_vote():
    """Test parsing of individual preference votes from JSON responses."""

    # Define valid values for A/B voting
    valid_values = {
        "A": "A",
        "B": "B",
        "Both": "Both",
        "Neither": "Neither",
        "None": None,
        None: None,
    }

    # Test valid JSON votes
    assert parse_individual_pref_vote(
        vote='{"1": "A", "2": "B"}', num_principles=2, valid_values=valid_values
    ) == {
        1: "A",
        2: "B",
    }, "Should correctly parse A/B votes"

    # Test invalid JSON format
    assert parse_individual_pref_vote(
        vote="invalid_json", num_principles=2, valid_values=valid_values
    ) == {
        0: "invalid",
        1: "invalid",
    }, "Should mark invalid JSON as invalid votes"

    # Test missing keys
    assert parse_individual_pref_vote(
        vote='{"1": "A"}', num_principles=2, valid_values=valid_values
    ) == {
        1: "A",
    }, "Should parse partial votes"

    # Test invalid vote values
    assert parse_individual_pref_vote(
        vote='{"1": "C", "2": "D"}', num_principles=2, valid_values=valid_values
    ) == {
        1: "invalid",
        2: "invalid",
    }, "Should mark invalid vote values as 'invalid'"

    # Test with None values
    assert parse_individual_pref_vote(
        vote='{"1": "foo", "2": "A"}', num_principles=2, valid_values=valid_values
    ) == {
        1: "invalid",
        2: "A",
    }, "Should handle null values"

    # Test with different summary lengths
    assert parse_individual_pref_vote(
        vote='{"1": "A", "2": "B", "3": "A"}',
        num_principles=3,
        valid_values=valid_values,
    ) == {
        1: "A",
        2: "B",
        3: "A",
    }, "Should handle different numbers of summaries"
