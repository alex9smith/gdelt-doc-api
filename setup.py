import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gdeltdoc",
    version="1.2.0",
    author="Alex Smith",
    author_email="alex@alexsmith.dev",
    description="A client for the GDELT 2.0 Doc API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alex9smith/gdelt-doc-api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)