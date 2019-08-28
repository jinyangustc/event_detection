import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="Event Detection",
    version="0.1",
    author="Jinyang Li, Jiawei Tang",
    author_email="jinyang7@illinois.edu, jiaweit2@illinois.edu",
    description="Apollo event detection package",
    long_description=long_description,
    url="apollo4.cs.illinois.edu",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: University of Illinois at Urbana-Champaign",
        "Operating System :: OS Independent",
    ],
    install_requires=["toml", "click"],
    python_requires=">=3.7",
)
