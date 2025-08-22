from setuptools import setup, find_packages

setup(
    name='haigen',
    version='0.5.2',
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langchain_core"
    ]

)
