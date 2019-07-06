from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open("README.md") as f:
    long_description = f.read()

setup(
    name="iv",
    version="1.0.4",
    description="Flexible terminal image viewer for iTerm2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Russ Garrett",
    author_email="russ@garrett.co.uk",
    url="https://github.com/russss/iv",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="image iterm2 cli terminal",
    python_requires=">=3.4",
    packages=["iv"],
    install_requires=[
        "pillow>=6",
        "imgcat",
        "click>=7"
    ],
    entry_points={"console_scripts": {"iv=iv:main"}},
)
