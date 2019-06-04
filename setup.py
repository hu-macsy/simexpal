#!/usr/bin/env python3

from setuptools import setup

with open('README.md', 'r') as f:
	readme = f.read()

setup(
	# First, state all metadata about the package.
	name='simexpal',
	version='0.2',
	description='Tool to Simplify Experimental Algorithmics',
	url='https://github.com/hu-macsy/simexpal',
	author='Alexander van der Grinten, MACSy group HU-Berlin',
	author_email='alexander.vandergrinten@gmail.com',
	license='MIT',
	long_description=readme,
	long_description_content_type='text/markdown',

	# Now, set the actual Python configuration.
	packages=['simexpal', 'simexpal.launch'],
	scripts=['scripts/simex'],
	install_requires=[
		'argcomplete',
		'requests',
		'pyyaml'
	]
)

