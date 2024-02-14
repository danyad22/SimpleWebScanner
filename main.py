import random
import multiprocessing
import socket
import time
import argparse

# ANSI color codes for red and green
RED = '\033[91m'
GREEN = '\033[92m'
ENDC = '\033[0m'  # Reset color

def ping(ip_address, timeout=2, verbose=False):
    try:
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip_address, 80))
        elapsed_time = time.time() - start_time
        if result == 0:
            if verbose:
                print(GREEN + f"Success: {ip_address} - Response time: {elapsed_time:.2f}s" + ENDC)
            return ip_address, True
        else:
            if verbose:
                print(RED + f"Failed: {ip_address} - Response time: {elapsed_time:.2f}s" + ENDC)
            return ip_address, False
    except socket.timeout:
        if verbose:
            print(RED + f"Timeout: {ip_address}" + ENDC)
        return ip_address, False
    except Exception as e:
        if verbose:
            print(RED + f"Error: {ip_address} - {str(e)}" + ENDC)
        return ip_address, False

def scan_ips(num_ips, timeout=2, verbose=False, cpu_amount=None):
    # Generate random IP addresses and scan them
    if cpu_amount:
        pool = multiprocessing.Pool(cpu_amount)
    else:
        pool = multiprocessing.Pool()
    ips = ['.'.join(str(random.randint(1, 255)) for _ in range(4)) for _ in range(num_ips)]
    results = [pool.apply_async(ping, (ip, timeout, verbose)) for ip in ips]
    pool.close()
    pool.join()

    # Collect results
    scanned_ips = [result.get() for result in results]
    return scanned_ips

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Web Scanner")
    parser.add_argument("--scan_amount", type=int, default=5, help="Number of IP addresses to scan")
    parser.add_argument("--timeout", type=float, default=2, help="Timeout for each ping request")
    parser.add_argument("--verbose", action="store_true", help="Print verbose output")
    parser.add_argument("--cpu_amount", type=int, default=None, help="Number of CPU cores to use in multiprocessing")
    args = parser.parse_args()

    num_ips_to_scan = args.scan_amount
    timeout = args.timeout
    verbose = args.verbose
    cpu_amount = args.cpu_amount

    print(f"Scanning {num_ips_to_scan} random IP addresses...")
    scanned_ips = scan_ips(num_ips_to_scan, timeout, verbose, cpu_amount)
    print("Scan complete. Results:")
    for ip, status in scanned_ips:
        status_str = GREEN + "Alive" + ENDC if status else RED + "Dead" + ENDC
        print(f"IP: {ip}, Status: {status_str}")
