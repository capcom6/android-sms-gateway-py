import pytest

from android_sms_gateway.domain import MessageState, RecipientState


# Test for successful instantiation from a dictionary
def test_message_state_from_dict():
    payload = {
        "id": "123",
        "state": "Pending",
        "recipients": [
            {"phoneNumber": "123", "state": "Pending"},
            {"phoneNumber": "456", "state": "Pending"},
        ],
        "isHashed": True,
        "isEncrypted": False,
    }

    message_state = MessageState.from_dict(payload)
    assert message_state.id == payload["id"]
    assert message_state.state.name == payload["state"]
    assert all(
        isinstance(recipient, RecipientState) for recipient in message_state.recipients
    )
    assert len(message_state.recipients) == len(payload["recipients"])
    assert message_state.is_hashed == payload["isHashed"]
    assert message_state.is_encrypted == payload["isEncrypted"]


# Test for backward compatibility
def test_message_state_from_dict_backwards_compatibility():
    payload = {
        "id": "123",
        "state": "Pending",
        "recipients": [
            {"phoneNumber": "123", "state": "Pending"},
            {"phoneNumber": "456", "state": "Pending"},
        ],
    }

    message_state = MessageState.from_dict(payload)
    assert message_state.id == payload["id"]
    assert message_state.state.name == payload["state"]
    assert all(
        isinstance(recipient, RecipientState) for recipient in message_state.recipients
    )
    assert len(message_state.recipients) == len(payload["recipients"])
    assert message_state.is_hashed is False
    assert message_state.is_encrypted is False


# Test for handling missing fields
def test_message_state_from_dict_missing_fields():
    incomplete_payload = {
        "id": "123",
        # 'state' is missing
        "recipients": [
            {"phoneNumber": "123", "state": "Pending"}
        ],  # Assume one recipient is enough to test
        "isHashed": True,
        "isEncrypted": False,
    }

    with pytest.raises(KeyError):
        MessageState.from_dict(incomplete_payload)


# Test for handling incorrect types
def test_message_state_from_dict_incorrect_types():
    incorrect_payload = {
        "id": 123,  # Should be a string
        "state": 42,  # Should be a string that can be converted to a ProcessState
        "recipients": "Alice, Bob",  # Should be a list of dictionaries
        "isHashed": "yes",  # Should be a boolean
        "isEncrypted": "no",  # Should be a boolean
    }

    with pytest.raises(
        Exception
    ):  # Replace Exception with the specific exception you expect
        MessageState.from_dict(incorrect_payload)
