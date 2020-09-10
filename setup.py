import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sentry-kmall-test-amarburg", # Replace with your own username
    version="0.0.1",
    author="Aaron Marburg",
    author_email="amarburg@uw.edu",
    description="A collection of tools for processing EM2040 data from AUV Sentry",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    install_requires=['kmall'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
