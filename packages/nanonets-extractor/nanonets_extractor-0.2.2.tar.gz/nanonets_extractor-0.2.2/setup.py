from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nanonets-extractor",
    version="0.2.2",
    author="Nanonets",
    author_email="support@nanonets.com",
    description="A Python library for extracting data from any document using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nanonets/document-extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "nanonets-extractor=nanonets_extractor.cli:main",
        ],
    },
    include_package_data=True,
) 