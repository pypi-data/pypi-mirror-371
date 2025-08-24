from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mkdocs-md-preview",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="MkDocs plugin for side-by-side markdown preview",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mkdocs-md-preview",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/mkdocs-md-preview/issues",
        "Documentation": "https://github.com/yourusername/mkdocs-md-preview#readme",
        "Source Code": "https://github.com/yourusername/mkdocs-md-preview",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
    python_requires=">=3.7",
    install_requires=[
        "mkdocs>=1.0",
        "markdown>=3.0",
    ],
    entry_points={
        "mkdocs.plugins": [
            "md-preview = mkdocs_md_preview:MarkdownPreviewPlugin",
        ]
    },
    keywords="mkdocs plugin markdown preview side-by-side",
)
