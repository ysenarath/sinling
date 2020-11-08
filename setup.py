import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('packages.txt', 'r') as fh:
    requirements = fh.read().split('\n')

setuptools.setup(
    name="sinling",  # Replace with your own username
    version="0.3.6",
    author="Yasas Senarath",
    description="A language processing tool for Sinhalese (සිංහල)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ysenarath/sinling",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
)
