"""
MkDocs Markdown Preview Plugin

A plugin that renders markdown blocks with `md preview into side-by-side boxes,
showing both the source code and the rendered output.
"""

from .plugin import MarkdownPreviewPlugin

__version__ = "1.0.0"
__all__ = ["MarkdownPreviewPlugin"]
