from setuptools import setup, find_packages

setup(
    name="arpscanner",
    version="0.1",
    packages=find_packages(),
    install_requires=["scapy"],
    entry_points={
        'console_scripts': ['arpscanner = arpscanner.arpscanner:main']
    }
)