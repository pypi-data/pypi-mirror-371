from setuptools import setup, find_packages

setup(
    name='initPygame',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'pygame-ce'
    ],
    entry_points={
        "console_scripts":[
            "initPygame = initPygame:InitPygame"
        ],
    },
)