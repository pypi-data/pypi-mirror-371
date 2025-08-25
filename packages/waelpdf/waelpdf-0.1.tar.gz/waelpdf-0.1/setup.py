import setuptools
from pathlib import Path

setuptools.setup(
    name="waelpdf",
    version="0.1",
    description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["tests", "data"]),

)
