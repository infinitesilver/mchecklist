from setuptools import setup

setup(
    name='click_test',
    version='0.0.9',
    py_modules=['click_test'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'click_test = click_test:cli',
        ],
    },
)