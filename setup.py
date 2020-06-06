# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages
import os

with open("README.md") as f:
    readme = f.read()


def package_files():
    paths = []
    for (path, _, filenames) in os.walk("mlspeclib/schemas"):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


extra_files = package_files()

setup(
    name="mlspeclib",
    version="0.0.25",
    description="MLSpec helper library to making using metadata in ML workflows easier",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="David Aronchick",
    author_email="aronchick@gmail.com",
    url="https://github.com/mlspec/mlspec-lib",
    license="MIT License",
    keywords=["MLSpec", "Machine Learning"],  # Keywords that define your package best
    install_requires=[
        "wheel",
        "pyyaml",
        "marshmallow",
        "uritools",
        "semver",
        "python-box",
        "gremlinpython",
        "pymysql",
    ],
    packages=["mlspeclib", "mlspeclib.experimental"],
    include_package_data=True,
    package_data={"": extra_files},
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Intended Audience :: Developers",  # Define that your audience are developers
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",  # Again, pick a license
        "Programming Language :: Python :: 3",  # Specify which pyhton versions that you want to support
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
