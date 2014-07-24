from config import *
from time import sleep
from json import dumps
import requests

# TODO: Daemonize this script


def update_bandwidth(src, dest, bw):
    data = {
        "method": "update_bandwidth",
        "params": {
            "dpid1": SWITCHES[src],
            "dpid2": SWITCHES[dest],
            "bandwidth": bw,
        },
    }
    print "%s %s => bw %f" % (src, dest, bw),
    print requests.post(OVERSEER_API_ENDPOINT, data=dumps(data)).json()


def update_latency(src, dest, lat):
    data = {
        "method": "update_latency",
        "params": {
            "dpid1": SWITCHES[src],
            "dpid2": SWITCHES[dest],
            "latency": lat,
        },
    }
    print "%s %s => bw %f" % (src, dest, lat),
    print requests.post(OVERSEER_API_ENDPOINT, data=dumps(data)).json()


if __name__ == "__main__":
    while(True):
        flows = requests.get(OVERLORD_API_ENDPOINT).json()["result"]
        for flow in flows:
            update_bandwidth(flow["src"], flow["dest"], flow["iperf"]["bandwidth"])
            update_latency(flow["src"], flow["dest"], flow["ping"]["avg"])
        sleep(DELAY)
