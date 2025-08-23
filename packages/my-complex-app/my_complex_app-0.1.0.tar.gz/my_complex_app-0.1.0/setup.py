from setuptools import setup, find_packages

setup(
    name='my_complex_app',
    version='0.1.0',
    packages=find_packages(include=["my_complex_app"]),
    install_requires=["wheel","twine"],
    description='To add the given two complex numbers',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires=">=3.7"
)