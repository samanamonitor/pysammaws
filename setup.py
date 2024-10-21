from setuptools import setup, find_packages
from sammaws import __version__

if __name__ == "__main__":
    setup(
        name='sammsnmp',
        version=__version__,
        packages=find_packages(include=['sammaws', 'sammaws.*']),
        data_files=[],
        install_requires=[ 'boto3' ]
    )
