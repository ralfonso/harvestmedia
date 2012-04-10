# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
      name='harvestmedia',
      version='0.0.1',
      packages=find_packages('.'),
      author='Ryan Roemmich',
      author_email='ryan@roemmich.org',
      description='Wrapper for the Harvest Media XML API',
      install_requires=['httplib2', 'cElementTree', 'pytz', 'iso8601', ],
      keywords='Harvest HarvestMedia API Media Music',
)
