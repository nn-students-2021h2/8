from setuptools import setup, find_namespace_packages

setup(
    name='Get pretty time',
    version='0.1',
    description='Additional functional for \'Get time\' library',
    author='Korostast',

    packages=['namespace'],
    namespace_packages=['namespace'],

    install_requires=['requests==2.26.0'],
)
