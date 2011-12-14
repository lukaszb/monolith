import os
import sys
from setuptools import setup, find_packages

readme_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
    'README.rst'))

try:
    long_description = open(readme_file).read()
except IOError, err:
    sys.stderr.write("[ERROR] Cannot find file specified as "
        "long_description (%s)\n" % readme_file)
    sys.exit(1)

install_requires = []
if sys.version_info < (2, 7):
    install_requires.append('unittest2')

setup(
    name='monolith',
    version='0.0.1',
    url='https://github.com/lukaszb/monolith',
    author='Lukasz Balcerzak',
    author_email='lukaszbalcerzak@gmail.com',
    description='FOOBAR',
    long_description=long_description,
    zip_safe=False,
    packages=find_packages(),
    scripts=[],
    test_suite='monolith.tests.collector',
    install_requires=install_requires,
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ],
)

