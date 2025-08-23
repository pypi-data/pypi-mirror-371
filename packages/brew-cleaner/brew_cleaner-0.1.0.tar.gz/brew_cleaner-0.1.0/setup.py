from setuptools import setup, find_packages

setup(
    name="brew-cleaner",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "prompt-toolkit==3.0.51",
    ],
    entry_points={
        "console_scripts": [
            "brew-cleaner = brew_cleaner.main:main",
        ],
    },
    author="Harsh",
    author_email="",
    description="A simple, interactive command-line tool to help you clean up your installed Homebrew formulae.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
    ],
)
