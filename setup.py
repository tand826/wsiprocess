import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wsiprocess",  # Replace with your own username
    version="0.0.1",
    author="Takumi Ando",
    author_email="takumi.ando826@gmail.com",
    description="Whole Slide Image (WSI) Processing Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tand826/wsiprocess",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "wsiprocess = cli:main"
        ]
    },
    python_requires='>=3.4',
)
