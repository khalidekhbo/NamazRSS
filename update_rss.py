import requests
import time
import subprocess
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import sys

# Configuration
CONFIG = {
    "city": "Dhaka",
    "country": "Bangladesh",
    "method": 1,
    "timezone": "Asia/Dhaka",
    "api_url": "http://api.aladhan.com/v1/timingsByCity",
    "output_file": "rss_feed.xml",
    "backup_file": "old_rss_feed.xml",
}

def fetch_prayer_times():
    """Fetch prayer times from Aladhan API with error handling."""
    params = {
        "city": CONFIG["city"],
        "country": CONFIG["country"],
        "method": CONFIG["method"],
        "date": time.strftime("%Y-%m-%d")
    }
    
    try:
        response = requests.get(CONFIG["api_url"], params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "data" not in data or "timings" not in data["data"]:
            raise ValueError("Unexpected API response format")
        return data["data"]["timings"]
    except requests.RequestException as e:
        print(f"Error fetching prayer times: {e}", file=sys.stderr)
        raise
    except (ValueError, KeyError) as e:
        print(f"Error parsing prayer times: {e}", file=sys.stderr)
        raise

def convert_to_12_hour_format(time_24_hour):
    """Convert 24-hour format to 12-hour format."""
    try:
        time_struct = time.strptime(time_24_hour, "%H:%M")
        return time.strftime("%I:%M %p", time_struct)
    except ValueError as e:
        print(f"Error converting time format: {e}", file=sys.stderr)
        raise

def get_current_time_bdt():
    """Get current time in Bangladesh timezone."""
    tz = ZoneInfo(CONFIG["timezone"])
    return datetime.now(tz).strftime("%Y-%m-%d %I:%M:%S %p")

def prettify_xml(elem):
    """Return a pretty-printed XML string."""
    rough_string = tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def generate_rss_feed(prayer_timings, last_update_time):
    """Generate RSS feed with prayer timings."""
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    
    title = SubElement(channel, "title")
    title.text = "Namaz Time"
    
    description = SubElement(channel, "description")
    description.text = f"Stay updated with daily Namaz timings. Last updated at {last_update_time} ({CONFIG['timezone']})."
    
    # Add the last update time as the top item
    top_item = SubElement(channel, "item")
    top_title = SubElement(top_item, "title")
    top_title.text = "Last Update Time"
    top_description = SubElement(top_item, "description")
    top_description.text = f"Time: {last_update_time}"
    
    for prayer, prayer_time in prayer_timings.items():
        item = SubElement(channel, "item")
        title = SubElement(item, "title")
        title.text = prayer
        
        description = SubElement(item, "description")
        description.text = f"Time: {convert_to_12_hour_format(prayer_time)}"
    
    return prettify_xml(rss)

def update_rss_feed():
    """Main function to update RSS feed."""
    try:
        # Backup existing file
        if os.path.exists(CONFIG["output_file"]):
            try:
                os.rename(CONFIG["output_file"], CONFIG["backup_file"])
                print(f"{CONFIG['output_file']} backed up to {CONFIG['backup_file']}")
            except OSError as e:
                print(f"Warning: Could not backup file: {e}", file=sys.stderr)
        
        # Fetch prayer times
        prayer_times = fetch_prayer_times()
        current_time_bd = get_current_time_bdt()
        rss_feed = generate_rss_feed(prayer_times, current_time_bd)
        
        # Write RSS feed
        with open(CONFIG["output_file"], "w", encoding="utf-8") as rss_file:
            rss_file.write(rss_feed)
        print(f"RSS feed written to {CONFIG['output_file']}")
        
        # Commit changes
        try:
            subprocess.run(["git", "add", CONFIG["output_file"]], check=True, capture_output=True)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            subprocess.run(
                ["git", "commit", "-m", f"Update RSS Feed - {timestamp}"],
                check=True,
                capture_output=True
            )
            print("Changes committed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Git error: {e.stderr.decode('utf-8')}", file=sys.stderr)
            raise
        except FileNotFoundError:
            print("Error: git command not found", file=sys.stderr)
            raise
    
    except Exception as e:
        print(f"Failed to update RSS feed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    update_rss_feed()
