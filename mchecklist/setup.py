from setuptools import setup

setup(
    name="mchecklist",
    version="0.0.1",
    py_modules=["mchecklist", "cli"],
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "mchecklist = cli:cli",
        ],
    },
)
