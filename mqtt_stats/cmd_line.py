import argparse
import logging
from time import sleep

from mqtt_stats.connection import mqtt_client
from mqtt_stats.mqtt_stats import MQTTStats

LOG_LEVEL = {
    "debug": logging.DEBUG,
    "warn": logging.WARN,
    "error": logging.ERROR,
    "info": logging.INFO,
}


def run_stats(broker: str = "mqtt://localhost", interval: int = 30):
    client = mqtt_client(broker)
    stats = MQTTStats(client)
    client.loop_start()
    try:
        while True:
            sleep(interval)
            stats.publish()
    except KeyboardInterrupt:
        pass
    client.loop_stop()


def main():
    parser = argparse.ArgumentParser(
        description="Calculates statistics on values from a MQTT topic."
    )
    parser.add_argument(
        "--log_level",
        help="Set the logging level. Default error",
        choices=LOG_LEVEL.keys(),
        default="warn",
    )
    parser.add_argument(
        "--interval",
        default=30,
        help="Interval to publish stats on, in seconds. Default 30s.",
    )
    parser.add_argument(
        "broker",
        default="mqtt://localhost",
        help="MQTT broker URL, default mqtt://localhost",
        nargs="?",
    )
    args = parser.parse_args()

    logging.basicConfig(level=LOG_LEVEL[args.log_level])

    run_stats(broker=args.broker, interval=args.interval)


if __name__ == "__main__":
    main()
