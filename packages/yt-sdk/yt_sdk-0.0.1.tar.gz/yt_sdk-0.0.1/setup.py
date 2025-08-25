from pathlib import Path

from setuptools import find_packages, setup

def get_requirements_txt():
    with open("requirements.txt", "r") as f:
        lines = f.readlines()
        return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


setup(
    name="yt_sdk",
    version="0.0.1",
    author="Alejo Prieto Dávalos",
    packages=find_packages(),
    description="Youtube SDK - Download video audio, etc...",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/yt-sdk/",
    project_urls={
        "Source": "https://github.com/AlejoPrietoDavalos/yt-sdk/"
    },
    python_requires=">=3.11",
    install_requires=get_requirements_txt(),
    include_package_data=True
)
