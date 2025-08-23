from distutils.core import setup
from setuptools import find_packages
with open("README.md", "r") as f:
  long_description = f.read()
setup(
    name='PyUTLoc',
    version='1.0.1',
    description='PyUTLoc is implemented as a modular Python package designed to address the challenges of heterogeneous spatial location transformation through a unified framework. The implementation follows a layered architecture that separates concerns into distinct functional modules while maintaining interoperability between components. The package consists of three primary modules: annotation, geocoding, and transformation, each serving a specific role in the coordinate processing pipeline.',
    long_description=open('README.md').read(),
    author='Xiaoliang Dai',
    author_email='948719798@qq.com',
    url='https://github.com/dxl98/PyUTLoc',
    packages=find_packages(),
    install_requires=[
        'geopy',
        'requests',
        'geocoder',
        'pygeodesy',
        'mgrs',
        'utm',
        'pyproj',
        'openlocationcode',
        'geohash2',
        'maidenhead',
    ],
    entry_points={
        'console_scripts': [
            'locuct=LocUCT.transformation:main',  # Optional: if you want to create a command-line script
        ],
    },
)
