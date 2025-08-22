from setuptools import setup, find_packages

with open("README.md", "r") as f:
          description = f.read()

setup(
    name="farabi_demo",
    version="0.3.0",
    packages=find_packages(),
    install_requires = [
        # Add dependencies here.
        # e.g. 'numpy>=1.11.1'
    ],
    entry_points={
        "console_scripts": [
            "farabi-demo = farabi_demo:hello",
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown",
)