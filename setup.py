from version import palmapy_version
from setuptools import find_packages, setup

def get_requirements(path: str):
    return [l.strip() for l in open(path)]

setup(
    name="palma.py",
    version=palmapy_version,
    packages=find_packages(),
    install_requires=get_requirements("requirements.txt"),
)