from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="tracecolor",
    version="0.7.0",
    author="Marco Del Pin",
    description="Enhanced logging with TRACE/PROGRESS levels and UDP monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marcodelpin/python-shared-libs/tree/main/tracecolor",
    py_modules=["tracecolor", "monitor"],
    python_requires=">=3.8",
    install_requires=[
        "loguru>=0.7.2",
    ],
    extras_require={
        "yaml": [
            "pyyaml>=6.0",
        ],
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "pylint>=2.15",
            "mypy>=0.990",
        ]
    },
    entry_points={
        "console_scripts": [
            "tracecolor-monitor=tracecolor.monitor:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
    ],
)