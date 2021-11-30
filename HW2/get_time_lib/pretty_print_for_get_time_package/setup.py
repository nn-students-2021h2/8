from setuptools import setup, find_namespace_packages

setup(
    name='pretty_print_time',
    version='1.0',
    description='description',
    url='http://github.com/name/package_name',
    author='RaEzhov',
    author_email='email@example.com',
    license='MIT',
    packages=find_namespace_packages(include=['namespace_get_time.*']),
    namespace_packages=['namespace_get_time'],
    install_requires=[
        'requests==2.26.0',
    ]
)
