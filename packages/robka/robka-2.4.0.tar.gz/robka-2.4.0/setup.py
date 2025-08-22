from setuptools import setup, find_packages

try:
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="robka",
    version="2.4.0",
    description="A professional and localized Python library for interacting with Rubika Bot API, compatible with various systems.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="httex",
    author_email="",
    maintainer="httex",
    maintainer_email="",
    url="https://pypi.org/project/robka/",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "Pillow",
        "websocket-client",
        "pycryptodome",
        "aiohttp",
        "tqdm",
        "mutagen",
        "filetype",
        "aiofiles"
    ],
)


