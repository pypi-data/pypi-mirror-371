# coding: utf-8

import pathlib

from setuptools import find_packages, setup

# Package meta-data.
NAME = "electricitymaps"
VERSION = "0.0.1"
DESCRIPTION = "Official Electricity Maps Python SDK"
URL = "https://github.com/electricitymaps/electricitymaps-contrib"
EMAIL = "hello@electricitymaps.com"
AUTHOR = "Electricity Maps"
REQUIRES_PYTHON = ">=3.10"
LICENSE = "MIT"
REQUIRED = [
    "urllib3 >= 2.1.0, < 3.0.0",
    "python-dateutil >= 2.8.2",
    "pydantic >= 2",
    "typing-extensions >= 4.7.1",
]

# Read the long description from README.md
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "test"]),
    install_requires=REQUIRED,
    include_package_data=True,
    package_data={"electricitymaps": ["py.typed"]},
    license=LICENSE,
    keywords=["OpenAPI", "Electricity Maps API", "carbon intensity", "SDK"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
    project_urls={
        "Documentation": "https://docs.electricitymaps.com",
        "Source": "https://github.com/electricitymaps/electricitymaps-contrib",
        "Tracker": "https://github.com/electricitymaps/electricitymaps-contrib/issues",
    },
)
