#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='Mainumby',
      version='2.3',
      description='Ayudante para la traducción castellano-guaraní',
      author='Michael Gasser',
      author_email='gasser@indiana.edu',
      url='http://homes.soic.indiana.edu/gasser/plogs.html',
      license="GPL v3",
#      install_requires=["yaml>=5.0"],
      packages=find_packages("src"),
      package_dir={'': "src"},
      package_data = {'kuaa':
                      ['languages/grn/*', 'languages/grn/fst/*.pkl',
                       'languages/grn/lex/*', 'languages/grn/syn/*',
                       'languages/grn/stat/*', 'languages/grn/grp/*',
                       'languages/spa/*', 'languages/spa/fst/*.pkl',
                       'languages/spa/lex/*', 'languages/spa/syn/*',
                       'languages/spa/stat/*', 'languages/spa/grp/*',
                       'morphology/*',
                       'sessions/*',
                       'static/*',
                       'templates/*',
                       'texts/*',
                       '*.db'
                       ]}
     )
