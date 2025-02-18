import argparse
import csv
import re
import requests
from collections import Counter
from datetime import datetime

# Function to download the log file from the URL
def download_log(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to download the file from {url}")
        return None

# Function to process the log file
def process_log(file_contents):
    image_hits = 0
    total_hits = 0
    browsers = Counter()
    hour_hits = Counter()

    # Regular expressions
    image_pattern = re.compile(r'\.(jpg|gif|png)$', re.IGNORECASE)
    browser_patterns = {
        'Firefox': re.compile(r'Mozilla.*Firefox'),
        'Chrome': re.compile(r'Mozilla.*Chrome'),
        'Internet Explorer': re.compile(r'Mozilla.*MSIE'),
        'Safari': re.compile(r'Mozilla.*Safari'),
    }

    # Process the CSV file contents
    reader = csv.reader(file_contents.splitlines())
    for row in reader:
        if len(row) < 5:
            continue  # Skip invalid rows

        path = row[0]
        datetime_accessed = row[1]
        user_agent = row[2]
        status = row[3]
        file_size = row[4]

        total_hits += 1

        # Check if the request is for an image file
        if image_pattern.search(path):
            image_hits += 1

        # Count browser usage
        for browser, pattern in browser_patterns.items():
            if pattern.search(user_agent):
                browsers[browser] += 1
                break  # Only count the first match

        # Extract hour from datetime
        try:
            date_obj = datetime.strptime(datetime_accessed, "%m/%d/%Y %H:%M:%S")
            hour = date_obj.hour
            hour_hits[hour] += 1
        except ValueError:
            continue  # Skip invalid datetime formats

    return image_hits, total_hits, browsers, hour_hits

# Function to print statistics
def print_statistics(image_hits, total_hits, browsers, hour_hits):
    # Percentage of image requests
    if total_hits > 0:
        image_percentage = (image_hits / total_hits) * 100
        print(f"Image requests account for {image_percentage:.1f}% of all requests")
    
    # Most popular browser
    if browsers:
        most_popular_browser = browsers.most_common(1)[0]
        print(f"Most popular browser: {most_popular_browser[0]} with {most_popular_browser[1]} hits")
    
    # Hourly hit counts (Extra Credit)
    print("\nHourly Hit Counts:")
    for hour in sorted(hour_hits.keys()):
        print(f"Hour {hour:02d} has {hour_hits[hour]} hits")

# Main function to tie everything together
def main(url):
    print(f"Running main with URL = {url}...")
    
    # Step 1: Download the log file
    log_contents = download_log(url)
    if log_contents is None:
        return
    
    # Step 2: Process the log file
    image_hits, total_hits, browsers, hour_hits = process_log(log_contents)
    
    # Step 3: Print out statistics
    print_statistics(image_hits, total_hits, browsers, hour_hits)

if __name__ == "__main__":
    """Main entry point"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="URL to the datafile", type=str, required=True)
    args = parser.parse_args()
    main(args.url)
