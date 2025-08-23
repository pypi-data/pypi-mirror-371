import os
import sys

from setuptools import find_packages
from setuptools import setup

version = '1.0.0'

install_requires = [
    'requests>=2.25.0',
    'cryptography>=3.4.0',
    'setuptools>=39.0.1',
]

# Add certbot dependencies only if not in SNAP build
if not os.environ.get('SNAP_BUILD'):
    install_requires.extend([
        'acme>=1.0.0',
        'certbot>=1.0.0',
    ])

setup(
    name='certbot-dns-f5xc',
    version=version,
    description="F5 Distributed Cloud (F5XC) DNS Authenticator plugin for Certbot",
    url='https://github.com/fadlytabrani/certbot-dns-f5xc',
    author="Fadly Tabrani",
    author_email='fadly.tabrani@gmail.com',
    license='Apache License 2.0',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],

    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        'certbot.plugins': [
            'dns-f5xc = certbot_dns_f5xc._internal.dns_f5xc:Authenticator',
        ],
    },
)
