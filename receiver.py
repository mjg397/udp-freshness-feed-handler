import socket
import time

HOST = "127.0.0.1"
PORT = 9000

recieved = 0
accepted = 0
dropped = 0
last_sender_ts = -1

latency_sum = 0
latency_count = 0

start_ns = time.perf_counter_ns()
next_report_ns = start_ns + 1000000000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))

while True:
    data, addr = s.recvfrom(1024)
    msg = data.decode()
    fields = msg.split(",")
    seq = int(fields[0].strip())
    sender_ts = int(fields[1].strip())
    now_ns = time.perf_counter_ns()

    recieved += 1
    

    if sender_ts <= last_sender_ts:
        dropped += 1
    else:
        accepted += 1
        last_sender_ts = sender_ts

        latency = now_ns - sender_ts
        latency_count += 1
        latency_sum += latency
        
        if (seq % 4 == 0):
            print(f"recieved mesage: {seq} from {addr} with {latency} ns of latency")


    # periodic report
    if now_ns >= next_report_ns:
        elapsed_s = (now_ns - start_ns) / 1e9
        invariant_ok = (recieved == accepted + dropped)
        avg_us = (latency_sum / latency_count) / 1000 if latency_count > 0 else 0.0

        print (f"t={elapsed_s:.1f}s recv={recieved} acc={accepted} drop={dropped} "
               f"inv={'Ok' if invariant_ok else 'Bad'} avg={avg_us:.1f}us"
        )

        next_report_ns += 1000000000