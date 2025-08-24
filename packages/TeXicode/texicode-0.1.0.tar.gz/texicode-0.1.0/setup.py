from setuptools import setup, find_packages

setup(
    name='TeXicode',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'txc=main:main',
        ],
    },
    install_requires=[
        # List your dependencies here
    ],
)
