from setuptools import setup, find_packages

setup(
    name='turtleQS',
    version='0.5',
    packages=find_packages(),
    install_requires=[
        
    ],
    entry_points={
        "console_scripts":[
            "turtleQS = turtleQS:TurtleQS"
        ],
    },
)