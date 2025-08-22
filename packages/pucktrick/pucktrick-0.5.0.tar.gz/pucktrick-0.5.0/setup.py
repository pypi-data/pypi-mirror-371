# setup.py
from setuptools import setup, find_packages

setup(
    name="pucktrick",
    version="0.5.0",
    packages=find_packages(),
    install_requires=["numpy","pandas"],
    author="Andrea Maurino",
    author_email="andrea.maurino@unimib.it",
    description="A python library for error genration in dataset for machine learning",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/andreamaurino/pucktrick",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    license="CC BY-NC 4.0",
)