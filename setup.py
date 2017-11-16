import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djac',
    version='0.1.0',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    include_package_data=True,
    license='MIT',
    description='A Django app to manage AC models and demo AC.',
    long_description=README,
    url='https://github.com/juga0/djac/',
    author='juga',
    author_email='juga@riseup.net',
    keywords='AC Email OpenPGP',
    install_requires=['emailpgp', 'py-autocrypt'],
    package_data={'fixtures': ['*.json'],
                  },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Build Tools',
    ],
)
