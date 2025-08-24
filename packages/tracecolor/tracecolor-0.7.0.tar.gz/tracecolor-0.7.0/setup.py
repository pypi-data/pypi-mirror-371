from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tracecolor",
    version="0.7.0",
    author="Marco Del Pin",
    author_email="marco.delpin@gmail.com",
    description="Enhanced Python logger with colorized output, TRACE/PROGRESS levels, UDP monitoring, and Loguru backend.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marcodelpin/tracecolor",
    packages=find_packages(exclude=["tests.*", "tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "loguru>=0.7.2",
        "colorlog>=6.0.0",  # Fallback for when loguru is not available
    ],
    extras_require={
        "yaml": [
            "pyyaml>=6.0",
        ],
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=0.990",
        ]
    },
    entry_points={
        "console_scripts": [
            "tracecolor-monitor=tracecolor.monitor:main",
        ],
    },
)