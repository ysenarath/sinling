import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sinling", # Replace with your own username
    version="0.0.1",
    author="Yasas Senarath",
    description="A language processing tool for Sinhalese (සිංහල)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ysenarath/sinling",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=['emoji'],
)