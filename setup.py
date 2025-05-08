from setuptools import setup


NAME = "myclimbz"
DESCRIPTION = "App to track your climbing sessions and projects."
URL = "https://github.com/carlosfranzreb/boulders"


def req_file(filename: str) -> list[str]:
    """Get requirements from file"""
    with open(filename, encoding="utf-8") as f:
        content = f.readlines()
    required, links = list(), list()
    for line in content:
        line = line.strip()
        required.append(line)
    return required, links


REQUIRED = req_file("requirements.txt")
EXTRAS = {}
VERSION = "2.0.0"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    url=URL,
    packages=["myclimbz"],
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    author="Carlos Franzreb",
    author_email="myclimbz@outlook.de",
    license="MIT",
)
