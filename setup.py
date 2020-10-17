import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lingua-tools-GonnaFlyMethod",
    version="0.0.5",
    author="GonnaFlyMethod",
    author_email="alexandergusakov@yahoo.com",
    description="Tools for working with different texts, words, and more!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GonnaFlyMethod/lingua-tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)