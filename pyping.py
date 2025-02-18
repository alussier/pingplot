# credit to chatgpt o3-mini-high
import curses
import subprocess
import time
import re

def get_ping_time(host):
    """
    Pings the given host once and returns the ping time in milliseconds.
    Uses the Linux ping syntax ("-c 1"). For Windows, use "-n 1".
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "1", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        output = result.stdout
        match = re.search(r'time=([\d.]+)', output)
        if match:
            return float(match.group(1))
    except Exception:
        pass
    return None

def main(stdscr):
    # Hide the cursor and enable non-blocking input.
    curses.curs_set(0)
    stdscr.nodelay(True)

    host = "google.com"  # Change this to your target server.
    data = []  # To store recent ping times

    # Define margins for the graph (for axis labels and spacing)
    margin_left = 6    # Reserve columns on the left for Y-axis labels
    margin_bottom = 2  # Reserve rows at the bottom for the X-axis

    # Info box dimensions (for statistics)
    info_box_height = 7  # Increased height to show stats and last 3 pings
    info_box_width = 30

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()

        # Draw header.
        header_text = f"Ping times to {host} (ms) - Press 'q' to quit"
        try:
            stdscr.addstr(0, 0, header_text)
        except curses.error:
            pass

        # Determine graph area boundaries.
        graph_top = 1
        graph_bottom = max_y - margin_bottom - 1  # leave room for X-axis line
        graph_height = graph_bottom - graph_top + 1
        graph_width = max_x - margin_left - 1  # leave room on right

        # Maximum number of data points that fit horizontally.
        max_data_points = graph_width

        # Get a new ping time and add it to the list.
        ping_time = get_ping_time(host)
        data.append(ping_time if ping_time is not None else 0)

        # Keep only the most recent data points.
        if len(data) > max_data_points:
            data.pop(0)

        # Compute statistics.
        if data:
            min_ping = min(data)
            max_ping = max(data)
            avg_ping = sum(data) / len(data)
            # Avoid division by zero.
            if max_ping == min_ping:
                max_ping = min_ping + 1
        else:
            min_ping = max_ping = avg_ping = 0

        # Draw the Y-axis (vertical line).
        for y in range(graph_top, graph_bottom + 1):
            try:
                stdscr.addch(y, margin_left, '|')
            except curses.error:
                pass

        # Draw the X-axis (horizontal line).
        for x in range(margin_left, margin_left + graph_width + 1):
            try:
                stdscr.addch(graph_bottom, x, '-')
            except curses.error:
                pass

        # Mark the origin where axes meet.
        try:
            stdscr.addch(graph_bottom, margin_left, '+')
        except curses.error:
            pass

        # Add Y-axis labels for each row in the graph area.
        for y in range(graph_top, graph_bottom + 1):
            value = max_ping - ((y - graph_top) * (max_ping - min_ping) / (graph_height - 1))
            try:
                stdscr.addstr(y, 0, f"{value:5.1f}")
            except curses.error:
                pass

        # Draw the ping times graph.
        for i, pt in enumerate(data):
            normalized = int((pt - min_ping) / (max_ping - min_ping) * (graph_height - 1))
            y = graph_bottom - normalized
            x = margin_left + i + 1  # offset to avoid overwriting the Y-axis
            if x < max_x and y < max_y:
                try:
                    stdscr.addch(y, x, '*')
                except curses.error:
                    pass

        # Create and draw the stats info box.
        box_top = 1
        box_left = max_x - info_box_width - 1
        if box_left < margin_left + 5:
            box_left = margin_left + 5  # Ensure it's not too close to the graph.
        info_win = curses.newwin(info_box_height, info_box_width, box_top, box_left)
        info_win.box()
        try:
            info_win.addstr(0, 2, " Stats ")
            info_win.addstr(1, 2, f"Min: {min_ping:6.2f} ms")
            info_win.addstr(2, 2, f"Max: {max_ping:6.2f} ms")
            info_win.addstr(3, 2, f"Avg: {avg_ping:6.2f} ms")
            # Prepare and add the last 3 ping times in reverse order (newest first).
            last_three = data[-3:][::-1]
            last_str = ", ".join(f"{pt:4.1f}" for pt in last_three)
            info_win.addstr(4, 2, f"Last: {last_str}")
        except curses.error:
            pass

        # Refresh the main screen then the info box.
        stdscr.refresh()
        info_win.refresh()
        
        time.sleep(1)

        # Check for user input to exit.
        try:
            key = stdscr.getkey()
            if key.lower() == 'q':
                break
        except curses.error:
            # No key was pressed.
            pass

if __name__ == "__main__":
    curses.wrapper(main)
