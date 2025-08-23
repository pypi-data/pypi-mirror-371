#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()

test_requirements = ['pytest>=3', ]

setup(
    author="Alex Rowley",
    author_email='',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Succinct small scale data manipulation",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='martens',
    name='martens',
    packages=find_packages(include=['martens', 'martens.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/arowley-ai/martens',
    version='0.4.24',
    zip_safe=False
)
