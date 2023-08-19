import os

# Check if the rss_feed.xml file exists and delete it if it does
if os.path.exists("rss_feed.xml"):
    os.rename("rss_feed.xml", "old_rss_feed.xml")
    
    print("rss_feed.xml file renamed successfully")
else:
    print("rss_feed.xml file does not exist")

#  os.remove("rss_feed.xml")
   # print("rss_feed.xml file deleted successfully")
#else:
 #   print("rss_feed.xml file does not exist")
