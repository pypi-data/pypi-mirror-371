"""
Simple setup.py for durusai-cli compatible with modern PyPI
"""
from setuptools import setup, find_packages

setup(
    name="durusai-cli",
    version="1.0.2",
    description="Native CLI client for DurusAI - AI-powered development assistant",
    long_description="# DurusAI Native CLI\n\n🤖 Native CLI client for DurusAI - AI-powered development assistant",
    long_description_content_type="text/markdown",
    author="DurusAI Team",
    author_email="support@durusai.com",
    url="https://github.com/durusai/cli",
    
    packages=find_packages(),
    python_requires=">=3.8",
    
    install_requires=[
        "typer[all]>=0.9.0",
        "rich>=13.0.0", 
        "httpx>=0.24.0",
        "prompt-toolkit>=3.0.0",
        "keyring>=24.0.0",
        "cryptography>=40.0.0",
        "PyJWT>=2.8.0",
        "markdown>=3.4.0",
        "packaging>=21.0",
    ],
    
    entry_points={
        "console_scripts": [
            "durusai-cli=durusai.cli:main",
        ],
    },
    
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
)