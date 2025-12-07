"""
Setup script for Quranic Phonemizer package.
""" 
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

setup(
    name="quranic-phonemizer",
    version="1.0.0",
    description="A custom phonemizer (Grapheme to Phoneme converter) for the Qurʾān in the Hafs riwaya",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ahmed Ibrahim",
    author_email="quranicphonemizer@gmail.com",
    url="https://github.com/Hetchy/Quranic-Phonemizer",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*", "phonemizer", "out"]),
    # Resources are included via MANIFEST.in
    # Note: The phonemizer code expects resources at parent.parent / "resources"
    # This works in development mode. For production, you may need to adjust
    # the resource path resolution in the phonemizer code to use importlib.resources
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Text Processing :: Linguistic",
    ],
)

