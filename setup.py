from setuptools import setup

setup(
    name = 'PetCare',
    packages = ['PetCare'],
    include_package_data = True,
    install_requires = [
        'flask',
    ],
)