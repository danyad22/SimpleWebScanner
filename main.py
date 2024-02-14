import random
import multiprocessing
import socket
import time
import argparse
from colorama import Fore, Style, init

# Initialize colorama
init()

def ping(ip_address, timeout=2, verbose=False):
    try:
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip_address, 80))
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        if result == 0:
            if verbose:
                print(Fore.GREEN + f"Success: {ip_address} - Response time: {elapsed_time:.2f}ms" + Style.RESET_ALL)
            return ip_address, True, elapsed_time
        else:
            if verbose:
                print(Fore.RED + f"Failed: {ip_address} - Response time: {elapsed_time:.2f}ms" + Style.RESET_ALL)
            return ip_address, False, elapsed_time
    except socket.timeout:
        if verbose:
            print(Fore.RED + f"Timeout: {ip_address}" + Style.RESET_ALL)
        return ip_address, False, timeout * 1000  # Return timeout in milliseconds
    except Exception as e:
        if verbose:
            print(Fore.RED + f"Error: {ip_address} - {str(e)}" + Style.RESET_ALL)
        return ip_address, False, 0  # Return 0 ms for errors

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

    # Collect results and sort by status (dead IPs first)
    scanned_ips = [result.get() for result in results]
    scanned_ips.sort(key=lambda x: (x[1], x[0]))  # Sort by status (dead IPs first) then IP address
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
    for ip, status, response_time in scanned_ips:
        status_str = Fore.GREEN + "Alive" + Style.RESET_ALL if status else Fore.RED + "Dead" + Style.RESET_ALL
        print(f"IP: {ip}, Status: {status_str}, Response Time: {response_time:.2f}ms")
