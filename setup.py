#!/usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='marmoset',
    version='0.5.0',
    description="Simple HTTP API for managing stuff on libvirt hosts ",
    author="https://github.com/virtapi/marmoset/graphs/contributors",
    url="https://github.com/virtapi/marmoset",
    packages=['marmoset'],
    scripts=['marmoset.py'],
    install_requires=["Flask>=0.10.1", "Flask-RESTful>=0.3.5", "ldap3>=1.0.4", "libvirt-python>=1.3.1"],
    tests_require=["nose>=1.3.7", "mock>=1.3.0", "testfixtures>=4.7.0"],
    test_suite="nose.collector"
)
