from setuptools import setup, find_packages
import tomllib  
 
with open("pyproject.toml",  "rb") as f:  
    pyproject = tomllib.load(f)

setup(
    **pyproject["project"],
    author="ScottHu",
    author_email="scotthu1999@foxmail.com",
    packages=find_packages(),
)