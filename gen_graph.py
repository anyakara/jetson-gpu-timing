import time
import psutil
import subprocess
import matplotlib.pyplot as plt
from datetime import datetime
import signal
import sys

# Lists to store stats
gpu_utilizations = []
gpu_memory_used = []
timestamps = []

# Flag to indicate whether to collect data
collecting_data = True

def get_gpu_info_from_tegrastats():
    """Fetch GPU info from tegrastats."""
    try:
        # Start tegrastats in a continuous stream
        process = subprocess.Popen(
            "tegrastats", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )

        # Capture output line by line in real time
        for line in process.stdout:
            print(f"Raw tegrastats output: {line.strip()}")  # Debugging: print every line of output

            if not collecting_data:
                break  # Stop collecting when flag is set to False

            # Skip the timestamp by finding the first space and removing everything before it
            line_data = line.split(' ', 1)[-1]  # Remove the timestamp

            # Debugging: print the data we're parsing
            print(f"Parsed line (after timestamp removal): {line_data}")

            if "GR3D_FREQ" in line_data:
                # Extract the GPU utilization from GR3D_FREQ
                try:
                    # Example format: GR3D_FREQ 0% cpu@48.12C
                    gpu_utilization = int(line_data.split("GR3D_FREQ")[1].split('%')[0].strip())
                    gpu_utilizations.append(gpu_utilization)
                    print(f"Extracted GPU utilization: {gpu_utilization}%")
                except Exception as e:
                    print(f"Error parsing GPU utilization: {e}")
            
            if "RAM" in line_data:
                # Extract GPU memory used (if present in RAM data)
                try:
                    # Example format: RAM 4472/7620MB (lfb 6x4MB) ...
                    memory_used = int(line_data.split("RAM")[1].split("/")[0].strip())
                    gpu_memory_used.append(memory_used)
                    print(f"Extracted GPU memory used: {memory_used}MB")
                except Exception as e:
                    print(f"Error parsing GPU memory: {e}")

            # If we have collected both GPU utilization and memory used, store timestamp
            if len(gpu_utilizations) > 0 and len(gpu_memory_used) > 0:
                timestamps.append(datetime.now().strftime('%H:%M:%S'))

    except Exception as e:
        print(f"Error fetching GPU stats from tegrastats: {e}")

def collect_stats():
    """Collect system and GPU stats."""
    global collecting_data

    while collecting_data:
        # Collect CPU and memory stats
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent

        # Collect GPU stats from tegrastats
        get_gpu_info_from_tegrastats()

        # Print out stats for debugging
        print(f"CPU Usage: {cpu_usage}%")
        print(f"Memory Usage: {memory_usage}%")

        # Delay between collecting stats
        time.sleep(1)

def plot_stats():
    """Plot collected stats and save the plot."""
    if len(gpu_utilizations) == 0 or len(gpu_memory_used) == 0:
        print("No GPU data to plot.")
        return

    plt.figure(figsize=(10, 5))

    # Plot GPU utilization
    plt.subplot(1, 2, 1)
    plt.plot(timestamps, gpu_utilizations, label="GPU Utilization (%)", color="b")
    plt.xlabel('Time')
    plt.ylabel('GPU Utilization (%)')
    plt.title('GPU Utilization Over Time')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Plot GPU memory usage
    plt.subplot(1, 2, 2)
    plt.plot(timestamps, gpu_memory_used, label="GPU Memory Used (MB)", color="r")
    plt.xlabel('Time')
    plt.ylabel('GPU Memory Used (MB)')
    plt.title('GPU Memory Usage Over Time')
    plt.xticks(rotation=45)
    plt.grid(True)

    plt.tight_layout()

    # Save the plot as a PNG file
    plot_filename = "gpu_stats_plot.png"
    plt.savefig(plot_filename)
    print(f"Plot saved as {plot_filename}")

    # Show the plot
    plt.show()


def stop_data_collection(signal, frame):
    """Stop data collection on signal."""
    global collecting_data
    collecting_data = False
    print("Signal received, stopping data collection...")

    plot_stats()

if __name__ == "__main__":
    # Set up signal handler to stop collection and plot when Ctrl+C is pressed
    signal.signal(signal.SIGINT, stop_data_collection)

    print("Starting to collect system and GPU stats...")
    collect_stats()

