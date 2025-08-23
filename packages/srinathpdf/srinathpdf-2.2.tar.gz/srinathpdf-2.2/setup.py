import setuptools
from pathlib import Path

setuptools.setup(
    name="srinathpdf",
    version="2.2",
    author="Srinath Reddy",
    author_email="srinathreddy438@gmail.com",
    description="It will convert pdf to image and text",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    # url="https://github.com/yourusername/srinathpdf",
    packages=setuptools.find_packages(exclude=["tests", "data"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # python_requires=">=3.6",

)