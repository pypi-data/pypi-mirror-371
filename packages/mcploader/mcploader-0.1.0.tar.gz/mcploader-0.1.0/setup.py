from setuptools import setup
from pathlib import Path

this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text()


setup(
    name="mcploader",
    version="0.1.0",
    description="This package is a small helper module that lets you define and consume multiple MCP servers (stdio, SSE, or Streamable HTTP) from a JSON configuration. It uses `pydantic-ai` MCP clients and validates configuration with Pydantic models.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fswair/mcploader",
    author="Mert Sirakaya",
    author_email="contact@tomris.dev",
    license="MIT",
    packages=["mcploader"],
    install_requires=[
        "pydantic-ai",
        "pydantic",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="mcp, mcp config management, pydantic-ai, mcp server, mcp client, mcp config, mcp servers",
    project_urls={
        "Bug Reports": "https://github.com/fswair/mcploader/issues",
        "Source": "https://github.com/fswair/mcploader",
    },
    package_data={
        "mcploader": ["py.typed"],
    },
)
