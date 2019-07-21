import setuptools

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="maestro-servo",
    version="0.1",
    description="Interact with Pololu Maestro servo controllers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alexander Dutton",
    author_email="code@alexdutton.co.uk",
    url="https://github.com/alexsdutton/python-maestro-servo",
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires=["pyusb"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ],
)
