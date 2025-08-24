from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="homeseer-client",
    version="0.1.1",
    author="John Ritsema",
    description="A thin wrapper around the Homeseer HTTP JSON API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jritsema/homeseer-python-client",
    project_urls={
        "Bug Tracker": "https://github.com/jritsema/homeseer-python-client/issues",
        "Documentation": "https://github.com/jritsema/homeseer-python-client#readme",
        "Source Code": "https://github.com/jritsema/homeseer-python-client",
    },    
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
)
