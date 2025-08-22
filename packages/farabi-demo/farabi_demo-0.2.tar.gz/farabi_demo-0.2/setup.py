from setuptools import setup, find_packages

setup(
    name='farabi_demo',
    version='0.2',
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
)