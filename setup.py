import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="Event Detection",
    version="1.0",
    author="Jinyang Li, Jiawei Tang",
    author_email="",
    description="Apollo event detection package",
    long_description=long_description,
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: University of Illinois at Urbana-Champaign",
        "Operating System :: OS Independent",
    ],
)
