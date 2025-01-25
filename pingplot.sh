#!/usr/bin/env bash

killall gnuplot

# Quick check for gnuplot:
if ! command -v gnuplot &>/dev/null; then
  echo "Please install gnuplot (e.g., brew install gnuplot)."
  exit 1
fi

# default to 192.168.1.1
SERVER="${1:-192.168.1.1}"

# Temporary file to collect timestamp + latency
TMPFILE=$(mktemp)

# Cleanup function to run on script exit
cleanup() {
  echo "Cleaning up..."
  # Kill the background ping
  kill "$PING_PID" 2>/dev/null
  # Remove the temporary file
  rm -f "$TMPFILE"
}
# Register the cleanup function to be called on EXIT (script end)
trap cleanup EXIT

echo "Pinging $SERVER... Press Ctrl+C to stop."
echo "Data is logged to $TMPFILE"

# Start ping, parse each line in a while-loop, extract the latency
ping "$SERVER" | \
while IFS= read -r line; do
  # Skip lines that don’t have 'time='
  [[ "$line" =~ time= ]] || continue

  # Use a bash regex to capture the numeric portion after time=
  if [[ "$line" =~ time=([0-9.]+) ]]; then
    latency="${BASH_REMATCH[1]}"
    # Print epoch_timestamp and the latency
    echo "$(date +%s) $latency" >> "$TMPFILE"
  fi
done &

PING_PID=$!

# Run gnuplot in "persist" mode so the window remains
gnuplot -persist <<EOF
set title "Ping times to ${SERVER}"
set xlabel "Time (HH:MM:SS)"
set ylabel "Latency (ms)"
set grid

# Treat the first column as Unix epoch time
set xdata time
set timefmt "%s"
set format x "%H:%M:%S"

while (1) {
    plot "${TMPFILE}" using 1:2 with lines title "Ping (ms)"
    pause 1
}
EOF

