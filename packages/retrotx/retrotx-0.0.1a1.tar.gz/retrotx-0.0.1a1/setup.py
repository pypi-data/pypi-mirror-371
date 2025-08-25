"""Setup script for RetroTx"""

from setuptools import setup, find_packages

setup(
    name="retrotx",
    version="0.0.1a1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
