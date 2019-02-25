#!/usr/bin/env python3

from setuptools import setup

setup(name='simexpal',
		version='0.1',
		description='Tool to Simplify Experimental Algorithmics',
		url='https://github.com/hu-macsy/simexpal',
		author='Alexander van der Grinten, MACSy group HU-Berlin',
		author_email='alexander.vandergrinten@gmail.com',
		license='MIT',

		packages=['simexpal', 'simexpal.launch'],
		scripts=['scripts/simex'],
		install_requires=[
			'argcomplete',
			'pyyaml'
		])
