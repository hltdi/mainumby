#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='Mainumby',
      version='2.2',
      description='Ayudante para la traducción castellano-guaraní',
      author='Michael Gasser',
      author_email='gasser@indiana.edu',
      url='http://homes.soic.indiana.edu/gasser/plogs.html',
      license="GPL v3",
#      install_requires=["yaml>=5.0"],
      packages=find_packages("src"),
      package_dir={'': "kuaa"},
      package_data = {'kuaa':
                      ['languages/grn/*', 'languages/grn/fst/*.pkl',
                       'languages/spa/*', 'languages/spa/fst/*.pkl',
                       'morphology/*',
                       'sessions/*',
                       'static/*',
                       'templates/*',
                       'texts/*'
                       ]}
     )
