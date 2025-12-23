import socket
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--inject-stale", action="store_true")
parser.add_argument("--rate-hz", type=float, default=10.0)
args = parser.parse_args()

HOST = "127.0.0.1"
PORT = 9000
seq = 0
last_ts_sent = -1
STALE_EVERY = 20
STALE_DELTA = 1000000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    ts = time.perf_counter_ns()
    if (seq % STALE_EVERY == 0 and last_ts_sent != -1 and args.inject_stale):
        ts = last_ts_sent - STALE_DELTA
    packet = f"{seq},{ts}"
    s.sendto(packet.encode("utf-8"), (HOST, PORT))

    if ts > last_ts_sent:
        last_ts_sent = ts

    seq += 1
    if args.rate_hz > 0:
        time.sleep(1/args.rate_hz)

    if seq % 10 == 0:
        print("sent 10 messages to reviever")