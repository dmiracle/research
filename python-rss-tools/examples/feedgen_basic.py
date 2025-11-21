from datetime import datetime
from feedgen.feed import FeedGenerator

if __name__ == "__main__":
    fg = FeedGenerator()
    fg.title("Example Feed")
    fg.link(href="https://example.com")
    fg.description("Demo RSS feed built with feedgen")

    entry = fg.add_entry()
    entry.id("urn:example:1")
    entry.title("Hello RSS")
    entry.link(href="https://example.com/hello")
    entry.published(datetime.utcnow())

    rss_str = fg.rss_str(pretty=True)
    print(rss_str.decode())
