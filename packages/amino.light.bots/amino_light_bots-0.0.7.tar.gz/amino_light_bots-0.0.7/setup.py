from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

keywords = [
    "amino",
    "aminoapps",
    "amino.fix",
    "amino.light",
    "amino.ligt.py",
    "AminoLightPy",
    "amino-bot",
    "narvii",
    "medialab",
    "api",
    "python",
    "python3",
    "python3.x",
    "minori",
    "august",
    "augustlight",
    "aminolightpy",
    "amino.py"
    "amino.light.bots"
    "aminolightbots"
]

setup(
    name="amino.light.bots",
    version="0.0.7",
    url="https://github.com/AugustLigh/AminoLightBots",
    license="MIT",
    description="Best library for amino bots",
    author="AugustLight",
    packages=find_packages(),
    install_requires=["amino.light.py"],
    long_description_content_type="text/markdown",
    keywords=keywords,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)