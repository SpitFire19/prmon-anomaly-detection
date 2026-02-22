import subprocess
import time
import random
import numpy as np
import argparse
from pathlib import Path

# Generate time series imitating system resource load using prmon + noise

# This script is suppose to be run from prmon root
# Resolve burner test paths
SCRIPT_DIR = Path(__file__).resolve().parent
TEST_DIR = SCRIPT_DIR / "build" / "package" / "tests" 
BURNER = TEST_DIR / "burner"
MEM_BURNER = TEST_DIR / "mem-burner"


# Add command-line arguments to allow for more flexible data generation
parser = argparse.ArgumentParser(description="prmon workload generator")
parser.add_argument(
    "--samples",
    type=int,
    default=1000,
    help="Total number of time samples (default: 1000)"
)
parser.add_argument(
    "--rate",
    type=float,
    default=0.05,
    help="Fraction of anomaly samples (default: 0.05)"
)

args = parser.parse_args()

samples = args.samples
contamination = args.rate

# Don't generate anomalies in the first and last 10% of data
first_anomaly, last_anomaly = int(samples * 0.1), int(samples * 0.9)
anomaly_duration = 10
# Set anomalies to be distant in time
min_spacing = 60
# Anomaly count is obtained from sample count and contamination rate
anomaly_count = int(samples * contamination / anomaly_duration)
print(anomaly_count)
# Set seeds to be reproducible
random.seed(42)
np.random.seed(42)

# Generate data corrupted by white gaussian noise
def gaussian_from_range(a, b):
    mean = (a + b) / 2
    sigma =  (b-a)/4 #  Make so that 95% of data lie within [a, b], with P(|X-u| > 2* sigma ) < 0.05
    variance = sigma ** 2
    sigma = np.sqrt(variance)
    value = np.random.normal(mean, sigma)
    return int(round(value))

# Generate anomaly start times
anomaly_times = []
while len(anomaly_times) < anomaly_count:
    candidate = random.randint(first_anomaly, last_anomaly)
    # Ensure that anomalies respect min spacing
    if all(abs(candidate - existing) >= min_spacing
           for existing in anomaly_times):
        anomaly_times.append(candidate)

# Write anomalies start times and their duration to file
with open("anomalies_start.csv", "w") as f:
    f.write("start_time,duration\n")
    for t in anomaly_times:
        f.write(f"{t},{anomaly_duration}\n")

print("Anomaly start times:", anomaly_times)

# Set background CPU noise, analogous to OS taking resources by default
cpu_background = subprocess.Popen(
    [BURNER, "-t", "1", "-p", "1", "-r", str(samples)]
)

# Main loop
try:
    for t in range(1, samples + 1):
        anomaly_active = False
        anomaly_type = None

        for a in anomaly_times:
            if a <= t < a + anomaly_duration:
                anomaly_active = True
                anomaly_type = random.randint(0, 2)
                break
        if anomaly_active:
            if anomaly_type == 0:
                # Type 1: Memory anomaly
                mem = gaussian_from_range(600, 700)
                procs = gaussian_from_range(2, 5)
                threads = gaussian_from_range(3, 6)
            elif anomaly_type == 1:
                # Type 2: Process anomaly
                mem = gaussian_from_range(420, 550)
                procs = gaussian_from_range(6, 10)
                threads = gaussian_from_range(4, 7)
            else:
                # Type 3: Thread anomaly
                mem = gaussian_from_range(380, 420)
                procs = gaussian_from_range(4, 8)
                threads = gaussian_from_range(5, 10)
        else:
            # Normal baseline
            mem = gaussian_from_range(290, 310)
            procs = gaussian_from_range(2, 4)
            threads = gaussian_from_range(2, 4)

        subprocess.Popen([MEM_BURNER, "-m", str(mem),
                          "-p", str(procs), "-s", "1"])
        subprocess.Popen([BURNER, "-t", str(threads),
                          "-p", str(procs), "-r", "1"])
        time.sleep(1)
finally:
    cpu_background.terminate() # terminate background noise

print("Workload finished.")