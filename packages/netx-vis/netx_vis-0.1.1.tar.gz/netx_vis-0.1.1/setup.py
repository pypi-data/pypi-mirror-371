"""
Setup configuration for NetworkX HTML Viewer package.
"""

from setuptools import setup, find_packages

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="netx-vis",
    version="0.1.1",
    author="Olsi",
    description="Convert NetworkX graphs to interactive HTML visualizations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/olsihoxha/netx-vis",
    project_urls={
        "Bug Tracker": "https://github.com/olsihoxha/netx-vis/issues",
        "Documentation": "https://github.com/olsihoxha/netx-vis#readme",
        "Source Code": "https://github.com/olsihoxha/netx-vis",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: JavaScript",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "networkx_html_viewer": ["templates/*.html"],
    },
    keywords=[
        "networkx", "graph", "visualization", "html", "interactive",
        "d3js", "network", "graph-analysis", "data-visualization"
    ],
    entry_points={
        "console_scripts": [
            "netx-vis=networkx_html_viewer.examples.demo:main",
        ],
    },
    zip_safe=False,
)