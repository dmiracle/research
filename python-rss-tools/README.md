# Python RSS tooling roundup

A quick survey of Python RSS/Atom tools with runnable examples for parsing, aggregating, and generating feeds. Examples use simple "read top 3 items" semantics where applicable.

## Setup (using uv)
```bash
uv venv .venv
source .venv/bin/activate
uv pip install feedparser reader feedgen PyRSS2Gen podcastparser aiofeedparser
```

Run any example with `uv run python examples/<file>.py` from this directory.

## Tools

### feedparser — parse RSS/Atom quickly
- What it is: De facto standard parser for RSS/Atom, tolerant of feed quirks.
- Example: `examples/feedparser_basic.py` – fetch and list titles from Planet Python.
- Usage: synchronous parse of a URL or bytes; returns a dict-like object with `feed` metadata and `entries` list.

### reader — full-feed aggregator with storage
- What it is: Batteries-included reader/aggregator with SQLite storage, entry management, and plugins (entry dedupe, read-state, tags).
- Example: `examples/reader_basic.py` – create a SQLite DB, add a feed, update, and print three entries.
- Notes: Good when you need persistence and incremental updates instead of ad-hoc parsing.

### feedgen — generate RSS/Atom feeds programmatically
- What it is: High-level builder for RSS/Atom with helpers for enclosures, categories, and Atom extensions.
- Example: `examples/feedgen_basic.py` – build a small RSS feed and print XML.

### PyRSS2Gen — minimal RSS 2.0 generator
- What it is: Lightweight RSS 2.0 helper (no Atom) with straightforward object model.
- Example: `examples/rss2gen_basic.py` – build and emit an RSS document with a single item.
- When to use: Simple feeds with minimal dependencies; fewer conveniences than feedgen.

### podcastparser — podcast-centric RSS parser
- What it is: Focused parser that extracts podcast metadata, enclosures, durations, and episode data from podcast feeds.
- Example: `examples/podcastparser_basic.py` – parse a podcast feed from URL and print the first few episodes.

### aiofeedparser — async feed parsing
- What it is: Async wrapper around feedparser-style parsing with aiohttp-like client session for concurrent fetching.
- Example: `examples/aiofeedparser_basic.py` – asynchronously fetch and print the first three titles.

## Quick usage references
- Parse a feed (sync): `feedparser.parse(url)` → inspect `feed.entries`.
- Parse feeds with persistence: `reader.make_reader('reader.sqlite'); reader.add_feed(url); reader.update_feeds(); reader.get_entries(...)`.
- Generate RSS: use `feedgen.FeedGenerator()` or `PyRSS2Gen.RSS2(...)` then `rss_str()` / `to_xml()`.
- Async parse multiple feeds: create `aiofeedparser.ClientSession()` and `await session.parse(url)` per feed.

## Notes
- Examples use public feeds; swap URLs as needed.
- No tests were run; scripts are illustrative and minimal.
