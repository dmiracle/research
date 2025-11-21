import asyncio
import aiofeedparser

FEED_URL = "https://planetpython.org/rss20.xml"

async def main():
    async with aiofeedparser.ClientSession() as session:
        feed = await session.parse(FEED_URL)
        print(feed.feed.title)
        for entry in feed.entries[:3]:
            print("-", entry.title)

if __name__ == "__main__":
    asyncio.run(main())
