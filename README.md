# Wikipedia Graph Web

Finding the minimum degree of separation between any two Wikipedia articles using bidirectional BFS.

## What is this?

This project implements a bidirectional breadth-first search algorithm to find the shortest path between two Wikipedia articles. Each article is treated as a node, with hyperlinks acting as edges in the graph.

For research findings and results, see the `research/` folder.

## Usage

### Run the Bidirectional BFS

```bash
cd src
python bidirectional_bfs.py
```

Edit the bottom of `src/bidirectional_bfs.py` to change the source and target articles:

```python
thing1 = "Mac Pro"
thing2 = "Puff pastry"
find_degrees_of_relation_bidirectional(
    thing1, thing2,
    max_links=1800,
    num_threads=40,
    visualize=True,
    vistype="pyvis",
    auto_load=True
)
```

### Use the CLI

```bash
cd src
python wiki_cli.py summary "Python (programming language)"
python wiki_cli.py links "Machine learning" --max-links 20
```

## Project Structure

```
src/               # Main implementation
├── bidirectional_bfs.py    # Core algorithm
├── wiki_cli.py             # Command-line interface
└── visualizer/             # Network visualization

utils/             # Utility scripts
archive/           # Previous versions
research/          # Research data and findings
cache/             # Generated visualizations
```

## How it works

The algorithm uses bidirectional BFS starting from both articles simultaneously, meeting in the middle to find the shortest path. Results are visualized as an interactive network graph using PyVis.
