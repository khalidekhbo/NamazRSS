import os
import time
import subprocess
import requests
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

# Verse & Hadith Metadata with Aayatun Deep Links
PRAYER_META = {
    "Fajr": {
        "emoji": "🌅",
        "link": "https://www.aayatun.com/11/114",
        "content": (
            "📖 Quran: \"Establish prayer at the two ends of the day and at the approach of the night.\" [Surah Hud 11:114]\n\n"
            "📜 Hadith: Prophet Muhammad (ﷺ) said: \"Whoever prays the Fajr prayer, he is under the protection of Allah.\" [Sahih Muslim 657]"
        )
    },
    "Sunrise": {
        "emoji": "☀️",
        "link": "https://sunnah.com/tirmidhi:586",
        "content": (
            
            "📜 Hadith: Prophet Muhammad (ﷺ) said: \"Whoever prays Fajr in congregation then sits remembering Allah until the sun rises, then prays two rak'ahs, will have a reward like that of Hajj and 'Umrah.\" [Jami' at-Tirmidhi 586]"
        )
    },
    "Dhuhr": {
        "emoji": "🌤️",
        "link": "https://sunnah.com/tirmidhi:161",
        "content": (
            
            "📜 Hadith: Prophet Muhammad (ﷺ) said: \"This is an hour in which the gates of the heavens are opened, and I like that a righteous deed of mine ascends during it.\" [Jami' at-Tirmidhi 161]"
        )
    },
    "Asr": {
        "emoji": "⛅",
        "link": "https://sunnah.com/bukhari:574",
        "content": (
            "📜 Hadith: Prophet Muhammad (ﷺ) said: \"Whoever prays the two cool prayers (Fajr and 'Asr) will enter Paradise.\" [Sahih al-Bukhari 574]"
        )
    },
    "Sunset": {
        "emoji": "🌇",
        "link": "https://www.aayatun.com/50/39",
        "content": (
            "📖 Quran: \"And glorify the praises of your Lord before the rising of the sun and before its setting.\" [Surah Qaf 50:39]"
        )
    },
    "Maghrib": {
        "emoji": "🌆",
        "link": "https://sunnah.com/abudawud:418",
        "content": (
            
            "📜 Hadith: Prophet Muhammad (ﷺ) said: \"My Ummah will continue to be upon goodness so long as they do not delay Maghrib until the stars intertwine.\" [Sunan Abi Dawud 418]"
        )
    },
    "Isha": {
        "emoji": "🌙",
        "link": "https://sunnah.com/bukhari:615",
        "content": (
           
            "📜 Hadith: Prophet Muhammad (ﷺ) said: \"If people knew what reward there is in the Isha and Fajr prayers, they would come to them even if they had to crawl.\" [Sahih al-Bukhari 615]"
        )
    },
    "Imsak": {
        "emoji": "🌌",
        "link": "https://www.aayatun.com/2/187",
        "content": (
            "📖 Quran: \"And eat and drink until the white thread of dawn becomes distinct to you from the black thread.\" [Surah Al-Baqarah 2:187]"
        )
    },
    "Midnight": {
        "emoji": "🌌",
        "link": "https://www.aayatun.com/73/2",
        "content": (
            "📖 Quran: \"Arise [to pray] the night, except for a little...\" [Surah Al-Muzzammil 73:2]\n\n"
            "📜 Hadith: Prophet Muhammad (ﷺ) said: \"The most beloved of prayer to Allah is the prayer of David (AS)... he would sleep half the night, stand in prayer for a third, and sleep for a sixth.\" [Sahih al-Bukhari 1131]"
        )
    },
    "Firstthird": {
        "emoji": "✨",
        "link": "https://www.aayatun.com/17/79",
        "content": (
            "📖 Quran: \"And from [part of] the night, pray with it as additional [worship] for you...\" [Surah Al-Isra 17:79]"
        )
    },
    "Lastthird": {
        "emoji": "🌟",
        "link": "https://www.aayatun.com/51/18",
        "content": (
            "📖 Quran: \"And in the hours before dawn they would ask forgiveness.\" [Surah Adh-Dhariyat 51:18]\n\n"
            "📜 Hadith: Prophet Muhammad (ﷺ) said: \"Our Lord descends every night to the lowest heaven during the last third of the night and says: Who is calling upon Me that I may answer him?\" [Sahih al-Bukhari 1145]"
        )
    }
}

BASE_SITE = "https://www.aayatun.com/"

def fetch_prayer_times():
    api_url = "http://api.aladhan.com/v1/timingsByCity"
    params = {
        "city": "Dhaka",
        "country": "Bangladesh",
        "method": 1,  # Karachi University
        "date": time.strftime("%Y-%m-%d")
    }

    response = requests.get(api_url, params=params)
    data = response.json()
    return data["data"]["timings"]

def convert_to_12_hour_format(time_24_hour):
    time_struct = time.strptime(time_24_hour.split(" ")[0], "%H:%M")
    return time.strftime("%I:%M %p", time_struct)

def prettify_xml(elem):
    rough_string = tostring(elem, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# --- 1. SIMPLE RSS FEED GENERATOR ---
def generate_simple_rss(prayer_timings, last_update_time):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    title = SubElement(channel, "title")
    title.text = "Namaz Times"

    link = SubElement(channel, "link")
    link.text = BASE_SITE

    description = SubElement(channel, "description")
    description.text = f"Daily Namaz timings for Dhaka. Updated: {last_update_time}"

    for prayer, raw_time in prayer_timings.items():
        time_12h = convert_to_12_hour_format(raw_time)
        meta = PRAYER_META.get(prayer, {"link": BASE_SITE})
        
        item = SubElement(channel, "item")
        
        item_title = SubElement(item, "title")
        item_title.text = f"{prayer}"

        item_link = SubElement(item, "link")
        item_link.text = meta["link"]

        item_desc = SubElement(item, "description")
        item_desc.text = f" Time : {time_12h}."

        item_guid = SubElement(item, "guid")
        item_guid.text = f"simple-namaz-{prayer.lower()}-{time.strftime('%Y-%m-%d')}"

    return prettify_xml(rss)

# --- 2. MODERN RSS FEED GENERATOR (STARIO OPTIMIZED) ---
def generate_modern_rss(prayer_timings, last_update_time):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    title = SubElement(channel, "title")
    title.text = "🕌 Namaz Times"

    link = SubElement(channel, "link")
    link.text = BASE_SITE

    description = SubElement(channel, "description")
    description.text = f"Daily prayer schedule. Updated: {last_update_time}"

    # Overview Widget Card
    summary_item = SubElement(channel, "item")
    summary_title = SubElement(summary_item, "title")
    summary_title.text = f"📅 Today's Timetable ({time.strftime('%b %d, %Y')})"
    
    summary_desc = SubElement(summary_item, "description")
    
    lines = []
    for prayer in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]:
        if prayer in prayer_timings:
            time_12h = convert_to_12_hour_format(prayer_timings[prayer])
            emoji = PRAYER_META.get(prayer, {}).get("emoji", "📌")
            lines.append(f"{emoji} {prayer:<8} • {time_12h}")
            
    summary_desc.text = "\n".join(lines)

    # Detailed Prayer Cards
    for prayer, raw_time in prayer_timings.items():
        time_12h = convert_to_12_hour_format(raw_time)
        meta = PRAYER_META.get(prayer, {"emoji": "📌", "link": BASE_SITE, "content": "Daily prayer time."})
        
        item = SubElement(channel, "item")
        
        item_title = SubElement(item, "title")
        item_title.text = f"{meta['emoji']} {prayer} — {time_12h}"

        item_link = SubElement(item, "link")
        item_link.text = meta["link"]

        item_desc = SubElement(item, "description")
        item_desc.text = meta["content"]

        item_guid = SubElement(item, "guid")
        item_guid.text = f"modern-namaz-{prayer.lower()}-{time.strftime('%Y-%m-%d')}"

    return prettify_xml(rss)

# Main Execution
prayer_times = fetch_prayer_times()
current_time_bdt = time.strftime("%Y-%m-%d %I:%M:%S %p", time.localtime())

# Generate XML content
simple_xml_content = generate_simple_rss(prayer_times, current_time_bdt)
modern_xml_content = generate_modern_rss(prayer_times, current_time_bdt)

# Write to output files
with open("rss_feed_simple.xml", "w", encoding="utf-8") as f:
    f.write(simple_xml_content)

with open("rss_feed.xml", "w", encoding="utf-8") as f:
    f.write(modern_xml_content)

# Git Commit Automation
subprocess.run(["git", "add", "rss_feed.xml", "rss_feed_simple.xml"])
subprocess.run(["git", "commit", "-m", f"Update Simple & Modern RSS Feeds - {current_time_bdt}"])

print("Both Simple (rss_feed_simple.xml) & Modern (rss_feed.xml) feeds created and committed!")
