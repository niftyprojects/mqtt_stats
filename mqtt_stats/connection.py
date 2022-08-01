from urllib.parse import urlparse

import paho.mqtt.client as mqtt


def mqtt_client(url: str) -> mqtt.Client:
    """Make a connection to a MQTT broker

    Arguments:

    url
      A url to connect to mqtt(s)://hostname:port
      Username/password authentication is not supported.

    Returns a Paho MQTT client instance
    """
    loc = urlparse(url)
    c = mqtt.Client()

    host = loc.hostname
    if loc.scheme == "mqtts":
        port = loc.port if loc.port else 8883
        # Uses system certs for validation.
        c.tls_set()
    else:
        port = loc.port if loc.port else 1883

    c.connect(host, port, 60)

    return c
