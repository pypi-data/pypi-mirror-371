from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='TeXicode',
    version='0.1.2',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'txc=src:main',
        ],
    },
    install_requires=[
        # List your dependencies here
    ],
    long_descriptio=description,
    long_descriptio_content_type="text/markdown",
)
