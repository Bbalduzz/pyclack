from setuptools import setup, find_packages

base_requirements = ["readchar"]
core_requirements = base_requirements.copy()
prompts_requirements = base_requirements.copy()

setup(
    name="pyclack-cli",
    version="0.4.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    
    # dependencies
    install_requires=base_requirements,
    extras_require={
        "core": core_requirements,
        "prompts": prompts_requirements,
        "all": prompts_requirements,  # this includes everything
    },

    author="Edoardo Balducci",
    author_email="edoardoba2004@gmail.com",
    description="A python library for building interactive command line interfaces effortlessly. Inspired by clack.cc",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Bbalduzz/pyclack",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)