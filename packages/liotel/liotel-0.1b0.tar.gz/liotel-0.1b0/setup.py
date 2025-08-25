from setuptools import setup, find_packages

setup(
    name="liotel",
    version="0.1b0",
    author="amiraliali3",
    author_email="amiraliali3779@gmail.com",
    description="A lightweight Telegram bot library for beginners",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/amiraliali3284/liotel",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)