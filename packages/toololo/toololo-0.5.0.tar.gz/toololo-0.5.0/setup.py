from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="toololo",
    version="0.5.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0,<2"
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andreasjansson/toololo",
    author="Andreas Jansson",
    description="Minimal Python function calling for Claude and OpenRouter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
