"""
Unit tests for NetworkX HTML Viewer package.
"""

import unittest
import tempfile
import os
import networkx as nx
from netx_vis import (
    NetworkXHTMLConverter,
    convert_networkx_to_html,
    preview_networkx_graph
)


class TestNetworkXHTMLConverter(unittest.TestCase):
    """Test cases for NetworkXHTMLConverter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.converter = NetworkXHTMLConverter()
        self.temp_dir = tempfile.mkdtemp()

        # Create a sample graph
        self.graph = nx.Graph()
        self.graph.add_node("A", label="Node A", value=100, type="important")
        self.graph.add_node("B", label="Node B", value=50, type="normal")
        self.graph.add_edge("A", "B", weight=0.8, relation="strong")
        self.graph.graph['name'] = 'Test Graph'

    def test_converter_initialization(self):
        """Test converter initialization with default and custom parameters."""
        # Test default initialization
        converter = NetworkXHTMLConverter()
        self.assertEqual(converter.width, 1200)
        self.assertEqual(converter.height, 800)

        # Test custom initialization
        converter = NetworkXHTMLConverter(width=1600, height=1000)
        self.assertEqual(converter.width, 1600)
        self.assertEqual(converter.height, 1000)

    def test_extract_graph_data(self):
        """Test graph data extraction."""
        graph_data = self.converter._extract_graph_data(self.graph)

        # Test structure
        self.assertIn('nodes', graph_data)
        self.assertIn('edges', graph_data)
        self.assertIn('directed', graph_data)
        self.assertIn('graph_properties', graph_data)

        # Test node data
        self.assertEqual(len(graph_data['nodes']), 2)
        node_a = next(n for n in graph_data['nodes'] if n['id'] == 'A')
        self.assertEqual(node_a['label'], 'Node A')
        self.assertEqual(node_a['properties']['value'], 100)

        # Test edge data
        self.assertEqual(len(graph_data['edges']), 1)
        edge = graph_data['edges'][0]
        self.assertEqual(edge['source'], 'A')
        self.assertEqual(edge['target'], 'B')
        self.assertEqual(edge['properties']['weight'], 0.8)

        # Test graph properties
        self.assertEqual(graph_data['graph_properties']['name'], 'Test Graph')
        self.assertFalse(graph_data['directed'])

    def test_convert_to_file(self):
        """Test converting graph to HTML file."""
        output_file = os.path.join(self.temp_dir, "test_graph.html")

        result_file = self.converter.convert(
            self.graph,
            output_file,
            "Test Graph Visualization"
        )

        # Test file creation
        self.assertTrue(os.path.exists(result_file))
        self.assertEqual(os.path.abspath(output_file), result_file)

        # Test file content
        with open(result_file, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("Test Graph Visualization", content)
        self.assertIn("Node A", content)
        self.assertIn("Node B", content)
        self.assertIn('"weight": 0.8', content)
        self.assertIn('d3.select', content)  # Check D3.js integration

    def test_preview_html(self):
        """Test generating HTML preview without file."""
        html_content = self.converter.preview(self.graph, "Preview Test")

        # Test content structure
        self.assertIsInstance(html_content, str)
        self.assertIn("<!DOCTYPE html>", html_content)
        self.assertIn("Preview Test", html_content)
        self.assertIn("Node A", html_content)
        self.assertIn("Node B", html_content)
        self.assertIn('"weight": 0.8', html_content)

    def test_directed_graph(self):
        """Test with directed graph."""
        directed_graph = nx.DiGraph()
        directed_graph.add_edge("X", "Y", weight=1.0)

        graph_data = self.converter._extract_graph_data(directed_graph)
        self.assertTrue(graph_data['directed'])

        html_content = self.converter.preview(directed_graph)
        self.assertIn("Directed", html_content)

    def test_empty_graph(self):
        """Test with empty graph."""
        empty_graph = nx.Graph()

        graph_data = self.converter._extract_graph_data(empty_graph)
        self.assertEqual(len(graph_data['nodes']), 0)
        self.assertEqual(len(graph_data['edges']), 0)

        html_content = self.converter.preview(empty_graph)
        self.assertIn("<!DOCTYPE html>", html_content)

    def test_large_graph(self):
        """Test with larger graph."""
        large_graph = nx.karate_club_graph()

        # Add some properties
        for node in large_graph.nodes():
            large_graph.nodes[node]['degree'] = large_graph.degree(node)

        graph_data = self.converter._extract_graph_data(large_graph)
        self.assertEqual(len(graph_data['nodes']), 34)
        self.assertEqual(len(graph_data['edges']), 78)

        html_content = self.converter.preview(large_graph)
        self.assertIn("34", html_content)  # Node count
        self.assertIn("78", html_content)  # Edge count


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.graph = nx.Graph()
        self.graph.add_node("A", value=1)
        self.graph.add_node("B", value=2)
        self.graph.add_edge("A", "B", weight=0.5)

    def test_convert_networkx_to_html_function(self):
        """Test convert_networkx_to_html convenience function."""
        output_file = os.path.join(self.temp_dir, "convenience_test.html")

        result_file = convert_networkx_to_html(
            self.graph,
            output_file,
            "Convenience Test",
            width=800,
            height=600
        )

        print(result_file)

        self.assertTrue(os.path.exists(result_file))

        with open(result_file, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("Convenience Test", content)
        self.assertIn("800", content)  # Width
        self.assertIn("600", content)  # Height

    def test_convert_networkx_to_html_current_directory(self):
        """Test convert_networkx_to_html saves to current directory when only filename provided."""
        output_file = "test_current_dir.html"
        
        result_file = convert_networkx_to_html(
            self.graph,
            output_file,
            "Current Directory Test"
        )
        
        # Should save in current working directory
        expected_path = os.path.abspath(output_file)
        self.assertEqual(result_file, expected_path)
        self.assertTrue(os.path.exists(result_file))
        
        # Clean up
        if os.path.exists(result_file):
            os.remove(result_file)

    def test_preview_networkx_graph_function(self):
        """Test preview_networkx_graph convenience function."""
        html_content = preview_networkx_graph(
            self.graph,
            "Preview Function Test",
            width=1000,
            height=700
        )

        self.assertIsInstance(html_content, str)
        self.assertIn("Preview Function Test", html_content)
        self.assertIn("1000", html_content)  # Width
        self.assertIn("700", html_content)  # Height


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_node_with_complex_properties(self):
        """Test nodes with complex property types."""
        graph = nx.Graph()
        graph.add_node("complex",
                       nested_dict={"a": 1, "b": [1, 2, 3]},
                       list_prop=[1, 2, 3, 4],
                       none_prop=None,
                       bool_prop=True)

        converter = NetworkXHTMLConverter()
        graph_data = converter._extract_graph_data(graph)

        node = graph_data['nodes'][0]
        self.assertIn('nested_dict', node['properties'])
        self.assertIn('list_prop', node['properties'])
        self.assertIn('none_prop', node['properties'])
        self.assertIn('bool_prop', node['properties'])

    @unittest.skip("Currently this one is not properly set, will be fixed in the future")
    def test_unicode_properties(self):
        """Test handling of unicode characters in properties."""
        graph = nx.Graph()
        graph.add_node("unicode",
                       name="测试节点",
                       emoji="🎯",
                       special_chars="äöü ñ")

        converter = NetworkXHTMLConverter()
        html_content = converter.preview(graph, "Unicode Test")

        self.assertIn("测试节点", html_content)
        self.assertIn("🎯", html_content)
        self.assertIn("äöü ñ", html_content)


class TestColorByProperty(unittest.TestCase):
    """Test color by property functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a graph with categorized nodes
        self.graph = nx.Graph()
        self.graph.add_node("A", category="red", value=100)
        self.graph.add_node("B", category="red", value=200)
        self.graph.add_node("C", category="blue", value=150)
        self.graph.add_node("D", category="blue", value=75)
        self.graph.add_node("E", category="green", value=300)
        self.graph.add_edge("A", "B")
        self.graph.add_edge("B", "C")
        self.graph.add_edge("C", "D")
        self.graph.add_edge("D", "E")

    def test_color_by_property_application(self):
        """Test that color_by_property correctly assigns colors to nodes."""
        converter = NetworkXHTMLConverter()

        # Apply color by category
        converter.apply_color_by_property(self.graph, "category")
        
        # Check that nodes with same category have same color
        red_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("category") == "red"]
        blue_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("category") == "blue"]
        green_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("category") == "green"]
        
        # All red nodes should have the same color
        red_colors = [self.graph.nodes[n]["color"] for n in red_nodes]
        self.assertEqual(len(set(red_colors)), 1, "All red category nodes should have the same color")
        
        # All blue nodes should have the same color
        blue_colors = [self.graph.nodes[n]["color"] for n in blue_nodes]
        self.assertEqual(len(set(blue_colors)), 1, "All blue category nodes should have the same color")
        
        # All green nodes should have the same color
        green_colors = [self.graph.nodes[n]["color"] for n in green_nodes]
        self.assertEqual(len(set(green_colors)), 1, "All green category nodes should have the same color")
        
        # Different categories should have different colors
        all_colors = set(red_colors + blue_colors + green_colors)
        self.assertEqual(len(all_colors), 3, "Different categories should have different colors")

    def test_color_by_property_in_html_output(self):
        """Test that colors appear correctly in HTML output."""
        output_file = os.path.join(self.temp_dir, "color_test.html")
        
        # Use convenience function with color_by_property
        result_file = convert_networkx_to_html(
            self.graph,
            output_file,
            "Color Test",
            color_by_property="category"
        )
        
        self.assertTrue(os.path.exists(result_file))
        
        with open(result_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that color properties are in the generated JSON data
        self.assertIn('"color":', content, "HTML should contain color properties in node data")
        
        # Verify that nodes with same category have same color in the data
        import json
        import re
        
        # Extract the graph data JSON from the HTML
        match = re.search(r'const graphData = ({.*?});', content, re.DOTALL)
        self.assertIsNotNone(match, "Should find graphData in HTML")
        
        graph_data = json.loads(match.group(1))
        
        # Group nodes by category and check colors
        category_colors = {}
        for node in graph_data['nodes']:
            category = node['properties'].get('category')
            color = node['properties'].get('color')
            
            if category not in category_colors:
                category_colors[category] = color
            else:
                self.assertEqual(category_colors[category], color, 
                               f"All nodes in category '{category}' should have the same color")
        
        # Should have 3 different colors for 3 categories
        unique_colors = set(category_colors.values())
        self.assertEqual(len(unique_colors), 3, "Should have 3 unique colors for 3 categories")

    def test_color_by_nonexistent_property(self):
        """Test behavior when property doesn't exist on some nodes."""
        # Add a node without the category property
        self.graph.add_node("F", value=400)  # No category
        
        converter = NetworkXHTMLConverter()
        converter.apply_color_by_property(self.graph, "category")
        
        # Node F should get the default gray color
        self.assertEqual(self.graph.nodes["F"]["color"], "#cccccc")

    def test_color_palette_generation(self):
        """Test color palette generation for different numbers of categories."""
        converter = NetworkXHTMLConverter()
        
        # Test with 3 colors
        colors_3 = converter._generate_color_palette(3)
        self.assertEqual(len(colors_3), 3)
        self.assertEqual(len(set(colors_3)), 3, "All colors should be unique")
        
        # Test with 10 colors
        colors_10 = converter._generate_color_palette(10)
        self.assertEqual(len(colors_10), 10)
        self.assertEqual(len(set(colors_10)), 10, "All colors should be unique")
        
        # All should be valid hex colors
        for color in colors_3 + colors_10:
            self.assertRegex(color, r'^#[0-9a-fA-F]{6}$', f"'{color}' should be a valid hex color")


def run_tests():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()