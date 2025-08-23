"""
NetworkX to Interactive HTML Converter

A Python package to convert NetworkX graphs into interactive HTML visualizations
with dynamic property viewing for nodes and edges.

Author: NetworkX HTML Viewer Team
License: MIT
"""

import networkx as nx
import json
import os
from typing import Dict, Any
import pkg_resources
from pathlib import Path
import colorsys


class NetworkXHTMLConverter:
    """
    Converts NetworkX graphs to interactive HTML visualizations.

    Features:
    - Interactive node and edge visualization
    - Dynamic property display on hover/click
    - Customizable styling
    - Force-directed layout using D3.js
    - Zoom and pan capabilities
    - Professional UI with sidebar property viewer
    """

    def __init__(self, width: int = 1200, height: int = 800):
        """
        Initialize the converter.

        Args:
            width: Canvas width in pixels (default: 1200)
            height: Canvas height in pixels (default: 800)
        """
        self.width = width
        self.height = height
        self.color_property = None
        self.color_mapping = None
        self._load_template()

    def _load_template(self):
        """Load the HTML template from the package."""
        try:
            # Try to load from package resources
            template_path = pkg_resources.resource_filename(
                'netx_vis', 'templates/graph_template.html'
            )
            with open(template_path, 'r', encoding='utf-8') as f:
                self.template = f.read()
        except:
            # Fallback: load from relative path
            current_dir = Path(__file__).parent
            template_path = current_dir / 'templates' / 'graph_template.html'
            with open(template_path, 'r', encoding='utf-8') as f:
                self.template = f.read()

    def apply_color_by_property(self, G: nx.Graph, property_name: str):
        """
        Apply colors to nodes based on property values.
        
        Args:
            G: NetworkX graph
            property_name: Name of the node property to color by
        """
        # Get unique values for the property
        property_values = set()
        for _, node_data in G.nodes(data=True):
            if property_name in node_data:
                property_values.add(str(node_data[property_name]))
        
        # Generate color palette
        colors = self._generate_color_palette(len(property_values))
        value_to_color = dict(zip(sorted(property_values), colors))
        
        # Store the color mapping and property name for the legend
        self.color_property = property_name
        self.color_mapping = value_to_color
        
        # Apply colors to nodes
        for node_id, node_data in G.nodes(data=True):
            if property_name in node_data:
                value = str(node_data[property_name])
                node_data['color'] = value_to_color[value]
            else:
                node_data['color'] = '#cccccc'  # Default gray for missing values

    def _generate_color_palette(self, num_colors: int):
        """Generate a distinct color palette using HSV."""
        colors = []
        for i in range(num_colors):
            hue = i / num_colors
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
            )
            colors.append(hex_color)
        return colors

    def _extract_graph_data(self, G: nx.Graph) -> Dict[str, Any]:
        """
        Extract nodes and edges data from NetworkX graph.

        Args:
            G: NetworkX graph

        Returns:
            Dictionary containing nodes and edges data
        """
        # Extract nodes with all their properties
        nodes = []
        for node_id, node_data in G.nodes(data=True):
            node_info = {
                'id': str(node_id),
                'label': str(node_data.get('label', node_id)),
                'properties': dict(node_data)
            }
            nodes.append(node_info)

        # Extract edges with all their properties
        edges = []
        for source, target, edge_data in G.edges(data=True):
            edge_info = {
                'source': str(source),
                'target': str(target),
                'properties': dict(edge_data)
            }
            edges.append(edge_info)


        graph_properties = {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "is_directed": G.is_directed()
            }

        return {
            'nodes': nodes,
            'edges': edges,
            'directed': G.is_directed(),
            'graph_properties': graph_properties
        }

    def _format_properties(self, properties: Dict[str, Any]) -> str:
        """Format properties dictionary as HTML."""
        if not properties:
            return "<div class='property-item'>No properties</div>"

        html = ""
        for key, value in properties.items():
            display_value = json.dumps(value) if not isinstance(value, str) else value
            html += f"""
            <div class='property-item'>
                <span class='property-key'>{key}:</span>
                <span class='property-value'>{display_value}</span>
            </div>
            """
        return html

    def convert(self, G: nx.Graph, output_file: str = "graph_visualization.html",
                title: str = "NetworkX Graph Visualization") -> str:
        """
        Convert NetworkX graph to interactive HTML visualization.

        Args:
            G: NetworkX graph to convert
            output_file: Output HTML file path
            title: HTML page title

        Returns:
            Path to the generated HTML file
        """
        # Extract graph data
        graph_data = self._extract_graph_data(G)

        # Format template variables
        template_vars = {
            'TITLE': title,
            'WIDTH': self.width,
            'HEIGHT': self.height,
            'NODE_COUNT': len(graph_data['nodes']),
            'EDGE_COUNT': len(graph_data['edges']),
            'GRAPH_TYPE': 'Directed' if graph_data['directed'] else 'Undirected',
            'GRAPH_DATA': json.dumps(graph_data, indent=2, default=serialize_for_json),
            'GRAPH_PROPERTIES': self._format_properties(graph_data.get('graph_properties', {})),
            'COLOR_PROPERTY': json.dumps(self.color_property) if self.color_property else 'null',
            'COLOR_MAPPING': json.dumps(self.color_mapping) if self.color_mapping else 'null'
        }

        # Replace template variables
        html_content = self.template
        for key, value in template_vars.items():
            html_content = html_content.replace(f'{{{{{key}}}}}', str(value))

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return os.path.abspath(output_file)

    def preview(self, G: nx.Graph, title: str = "NetworkX Graph Visualization") -> str:
        """
        Generate HTML content for preview without saving to file.

        Args:
            G: NetworkX graph to convert
            title: HTML page title

        Returns:
            HTML content string
        """
        graph_data = self._extract_graph_data(G)

        template_vars = {
            'TITLE': title,
            'WIDTH': self.width,
            'HEIGHT': self.height,
            'NODE_COUNT': len(graph_data['nodes']),
            'EDGE_COUNT': len(graph_data['edges']),
            'GRAPH_TYPE': 'Directed' if graph_data['directed'] else 'Undirected',
            'GRAPH_DATA': json.dumps(graph_data, indent=2, default=serialize_for_json),
            'GRAPH_PROPERTIES': self._format_properties(graph_data.get('graph_properties', {})),
            'COLOR_PROPERTY': json.dumps(self.color_property) if self.color_property else 'null',
            'COLOR_MAPPING': json.dumps(self.color_mapping) if self.color_mapping else 'null'
        }

        html_content = self.template
        for key, value in template_vars.items():
            html_content = html_content.replace(f'{{{{{key}}}}}', str(value))

        return html_content


# Convenience functions
def convert_networkx_to_html(graph: nx.Graph, output_file: str = "graph.html",
                             title: str = "Graph Visualization",
                             width: int = 1200, height: int = 800,
                             color_by_property: str = None) -> str:
    """
    Convenience function to convert NetworkX graph to HTML.

    Args:
        graph: NetworkX graph
        output_file: Output file path
        title: Page title
        width: Canvas width
        height: Canvas height
        color_by_property: Node property name to color nodes by (same values get same colors)

    Returns:
        Path to generated HTML file
    """
    converter = NetworkXHTMLConverter(width, height)
    if color_by_property:
        converter.apply_color_by_property(graph, color_by_property)
    return converter.convert(graph, output_file, title)


def preview_networkx_graph(graph: nx.Graph, title: str = "Graph Visualization",
                           width: int = 1200, height: int = 800) -> str:
    """
    Convenience function to generate HTML preview of NetworkX graph.

    Args:
        graph: NetworkX graph
        title: Page title
        width: Canvas width
        height: Canvas height

    Returns:
        HTML content string
    """
    converter = NetworkXHTMLConverter(width, height)
    return converter.preview(graph, title)


def serialize_for_json(obj):
    """Custom JSON serializer to handle Python objects that are not JSON serializable"""
    if obj is None:
        return None
    elif isinstance(obj, set):
        return list(obj)
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    else:
        return obj