# Research projects carried out by AI tools

Each directory in this repo is a separate research project carried out by an LLM tool - usually [Claude Code](https://www.claude.com/product/claude-code). Every single line of text and code was written by an LLM.

I try to include prompts and links to transcripts in [the PRs](https://github.com/simonw/research/pulls?q=is%3Apr+is%3Aclosed) that added each report, or in [the commits](https://github.com/simonw/research/commits/main/).

<!--[[[cog
import os
import subprocess
import pathlib
from datetime import datetime, timezone

# Model to use for generating summaries
MODEL = "github/gpt-4.1"

# Get all subdirectories with their first commit dates
research_dir = pathlib.Path.cwd()
subdirs_with_dates = []

for d in research_dir.iterdir():
    if d.is_dir() and not d.name.startswith('.'):
        # Get the date of the first commit that touched this directory
        try:
            result = subprocess.run(
                ['git', 'log', '--diff-filter=A', '--follow', '--format=%aI', '--reverse', '--', d.name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                # Parse first line (oldest commit)
                date_str = result.stdout.strip().split('\n')[0]
                commit_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                subdirs_with_dates.append((d.name, commit_date))
            else:
                # No git history, use directory modification time
                subdirs_with_dates.append((d.name, datetime.fromtimestamp(d.stat().st_mtime, tz=timezone.utc)))
        except Exception:
            # Fallback to directory modification time
            subdirs_with_dates.append((d.name, datetime.fromtimestamp(d.stat().st_mtime, tz=timezone.utc)))

# Print the heading with count
print(f"## {len(subdirs_with_dates)} research projects\n")

# Sort by date, most recent first
subdirs_with_dates.sort(key=lambda x: x[1], reverse=True)

for dirname, commit_date in subdirs_with_dates:
    folder_path = research_dir / dirname
    readme_path = folder_path / "README.md"
    summary_path = folder_path / "_summary.md"

    date_formatted = commit_date.strftime('%Y-%m-%d')

    # Get GitHub repo URL
    github_url = None
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0 and result.stdout.strip():
            origin = result.stdout.strip()
            # Convert SSH URL to HTTPS URL for GitHub
            if origin.startswith('git@github.com:'):
                origin = origin.replace('git@github.com:', 'https://github.com/')
            if origin.endswith('.git'):
                origin = origin[:-4]
            github_url = f"{origin}/tree/main/{dirname}"
    except Exception:
        pass

    if github_url:
        print(f"### [{dirname}]({github_url}) ({date_formatted})\n")
    else:
        print(f"### {dirname} ({date_formatted})\n")

    # Check if summary already exists
    if summary_path.exists():
        # Use cached summary
        with open(summary_path, 'r') as f:
            description = f.read().strip()
            if description:
                print(description)
            else:
                print("*No description available.*")
    elif readme_path.exists():
        # Generate new summary using llm command
        prompt = """Summarize this research project concisely. Write just 1 paragraph (3-5 sentences) followed by an optional short bullet list if there are key findings. Vary your opening - don't start with "This report" or "This research". Include 1-2 links to key tools/projects. Be specific but brief. No emoji."""
        result = subprocess.run(
            ['llm', '-m', MODEL, '-s', prompt],
            stdin=open(readme_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            error_msg = f"LLM command failed for {dirname} with return code {result.returncode}"
            if result.stderr:
                error_msg += f"\nStderr: {result.stderr}"
            raise RuntimeError(error_msg)
        if result.stdout.strip():
            description = result.stdout.strip()
            print(description)
            # Save to cache file
            with open(summary_path, 'w') as f:
                f.write(description + '\n')
        else:
            raise RuntimeError(f"LLM command returned no output for {dirname}")
    else:
        print("*No description available.*")

    print()  # Add blank line between entries

]]]-->
## 4 research projects

### [python-3d-modeling-libs](https://github.com/dmiracle/research/tree/main/python-3d-modeling-libs) (2025-11-24)

Python developers exploring 3D modeling have several standout libraries to choose from in 2024-2025. Open3D is ideal for rapid development in 3D data processing and machine learning, thanks to point cloud manipulation and cross-framework support. Trimesh excels at mesh analysis and manipulation with its lightweight design and robust file handling. Blender's Python API (bpy) unlocks the full power of Blender’s suite for procedural modeling, animation, and rendering, automating industry-standard workflows. Additional options like PyVista and CadQuery cater to scientific visualization and parametric CAD respectively.

Key findings:
- Open3D (https://www.open3d.org/) offers fast, flexible tools for 3D data and ML integration.
- Trimesh (https://trimsh.org/) specializes in mesh operations and file conversions.
- Blender's bpy (https://docs.blender.org/api/current/) provides unparalleled versatility for complete 3D creation and automation.
- PyVista and CadQuery are recommended for scientific and code-based CAD modeling tasks.

### [python-rss-tools](https://github.com/dmiracle/research/tree/main/python-rss-tools) (2025-11-21)

Surveying Python's RSS and Atom ecosystem reveals a variety of libraries covering parsing, aggregation, and feed generation, each catering to differing needs from simple synchronous parsing to full-featured, persistent aggregation and async operations. Tools like [feedparser](https://github.com/kurtmckee/feedparser) and [reader](https://github.com/lemon24/reader) respectively provide quick, tolerant parsing and persistent aggregation, while [feedgen](https://github.com/lkiesow/python-feedgen) and PyRSS2Gen streamline programmatic feed creation, varying in scope and convenience. Podcastparser targets podcast-specific metadata, and aiofeedparser supports async workflows for concurrent feed fetching. Usage examples demonstrate typical patterns, such as reading the top three items from a feed, highlighting simplicity and ease of integration.

**Key findings:**  
- feedparser is widely adopted for general feed parsing, excelling at handling malformed feeds.  
- reader offers persistent storage and incremental updates for robust aggregation needs.  
- feedgen and PyRSS2Gen are suited for feed generation, with feedgen supporting both Atom and RSS.  
- aiofeedparser enables async feed parsing, useful for batch or real-time applications.  
- podcastparser efficiently extracts detailed podcast metadata from RSS feeds.

### [python-rpc-alternatives](https://github.com/dmiracle/research/tree/main/python-rpc-alternatives) (2025-11-20)

Exploring practical Python RPC alternatives to REST and gRPC, this comparison emphasizes schema-driven, message-oriented, and dynamic approaches suited for modern Python environments. Key contenders include **Apache Thrift** (active, schema-first), **JSON-RPC** (lightweight, HTTP-native), and **RPyC** (Python-to-Python object remoting), with additional coverage of ZeroMQ (custom sockets), Cap'n Proto (zero-copy binary), Msgpack-RPC (binary, but stale), and SOAP (enterprise/legacy). Each tool is reviewed for strengths, weaknesses, recency of development, and ease of deployment, with runnable examples using [`uv`](https://github.com/astral-sh/uv) for environment management. For broader language coverage and high efficiency, [Apache Thrift](https://github.com/apache/thrift) stands out, while JSON-RPC and RPyC excel in lightweight or pure Python scenarios.

**Key findings:**
- Thrift and Cap'n Proto offer schema-first, polyglot RPC, suitable for scalable microservices.
- JSON-RPC provides frictionless HTTP APIs but lacks schema enforcement.
- RPyC facilitates seamless Python control channels, ideal for automation but not secure for public services.
- ZeroMQ and Cap'n Proto excel in performance, but require custom contract management.
- SOAP still serves in enterprise contexts requiring WSDL contracts despite verbosity.
- Msgpack-RPC has low activity and less community support compared to other options.

### [python-async-tools](https://github.com/dmiracle/research/tree/main/python-async-tools) (2025-11-19)

Python async libraries were benchmarked—`asyncio`, `trio`, and `anyio` (on Python 3.13)—using scenarios like task spawning, simulated I/O, and cancellation storms. `asyncio` led task churn and cancellation speed, while `trio` lagged on heavy spawn workloads but matched I/O latency and offered structured concurrency advantages. `anyio` performed between the two, matching `asyncio` on I/O and providing a unified task/group interface. All three libraries showed similar I/O latency under load, differing mainly in spawn and cancellation behavior. The full benchmarking code and results plots are available in the [python_async_tools repo](https://github.com/example/python_async_tools), and `anyio` itself offers a [cross-backend async API](https://anyio.readthedocs.io/).

Key findings:
- `asyncio` is fastest for raw task churn and bulk cancellation.
- `trio` offers robust structured concurrency, but with higher spawn overhead.
- `anyio` unifies APIs and matches `asyncio` on I/O when using its default backend.
- All libraries had similar p95 I/O latency under stress (≈15 ms).

<!--[[[end]]]-->

---

## Updating this README

This README uses [cogapp](https://nedbatchelder.com/code/cog/) to automatically generate project descriptions.

### Automatic updates

A GitHub Action automatically runs `cog -r -P README.md` on every push to main and commits any changes to the README or new `_summary.md` files.

### Manual updates

To update locally:

```bash
# Run cogapp to regenerate the project list
cog -r -P README.md
```

The script automatically:
- Discovers all subdirectories in this folder
- Gets the first commit date for each folder and sorts by most recent first
- For each folder, checks if a `_summary.md` file exists
- If the summary exists, it uses the cached version
- If not, it generates a new summary using `llm -m <!--[[[cog
print(MODEL, end='')
]]]-->
github/gpt-4.1
<!--[[[end]]]-->` with a prompt that creates engaging descriptions with bullets and links
- Creates markdown links to each project folder on GitHub
- New summaries are saved to `_summary.md` to avoid regenerating them on every run

To regenerate a specific project's description, delete its `_summary.md` file and run `cog -r -P README.md` again.
