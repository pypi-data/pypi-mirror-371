from setuptools import setup, find_packages

setup(
    name="grabby-tool",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "yt-dlp",
    ],
    entry_points={
        "console_scripts": [
            "grabby = grabby.cli:main"
        ],
    },
    author="ranveer",
    author_email="ranveerkavale12@gmail.com",
    description="A simple media downloader for YouTube and Instagram",
    url="https://github.com/ranveerkavale/grabby",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

