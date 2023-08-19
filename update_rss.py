import requests
import time
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

while True:
    prayer_times = fetch_prayer_times()
    rss_feed = generate_rss_feed(prayer_times)

    # Print or save the updated RSS feed
    print(rss_feed)

    # Wait for a certain interval before updating again (e.g., 24 hours)
    time.sleep(24 * 60 * 60)
    description.text = f"Time: {time}"

    return tostring(rss)

while True:
    prayer_times = fetch_prayer_times()
    rss_feed = generate_rss_feed(prayer_times)

    # Print or save the updated RSS feed
    print(rss_feed)

    # Wait for a certain interval before updating again (e.g., 24 hours)
    time.sleep(24 * 60 * 60)
