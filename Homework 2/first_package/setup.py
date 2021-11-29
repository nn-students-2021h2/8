from setuptools import setup, find_namespace_packages

setup(
    name='Get time',
    version='0.1',
    description='Library for work with time',
    author='Korostast',

    packages=['namespace'],
    namespace_packages=['namespace'],

    install_requires=['requests==2.26.0'],
    entry_points={
        'console_scripts': [
            'get_time=namespace.get_time_module:main',
        ]
    }
)


