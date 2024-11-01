import time
from datetime import datetime, timezone
from urllib.parse import urlparse
from browser_history.browsers import Firefox, Chrome, Brave, Edge

# Initialize each browser with its name
browsers = {
    "Firefox": Firefox(),
    "Chrome": Chrome(),
    "Brave": Brave(),
    "Edge": Edge()
}

# Function to fetch and filter new history entries based on a start time
def fetch_new_history(start_time):
    histories = []
    
    # Fetch history for each browser
    for browser_name, browser in browsers.items():
        try:
            # Attempt to fetch history
            history = browser.fetch_history().histories
            # Filter entries that are newer than the start time
            new_entries = [
                (
                    browser_name.lower(),  # Browser name in lowercase
                    timestamp.strftime('%Y-%m-%d'),  # Date in YYYY-MM-DD format
                    timestamp.strftime('%H:%M:%S'),  # Time in HH:MM:SS format
                    urlparse(url).netloc  # Extract domain only from URL
                )
                for (timestamp, url, *_) in history if timestamp > start_time
            ]
            histories.extend(new_entries)
        except Exception as e:
            # Ignore the exception if it's a "browser not installed" issue
            if "not installed" in str(e).lower():
                continue
            else:
                print(f"Error fetching history from {browser_name}: {e}")
    
    return histories

# Set the initial start time with timezone info (UTC)
start_time = datetime.now(timezone.utc)

# Start monitoring for new history entries
try:
    print("Monitoring live browsing history...")
    while True:
        # Fetch new entries since last check
        new_history = fetch_new_history(start_time)
        
        # If there are new entries, print them and update start_time
        if new_history:
            for entry in new_history:
                print(entry)  # Each entry is now (browser, YYYY-MM-DD, HH:MM:SS, domain)
            # Update the start time to the latest fetched entry
            start_time = max(datetime.strptime(f"{entry[1]} {entry[2]}", '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc) for entry in new_history)
        
        # Wait before checking again
        time.sleep(5)  # Check every 5 seconds

except KeyboardInterrupt:
    print("Stopped monitoring live browsing history.")
