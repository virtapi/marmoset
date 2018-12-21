#!/usr/bin/env python3
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='marmoset',
    version='0.6.0',
    description='Simple HTTP API for managing stuff on libvirt hosts',
    keywords='dhcp dhcpd ldap libvirt management vms virtual-machines',
    author='https://github.com/virtapi/marmoset/graphs/contributors',
    url='https://github.com/virtapi/marmoset',
    packages=['marmoset'],
    scripts=['marmoset.py'],
    install_requires=['Flask>=0.10.1', 'Flask-RESTful>=0.3.5', 'ldap3>=1.0.4', 'libvirt-python>=1.3.1'],
    tests_require=['nose>=1.3.7', 'mock>=1.3.0', 'testfixtures>=4.7.0', 'prospector'],
    test_suite='nose.collector',
    license='GNU Affero General Public License',
    author_email='tim@bastelfreak.de',
    zip_safe=False,
    long_description=read('README.md'),
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
