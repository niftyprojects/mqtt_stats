import json
import logging

from paho.mqtt import client as mqtt

from mqtt_stats.average import GroupedTimedAverage


class MQTTStats:
    """Statistics of MQTT Values."""

    INTERVALS = {"1_min": 60, "5_min": 5 * 60, "30_min": 30 * 60}

    def __init__(
        self,
        client: mqtt.Client,
        sub_topic: str = "random/value",
        pub_topic: str = "random/stats",
    ):

        """Initialize stastics handler.

        Arguments:

        client
          An unconnected mqtt.Client instance.

        Optional Arguments:

        pub_topic
          The topic to publish the stastics to.

        sub_topic
          The topic to subscribe to for incoming values.
        """
        self.client = client
        self.sub_topic = sub_topic
        self.pub_topic = pub_topic
        self.stats = GroupedTimedAverage(MQTTStats.INTERVALS)
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message

    def __on_connect(self, client, userdata, flags, rc):
        if rc == mqtt.MQTT_ERR_SUCCESS:
            rc, mid = self.client.subscribe(self.sub_topic)
            if rc == mqtt.MQTT_ERR_SUCCESS:
                logging.info(f"Subscribed to {self.sub_topic}")
            else:
                logging.error(
                    f"Unable to subscribe to {self.sub_topic}: {mqtt.error_string(rc)}"
                )
        else:
            logging.error(f"Unable to connect: {mqtt.error_string(rc)}")

    def __on_message(self, client, userdata, msg: mqtt.MQTTMessage):
        try:
            self.stats.add(int(msg.payload))
        except ValueError:
            logging.error(f"Bad integer: '{msg.payload}'")

    def publish(self) -> None:
        """Publish the averages to the broker.

        The averages are serialized in JSON.
        """
        self.client.publish(self.pub_topic, json.dumps(self.stats.avg()))
