from distutils.core import setup
from setuptools import setup, find_packages

with open('README.md', "r") as readme:
    long_description = readme.read()

setup(
    name="dns-spoofer",
    version="1.0",
    author="Kimball Leavitt",
    author_email="kimballleavitt@gmail.com",
    description="Spoof DNS queries over UDP",
    long_description=long_description,
    url="https://github.com/kimbo/dns-spoofer",
    package_data={'': ['README.md', 'LICENSE']},
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'dns-spoof=spoofer.spoofer:main',
            'dns-listen=spoofer.listen:main',
        ],
    },
    install_requires=['dnspython'],
    long_description_content_type='text/markdown'
)
