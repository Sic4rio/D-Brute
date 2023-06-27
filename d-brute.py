import os
import sys
import argparse
import concurrent.futures
import requests
import time
from colorama import Fore, Style
import signal

# Disable the default KeyboardInterrupt behavior
signal.signal(signal.SIGINT, signal.SIG_IGN)

# Function to handle KeyboardInterrupt
def handle_interrupt(signum, frame):
    print(f"\n{Fore.RED}[{Fore.YELLOW}!{Fore.RED}]{Fore.WHITE} Exiting...")
    sys.exit(0)

# Register the KeyboardInterrupt handler
signal.signal(signal.SIGINT, handle_interrupt)

# Configuring color variables
YELLOW = Fore.YELLOW
CYAN = Fore.CYAN
RED = Fore.RED
GREEN = Fore.GREEN
MAGENTA = Fore.MAGENTA
BLUE = Fore.BLUE
WHITE = Fore.WHITE

screen = '''
 ██████╗ ██╗██████╗       ███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗
 ██╔══██╗██║██╔══██╗      ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║
 ██║  ██║██║██████╔╝█████╗███████╗█████╗  ███████║██████╔╝██║     ███████║
 ██║  ██║██║██╔══██╗╚════╝╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║
 ██████╔╝██║██║  ██║      ███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║
 ╚═════╝ ╚═╝╚═╝  ╚═╝      ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
                                                                           v1.3.3.7

  >> URL Brute-Force Tool
            			 >[By SICARI0]<
'''
print(f"{RED}{screen}{RED}")

# Parsing and handling arguments
parser = argparse.ArgumentParser()
parser.add_argument("--url", required=True, help="Enter a target URL.")
parser.add_argument("--wordlist", required=True, help="Select a wordlist.")
parser.add_argument("--status", required=False, nargs='+', help="Filter status codes.")
parser.add_argument("--threads", required=False, type=int, default=10, help="Number of threads.")
parser.add_argument("--output", required=False, action="store_true", help="Output to a file.")
parser.add_argument("--recursive", required=False, action="store_true", help="Enable recursive searching.")
args = parser.parse_args()

# Using the arguments
target_url = args.url
wordlist_path = args.wordlist
status_codes = args.status
thread_num = args.threads
output_to_file = args.output
recursive_search = args.recursive

# Checking if wordlist file exists
if not os.path.isfile(wordlist_path):
    print(f"{CYAN}[{RED}!{CYAN}]{WHITE} The specified wordlist file does not exist.")
    sys.exit(1)

# Read wordlist file
try:
    with open(wordlist_path, 'r', errors='replace') as f:
        wordlist = [line.strip() for line in f.readlines()]
except Exception as e:
    print(f"{CYAN}[{RED}!{CYAN}]{WHITE} Error reading wordlist file: {str(e)}")
    sys.exit(1)

# Outputs
print(f"{CYAN}[{RED}*{CYAN}]{WHITE} Target URL: {target_url}")
print(f"{CYAN}[{RED}*{CYAN}]{WHITE} Wordlist: {wordlist_path}")
print(f"{CYAN}[{RED}*{CYAN}]{WHITE} Status Codes: {', '.join(status_codes) if status_codes else 'All'}")
print(f"{CYAN}[{RED}*{CYAN}]{WHITE} Threads: {thread_num}")
print(f"{CYAN}[{RED}*{CYAN}]{WHITE} Output to File: {'Enabled' if output_to_file else 'Disabled'}")
print(f"{CYAN}[{RED}*{CYAN}]{WHITE} Recursive Search: {'Enabled' if recursive_search else 'Disabled'}\n")

# Checking if the output file already exists
output_file_path = "Found-Directories.txt"
file_number = 2
while os.path.isfile(output_file_path):
    output_file_path = f"Found-Directories{file_number}.txt"
    file_number += 1

# Set to keep track of visited URLs during recursive search
visited_urls = set()

# Define start time
start_time = time.time()

# Function to scan URLs recursively
def scanner(url, word_index, depth, success_urls, is_rescan=False):
    if depth > 3:
        return

    try:
        response = requests.get(url)
        status_code = str(response.status_code)

        if not status_codes or status_code in status_codes:
            if status_code.startswith('2'):
                # Check if the URL is a directory
                if response.headers.get('Content-Type') and response.headers.get('Content-Type').startswith(('text/html', 'application/json')):
                    success_urls.append(url)

                if is_rescan:
                    attempt_line = f"\rRe-scan {word_index+1}/{len(wordlist)} => {MAGENTA}{url}{WHITE}"
                else:
                    attempt_line = f"\rAttempt {word_index+1}/{len(wordlist)} => {BLUE}{url}{WHITE}"

                print(f"{attempt_line}{GREEN}")

                # Rescan successful URLs with appended wordlist if recursive_search is enabled
                if recursive_search:
                    new_wordlist = [new_word for new_word in wordlist[word_index+1:]]
                    for new_word in new_wordlist:
                        new_url = url + '/' + new_word
                        if new_url not in visited_urls:  # Check if URL is visited before
                            visited_urls.add(new_url)
                            scanner(new_url, word_index+1, depth+1, success_urls, is_rescan=True)

    except requests.exceptions.RequestException:
        pass

# Start scanning
success_urls = []
with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
    futures = []
    for i, word in enumerate(wordlist):
        url = target_url + '/' + word
        if url not in visited_urls:  # Check if URL is visited before
            visited_urls.add(url)
            future = executor.submit(scanner, url, i, 1, success_urls)
            futures.append(future)

    # Wait for all threads to complete
    for future in concurrent.futures.as_completed(futures):
        future.result()

# Print the found URLs
if success_urls:
    print(f"\n{CYAN}[{RED}*{CYAN}]{WHITE} Found Directories:")
    for url in success_urls:
        print(f"{GREEN}{url}{WHITE}")

    # Output to file if enabled
    if output_to_file:
        with open(output_file_path, 'w') as f:
            f.write("\n".join(success_urls))
        print(f"\n{CYAN}[{RED}*{CYAN}]{WHITE} Results saved to: {output_file_path}")
else:
    print(f"\n{CYAN}[{RED}!{CYAN}]{WHITE} No directories found.")

# Calculate and print the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"\n{CYAN}[{RED}*{CYAN}]{WHITE} Elapsed Time: {elapsed_time:.2f} seconds")
