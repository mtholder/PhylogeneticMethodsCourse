from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='tree_likelihood_viz',
      version=version,
      description="Visualizations of the likelihood on trees using a few simple models of character evolution",
      long_description="""\
A PyQT-dependent library that can depict simple trees, the pattern frequencies implied by simpl e models and likelihoods.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='phylogenetics teaching likelihood',
      author='Mark T. Holder',
      author_email='mtholder@gmail.com',
      url='http://github.com/mtholder/PhylogeneticMethodsCourse',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        # 'PyQt4', # we do depend on PyQt4, but they are not setuptools-friendly
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
