#!/usr/bin/env python3
"""
Setup script for Zenify meditation app
"""

from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))

# Read README for long description
try:
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "A beautiful terminal-based meditation app with multi-language support"

setup(
    name='zenify',  # Simple and clean name
    version='1.0.2',
    description='🧘 A beautiful terminal meditation app with ASCII art, multi-language support, and breathing exercises',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Zenify Team',
    author_email='zenify.meditation@gmail.com',
    url='https://github.com/kawarox/zenify',
    project_urls={
        'Bug Reports': 'https://github.com/kawarox/zenify/issues',
        'Source': 'https://github.com/kawarox/zenify',
        'Documentation': 'https://github.com/kawarox/zenify/blob/main/README.md',
    },
    python_requires='>=3.6',
    packages=['zenify'],
    package_dir={'zenify': 'zenify'},
    include_package_data=True,
    package_data={
        'zenify': ['*.md', '*.txt'],
    },
    entry_points={
        'console_scripts': [
            'zen=zenify.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: English', 
        'Natural Language :: Japanese',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='meditation mindfulness terminal ascii wellness health breathing zen relaxation',
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    extras_require={
        'dev': [
            'build',
            'twine',
        ],
    },
)