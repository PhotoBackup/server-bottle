"""Setup module for photobackup-bottle.

See: https://photobackup.github.io/
"""

# system
from setuptools import setup, find_packages
# local
from photobackup_bottle import __version__


setup(
    name='photobackup_bottle',
    version=__version__,
    description='The simplest PhotoBackup server, made with bottle',
    long_description=open('README.md').read(),
    url='https://photobackup.github.io/',
    author='s13d',
    author_email='photobackup@s13d.fr',
    keywords='pictures photographs mobile backup',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['bcrypt', 'bottle', 'docopt', 'logbook'],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Bottle',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Natural Language :: English',
        'Topic :: System :: Archiving :: Backup',
    ],

    entry_points={
        'console_scripts': [
            'photobackup=photobackup_bottle.photobackup:main',
        ],
    },
)
