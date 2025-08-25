# setup.py
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="hashcounter",
    version="2025.8.241600",
    author="Eugene Evstafev",
    author_email="chigwel@gmail.com",
    description="Atomic per-string counter with sliding TTL in Redis (async).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chigwell/hashcounter",
    packages=find_packages(exclude=("tests",)),
    install_requires=["redis>=5.0.0"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    license="MIT",
    tests_require=["unittest"],
    test_suite="test",
)
