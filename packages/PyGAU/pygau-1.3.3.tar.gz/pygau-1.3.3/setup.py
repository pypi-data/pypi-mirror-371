import setuptools

with open("README.md", "r") as file:
    long_description = file.read()

setuptools.setup(
    name="PyGAU",
    version="1.3.3",
    author="SpaceProgrammer",
    packages=setuptools.find_packages(),
    url="https://github.com/SpaceProgrammerOriginal/PyGAU",
    license="Custom",
    classifiers=[
        "License :: Other/Proprietary License"
    ],

    long_description=long_description,
    long_description_content_type="text/markdown"
)