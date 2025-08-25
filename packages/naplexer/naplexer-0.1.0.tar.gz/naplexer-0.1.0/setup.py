from setuptools import setup, find_packages

setup(
    name="naplexer",  # Updated package name
    version="0.1.0",
    description="A Python package that helps students develop their programming knowledge",
    author="73",
    author_email="73@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "naplexer": ["data/*.txt"],  # Updated to match new package name
    },
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
