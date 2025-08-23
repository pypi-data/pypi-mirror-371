# Sublime 🍋‍🟩

Smart sub-line segmented embeddings that leave you feeling *sublime*.

Sublime offers two uniquely powerful features:
1. **Line-by-line embeddings** segmented as-needed to get exactly the code snippets required, nothing more or less
2. **Negative prompting** - just like image generation, searching over embeddings should include negative prompts

## How it works

Instead of chunking code arbitrarily, Sublime embeds every line of code individually. When you search, it uses ML clustering (similar to audio segmentation) to group nearby high-scoring lines into coherent code segments that target exactly what you've searched for.

## Quick Start

```python
from embedings import Embeddings

# Index your codebase
emb = Embeddings("./my_project")

# Search with semantic queries
results = emb.search("user authentication and login validation flow", top_n=1)

# Search with negative prompting to exclude unwanted patterns
results = emb.search("database connection and query execution", negative_query="test mocks and unit testing", top_n=1)

# Negative-only search to find problematic code
results = emb.search(negative_query="clean well-documented modern code", top_n=1)

# Print results
for result in results:
    print(f"File: {result.file_path}")
    print(f"Lines {result.start_line}-{result.end_line}")
    print(result)
```

## Output format

Search returns a list of CodeSection objects, globally ranked by similarity:
- file_path: path to the source file
- start_line, end_line: inclusive span of the snippet
- lines: the exact lines in the span
- avg_similarity, max_similarity: scores in [0, 1] (higher is more relevant)

Printing a CodeSection (via print(result)) renders:

```text
File: path/to/file.py (lines 120-134)
  120: def authenticate(user, password):
  121:     # ... code ...
  122:     return is_valid
  123: 
  124: class Session:
  125:     # ...
```

## Usage Notes

- Use from Python by importing `Embeddings`.
- Control file types with `supported_extensions` and ignores with an `.embedignore` file.
- `top_n` returns the best segments globally across all files.

## File watching (optional)

Keep the index up to date while you edit files.

```python
import asyncio
from embedings import EmbeddingsSuite

async def main():
    suite = EmbeddingsSuite("./project", ignore_file=".embedignore")
    await suite.build_initial_index()
    await suite.start_watching()

    # ... use suite.search_code(query, negative_query, top_n) as you work ...

    await suite.stop_watching()

asyncio.run(main())
```

Notes:
- Respects `.embedignore` patterns
- Debounced ~1s, then rebuilds index on change
- Safe to run while developing; searches use the latest index

## Configuration

```python
# Custom file types and ignore patterns
emb = Embeddings(
    "./project",
    supported_extensions={".py", ".js", ".rs"}, 
    ignore_file=".embedignore"
)
```

Create `.embedignore` file:
```
node_modules
*.log
test_*
__pycache__
```

## Install

```bash
pip install -r requirements.txt
```