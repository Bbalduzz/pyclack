from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh: long_description = fh.read()

setup(
    name='pyclack',
    version='0.1.0',
    author="Bbalduzz",
    description="Clack is a Python library for building interactive command line interfaces effortlessly. Inspired by clack.cc",
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'readchar',
        'enum'
    ],
    long_description_content_type="text/markdown",
    url="https://github.com/Bbalduzz/ith",
    project_urls={
        "Tracker": "https://github.com/Bbalduzz/pyclack/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)
