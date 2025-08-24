from setuptools import setup, find_packages

setup(
    name="eyec",
    version="0.1.0",
    py_modules=["eyec"],
    install_requires=["pyperclip"],
    entry_points={
        "console_scripts": [
            "eyec=eyec:main",
        ],
    },
    author="Your Name",
    description="A simple clipboard history + search tool for Linux",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
)

