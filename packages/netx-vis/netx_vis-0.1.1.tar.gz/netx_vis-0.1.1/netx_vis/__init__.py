"""
NetworkX HTML Viewer

A Python package to convert NetworkX graphs into beautiful, interactive HTML visualizations
with dynamic property viewing for nodes and edges.

Features:
- Interactive graph visualization using D3.js
- Click nodes/edges to view all properties in a sidebar
- Zoom, pan, and drag functionality
- Professional UI with modern styling
- Support for all NetworkX graph types
- Easy to use - just pass your NetworkX graph!

Quick Start:
    >>> import networkx as nx
    >>> from networkx_html_viewer import convert_networkx_to_html
    >>> 
    >>> # Create a sample graph
    >>> G = nx.Graph()
    >>> G.add_node("A", label="Node A", type="important", value=100)
    >>> G.add_edge("A", "B", weight=0.8, relation="strong")
    >>> 
    >>> # Convert to interactive HTML
    >>> html_file = convert_networkx_to_html(G, "my_graph.html", "My Network")
    >>> print(f"Graph saved to: {html_file}")

Author: Olsi
License: MIT
Version: 0.1.1
"""

from .converter import (
    NetworkXHTMLConverter,
    convert_networkx_to_html,
    preview_networkx_graph
)

__version__ = "0.1.1"
__author__ = "Olsi"
__license__ = "MIT"

__all__ = [
    "NetworkXHTMLConverter",
    "convert_networkx_to_html", 
    "preview_networkx_graph"
]