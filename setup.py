from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory: Path = Path(__file__).parent
long_description: str = (this_directory / "README.md").read_text()

setup(
    name="tsidpy",
    maintainer="Luis Medel",
    maintainer_email="luis@luismedel.com",
    description="A Python library for generating Time-Sorted Unique Identifiers (TSID)",
    url="https://github.com/luismedel/tsid-python",
    license="MIT",
    version="1.0.0.1",
    packages=["tsidpy"],
    long_description=long_description,
    long_description_content_type='text/markdown'
)