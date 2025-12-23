# UDP Freshness-First Feed Handler

This project is a minimal prototype of a low-latency market data feed handler.
It demonstrates freshness-first (“newest wins”) processing, where stale or out-of-order packets are deterministically dropped to preserve correctness.

The system is intentionally simple and focuses on time, ordering, and correctness invariants, not trading strategies.

OVERVIEW

The system consists of:
- A UDP sender that emits packets containing a sequence number and a sender-side timestamp
- A UDP receiver that enforces freshness guarantees and measures end-to-end latency

Key properties:
- Out-of-order or stale packets are dropped
- Correctness is validated via invariants
- Latency is measured using monotonic clocks
- Deterministic fault injection is supported for testing

PACKET FORMAT

Each UDP packet is a UTF-8 encoded, comma-separated string:

seq,sender_ts_ns

Where:
- seq is a monotonically increasing sequence number
- sender_ts_ns is a sender-side timestamp in nanoseconds

TIME AND LATENCY

Both sender and receiver use time.perf_counter_ns() to ensure:
- Monotonic timestamps
- Immunity to wall-clock adjustments
- Correct ordering comparisons

Latency is measured as:

latency_ns = receiver_now_ns - sender_ts_ns

This represents end-to-end application latency, including OS scheduling, UDP receive handling, and Python user-space overhead.

RECEIVER LOGIC (FRESHNESS-FIRST)

The receiver maintains a single piece of state:

last_sender_ts

Processing rule:
- Accept packet if sender_ts > last_sender_ts
- Drop packet if sender_ts <= last_sender_ts

Accepted packets update last_sender_ts.

Correctness invariant:
received = accepted + dropped

This invariant is continuously checked and reported.

FAULT INJECTION

The sender supports deterministic stale-packet injection.

When enabled:
- Every Nth packet is assigned a timestamp older than the last valid timestamp
- This guarantees the packet is stale relative to receiver state

This allows controlled testing of drop behavior without relying on timing races.

RUNNING THE DEMO

Terminal 1 — Receiver:
python receiver.py

Terminal 2 — Sender (normal operation):
python sender.py --rate-hz 50

Expected behavior:
- drop = 0
- inv = OK

Terminal 2 — Sender (stale injection enabled):
python sender.py --rate-hz 50 --inject-stale

Expected behavior:
- drop > 0
- inv = OK
- Approximately one drop per injection interval

TELEMETRY OUTPUT

The receiver prints periodic (1-second) telemetry in the following form:

t=10.0s recv=100 acc=95 drop=5 inv=OK avg=190.2us

Fields:
- recv: total packets received
- acc: packets accepted
- drop: packets dropped as stale
- inv: correctness invariant status
- avg: average latency of accepted packets in microseconds

NOTES

- Console printing increases measured latency due to I/O overhead
- Latency values vary with OS scheduling and system load
- The focus is on behavioral correctness, not absolute latency numbers

MOTIVATION

This project models a core problem in low-latency trading systems: ensuring correctness under out-of-order delivery while minimizing processing delay.

It is intended as a foundational building block for market data pipelines, order book construction, low-latency execution systems, and hardware-accelerated FPGA data paths.

FUTURE EXTENSIONS

Possible extensions include:
- Sliding-window latency statistics (p50 / p99)
- Multi-stream or multi-symbol support
- Replay from recorded packet traces
- Shared-memory or FPGA-based ingestion
