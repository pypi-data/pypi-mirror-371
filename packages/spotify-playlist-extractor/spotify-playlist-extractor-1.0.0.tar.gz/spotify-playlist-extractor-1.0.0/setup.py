from setuptools import setup, find_packages

with open("README.txt", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip()]

setup(
    name="spotify-playlist-extractor",
    version="1.0.0",
    author="Junior Developer",
    author_email="junior@example.com",
    description="A simple CLI tool to extract Spotify playlists",
    long_description=long_description,
    long_description_content_type="text/plain",
    url="https://github.com/username/spotify-playlist-extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "spotify-extract=spotify_extractor.cli:main",
        ],
    },
    keywords="spotify playlist extractor music cli",
    project_urls={
        "Bug Reports": "https://github.com/username/spotify-playlist-extractor/issues",
        "Source": "https://github.com/username/spotify-playlist-extractor",
    },
)