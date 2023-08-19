import requests
import time
import subprocess
from xml.etree.ElementTree import Element, SubElement, tostring

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

def generate_rss_feed(prayer_timings):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    title = SubElement(channel, "title")
    title.text = "Namaz Time"

    description = SubElement(channel, "description")
    description.text = "Stay updated with daily Namaz timings."

    for prayer, time in prayer_timings.items():
        item = SubElement(channel, "item")
        title = SubElement(item, "title")
        title.text = prayer

        description = SubElement(item, "description")
        description.text = f"Time: {time}"

    return tostring(rss)


prayer_times = fetch_prayer_times()
rss_feed = generate_rss_feed(prayer_times)
    #Convert the bytes content to a file
rss_feed_str = rss_feed.decode("utf-8")

# Check if the rss_feed.xml file exists
if os.path.exists("rss_feed.xml"):
    # Clear the old content and write new data
    with open("rss_feed.xml", "w") as rss_file:
        rss_file.write(rss_feed_str)
else:
    # Create a new file and write data
    with open("rss_feed.xml", "w") as rss_file:
        rss_file.write(rss_feed_str)
    # Print or save the updated RSS feed
   # print(rss_feed)
    # File Export - the updated RSS feed


subprocess.run(["git","add","rss_feed.xml"])

subprocess.run(["git","commit","-m","Update RSS Feed"])
print("RSS feed updated and committed successfully")

    # Wait for a certain interval before updating again (e.g., 24 hours)
    #time.sleep(24 * 60 * 60)
   
