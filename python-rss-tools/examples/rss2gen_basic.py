import datetime
import PyRSS2Gen

if __name__ == "__main__":
    rss = PyRSS2Gen.RSS2(
        title="Example RSS",
        link="https://example.com",
        description="Built with PyRSS2Gen",
        lastBuildDate=datetime.datetime.utcnow(),
        items=[
            PyRSS2Gen.RSSItem(
                title="Hello RSS",
                link="https://example.com/hello",
                guid=PyRSS2Gen.Guid("urn:example:1"),
                pubDate=datetime.datetime.utcnow(),
            )
        ],
    )

    print(rss.to_xml(encoding="utf-8"))
