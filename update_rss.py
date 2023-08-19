import requests
import time
import subprocess
from xml.etree.ElementTree import Element, SubElement, tostring
import os

def fetch_prayer_times():
    api_url = "http://api.aladhan.com/v1/timingsByCity"

    params = {
        "city": "Dhaka",
        "country": "Bangladesh",
        "method": 1,  # Calculation method for Karachi University
        "date": time.strftime("%Y-%m-%d")  # Current date
    }

    response = requests.get(api_url, params=params)
    data = response.json()
    timings = data["data"]["timings"]

    return timings

def generate_rss_feed(prayer_timings, last_update_time):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    title = SubElement(channel, "title")
    title.text = "Namaz Time"

    description = SubElement(channel, "description")
    description.text = f"Stay updated with daily Namaz timings. Last updated at {last_update_time} (BDT)."

    for prayer, time in prayer_timings.items():
        item = SubElement(channel, "item")
        title = SubElement(item, "title")
        title.text = prayer

        description = SubElement(item, "description")
        description.text = f"Time: {time}"

    return tostring(rss)

# Check if the rss_feed.xml file exists and rename it if it does
if os.path.exists("rss_feed.xml"):
    os.rename("rss_feed.xml", "old_rss_feed.xml")
    print("rss_feed.xml file renamed to old_rss_feed.xml")
else:
    print("rss_feed.xml file does not exist")

# Fetch prayer times
prayer_times = fetch_prayer_times()
current_time_bd = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 6 * 3600))  # Adding 6 hours for BDT
rss_feed = generate_rss_feed(prayer_times, current_time_bd)

# Convert the bytes content to a file
rss_feed_str = rss_feed.decode("utf-8")

# Write the updated RSS feed to a new file
with open("rss_feed.xml", "w") as rss_file:
    rss_file.write(rss_feed_str)

# Add the new file and commit the changes
subprocess.run(["git", "add", "rss_feed.xml"])
subprocess.run(["git", "commit", "-m", "Update RSS Feed"])

print("RSS feed updated and committed successfully")
