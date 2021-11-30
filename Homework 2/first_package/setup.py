from setuptools import setup, find_namespace_packages

setup(
    name='Get time',
    version='0.1',
    description='Library for work with time',
    author='Korostast',

    packages=find_namespace_packages(include=['namespace.*']),

    install_requires=['requests==2.26.0'],
    entry_points={
        'console_scripts': [
            'get_time=namespace.first_sub_package.get_time_module:main',
        ]
    }
)


