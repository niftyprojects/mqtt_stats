from unittest.mock import MagicMock

import paho.mqtt.client as mqtt
import pytest

from mqtt_stats import mqtt_client


class MockClient:
    def __init__(self):
        self.connect = MagicMock()
        self.tls_set = MagicMock()


@pytest.fixture
def patch_client(monkeypatch):
    monkeypatch.setattr(mqtt, "Client", MockClient)


def test_client_created_with_correct_host_name_and_default_port(patch_client):
    client = mqtt_client("mqtt://this.is.a.host")

    client.connect.assert_called_once_with("this.is.a.host", 1883, 60)


def test_client_created_with_non_default_port(patch_client):
    client = mqtt_client("mqtt://another.host:1234")

    client.connect.assert_called_once_with("another.host", 1234, 60)


def test_clients_sets_up_tls_params_if_secure_connection(patch_client):
    client = mqtt_client("mqtts://another.host")

    client.tls_set.assert_called_once_with()
    client.connect.assert_called_once_with("another.host", 8883, 60)
