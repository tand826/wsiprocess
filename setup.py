import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wsiprocess",
    version="0.1",
    author="Takumi Ando",
    author_email="takumi.ando826@gmail.com",
    description="Whole Slide Image (WSI) Processing Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tand826/wsiprocess",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache-2.0",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "wsiprocess = cli:main"
        ]
    },
    install_requires=[
        "joblib",
        "lxml",
        "numpy",
        "opencv-python",
        "pyvips",
    ],
    python_requires='>=3.6',
)
