# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='mcmod-cli',
    version='1.0.2',
    description = "A CLI tool for generating Minecraft Mod project structure and managing MODSDK development.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='CreatorMC',
    url='https://github.com/CreatorMC/MODSDKSping',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'mcmod=modsdkspring.main:main',
        ],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License"
    ],
    platforms='any'
)