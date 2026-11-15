#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="paper-pulse",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "paper-pulse=paper_pulse.cli:main",
        ],
    },
)
