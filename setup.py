from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in participatory_backend/__init__.py
from participatory_backend import __version__ as version

setup(
	name="participatory_backend",
	version=version,
	description="Backend to support participatory process",
	author="Steve Nyaga",
	author_email="stevenyaga@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
