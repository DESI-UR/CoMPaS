#!/usr/bin/env python

# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function

#
# Standard imports
#
import glob
import os
import sys

#
# setuptools' sdist command ignores MANIFEST.in
#
from distutils.command.sdist import sdist as DistutilsSdist
from setuptools import setup, find_packages
from setuptools.command.install import install as InstallCommand

#
# Begin setup
#
setup_keywords = dict()
#
# THESE SETTINGS NEED TO BE CHANGED FOR EVERY PRODUCT.
#
setup_keywords['name'] = 'CoMPaS'
setup_keywords['description'] = 'Cosmological Multi-PArameter Scan'
setup_keywords['author'] = 'Tolga Yapici'
setup_keywords['author_email'] = 'tyapici@ur.rochester.edu'
setup_keywords['license'] = 'MIT'
setup_keywords['url'] = ''
setup_keywords['version'] = "0.0.1"

#
# Treat everything in bin/ except *.rst as a script to be installed.
#
if os.path.isdir('bin'):
    setup_keywords['scripts'] = [fname for fname in glob.glob(os.path.join('bin', '*'))
        if not os.path.basename(fname).endswith('.rst')]

setup_keywords['provides'] = [setup_keywords['name']]
setup_keywords['dependency_links'] = ['git+https://github.com/DESI-UR/KITCAT.git@2.0.0#egg=KITCAT-2.0.0']
setup_keywords['install_requires'] = ['healpy>=1.11.0', 'numpy>=1.13.1',
                                      'configparser>=3.5', 'astropy>=1.2.1', 'scipy>=0.19.1',
                                      'matplotlib>=2.0.0', 'emcee>=2.2.1', 'scikit-learn>=0.18.1',
                                      'KITCAT']
setup_keywords['zip_safe'] = False
setup_keywords['use_2to3'] = False
setup_keywords['package_dir'] = {'':'py'}
setup_keywords['packages'] = find_packages('py')

# Add internal data directories.
#
setup_keywords['package_data'] = {'CoMPaS': ['data/*',]}

# Run setup command.
#
setup(**setup_keywords)
