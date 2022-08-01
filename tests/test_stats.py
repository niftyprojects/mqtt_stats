import logging
from unittest.mock import MagicMock

import pytest
from paho.mqtt import client as mqtt

from mqtt_stats.mqtt_stats import MQTTStats


class MockClient:
    def __init__(self):
        self.subscribe = MagicMock()
        self.publish = MagicMock()
        self.on_connect = None
        self.on_message = None


@pytest.fixture
def mock_client():
    return MockClient()


@pytest.fixture
def client():
    return mqtt.Client()


@pytest.fixture
def mock_logging_info(monkeypatch):
    mock_info = MagicMock()
    monkeypatch.setattr(logging, "info", mock_info)
    return mock_info


@pytest.fixture
def mock_logging_error(monkeypatch):
    mock_err = MagicMock()
    monkeypatch.setattr(logging, "error", mock_err)
    return mock_err


class MockAverage:
    def __init__(self):
        self.avg = MagicMock()
        self.add = MagicMock()


@pytest.fixture
def mock_avg():
    return MockAverage()


def test_on_connect_subscribes_to_source_topic(mock_client):
    stats = MQTTStats(mock_client)  # noqa: F841
    mock_client.subscribe.return_value = (mqtt.MQTT_ERR_SUCCESS, 12)
    mock_client.on_connect(mock_client, None, None, mqtt.MQTT_ERR_SUCCESS)

    mock_client.subscribe.assert_called_once_with("random/value")


def test_on_connect_doesnt_subscribe_on_failute(mock_client):
    stats = MQTTStats(mock_client)  # noqa: F841
    mock_client.on_connect(mock_client, None, None, mqtt.MQTT_ERR_UNKNOWN)

    assert mock_client.subscribe.call_count == 0


def test_on_connect_logs_successful_subscription(mock_client, mock_logging_info):
    stats = MQTTStats(mock_client, sub_topic="test/topic")  # noqa: F841
    mock_client.subscribe.return_value = (mqtt.MQTT_ERR_SUCCESS, 12)
    mock_client.on_connect(mock_client, None, None, mqtt.MQTT_ERR_SUCCESS)

    mock_logging_info.assert_called_once_with("Subscribed to test/topic")


def test_on_connect_logs_error_on_sub_failure(mock_client, mock_logging_error):
    stats = MQTTStats(mock_client, sub_topic="test/topic")  # noqa: F841
    mock_client.subscribe.return_value = (mqtt.MQTT_ERR_UNKNOWN, 12)
    mock_client.on_connect(mock_client, None, None, mqtt.MQTT_ERR_SUCCESS)

    mock_logging_error.assert_called_once_with(
        "Unable to subscribe to test/topic: Unknown error."
    )


def test_on_connect_logs_error_on_failure(mock_client, mock_logging_error):
    stats = MQTTStats(mock_client)  # noqa: F841
    mock_client.on_connect(mock_client, None, None, mqtt.MQTT_ERR_NO_CONN)

    mock_logging_error.assert_called_once_with(
        "Unable to connect: The client is not currently connected."
    )


def test_new_values_are_pushed_to_stats_calculator(mock_client, mock_avg):
    stats = MQTTStats(mock_client)
    stats.stats = mock_avg

    msg = mqtt.MQTTMessage(topic="random/value")
    msg.payload = "123"
    mock_client.on_message(mock_client, None, msg)

    mock_avg.add.assert_called_once_with(123)


def test_non_integer_values_are_logged(mock_client, mock_avg, mock_logging_error):
    stats = MQTTStats(mock_client)
    stats.stats = mock_avg

    msg = mqtt.MQTTMessage(topic="random/value")
    msg.payload = "blas"
    mock_client.on_message(mock_client, None, msg)

    assert mock_avg.add.call_count == 0
    mock_logging_error.assert_called_once_with("Bad integer: 'blas'")


def test_publish_pushes_averages(mock_client, mock_avg):
    mock_avg.avg.return_value = {"first": 12.3, "sec": 32.22}

    stats = MQTTStats(mock_client)
    stats.stats = mock_avg

    stats.publish()

    mock_client.publish.assert_called_once_with(
        "random/stats", '{"first": 12.3, "sec": 32.22}'
    )
