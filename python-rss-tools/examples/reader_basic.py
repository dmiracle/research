from reader import make_reader

FEED_URL = "https://planetpython.org/rss20.xml"
DB_PATH = "reader.sqlite"

if __name__ == "__main__":
    reader = make_reader(DB_PATH)
    reader.add_feed(FEED_URL)
    reader.update_feeds()  # fetch latest entries

    for entry in reader.get_entries(feed=FEED_URL, limit=3):
        print(entry.title)
