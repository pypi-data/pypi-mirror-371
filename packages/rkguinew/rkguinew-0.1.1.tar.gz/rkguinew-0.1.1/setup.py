from setuptools import setup, find_packages

setup(
    name="rkguinew",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.0",
        "PyQtWebEngine>=5.15.0"
    ],
    python_requires=">=3.7",
    description="Tkinter-like GUI library using PyQt5 with full widget set",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="1001015dhh",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
)
