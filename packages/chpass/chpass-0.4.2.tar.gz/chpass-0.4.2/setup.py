import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="chpass",
    version="0.4.2",
    author="Ben Gabay",
    author_email="ben.gabay38@gmail.com",
    license="License :: OSI Approved :: MIT License",
    description="Gather information from chrome",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bengabay11/chpass",
    packages=setuptools.find_packages(),
    install_requires=[
        "pattern-singleton==1.2.0",
        "sqlalchemy==2.0.31",
        "pandas==2.2.0"
    ],
    python_requires=">=3",
    entry_points={
        'console_scripts': ['chpass = chpass.__init__:main'],
    },
    keywords="chrome passwords",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
