#! /usr/bin/env python

import setuptools

with open('README.md', 'rt', encoding='ascii') as f:
    long_description = f.read()

short_description = long_description.split('\n', 1)[0].strip('# ')

with open('requirements.txt', 'rt', encoding='ascii') as f:
    requirements = f.readlines()

setuptools.setup(
        name = 'slidetextbridge',
        version='0.3.0',
        description=short_description,
        long_description=long_description,
        long_description_content_type='text/markdown',
        package_dir={'': 'src'},
        packages=setuptools.find_packages(where='src'),
        include_package_data=True,
        install_requires=requirements,
        python_requires='>=3.9',
        entry_points={
            'console_scripts': [
                'slidetextbridge=slidetextbridge.core.main:main',
            ],
        },
        url='https://github.com/norihiro/slidetextbridge',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Intended Audience :: End Users/Desktop',
            'Environment :: Console',
        ],
)
