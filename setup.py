#!/usr/bin/env python
"""
setup
Setup file for simcrunner.
Created by Romain Mondon-Cancel on 2018-08-02 12:00:42
"""

from setuptools import setup, find_packages

setup(
    name='simcrunner',
    version='0.1',
    packages=find_packages(exclude=['test*']),
    license='MIT',
    description='A python package to run simc.'
    long_description=open('README.md').read(),
    url='https://github.com/simcminmax/simcrunner',
    author='Romain Mondon-Cancel [skasch]',
    author_email='romain.mondoncancel@gmail.com'
)