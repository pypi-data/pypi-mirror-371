
from setuptools import setup, Extension
from setuptools.dist import Distribution

class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True

setup(
    name="sagebox",
    version="0.1.0",
    packages=["sagebox"],
    package_dir={"": "src"},
    package_data={"sagebox": ["*.pyd"]},
    distclass=BinaryDistribution,
)