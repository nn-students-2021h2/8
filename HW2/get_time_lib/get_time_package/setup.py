from setuptools import setup, find_namespace_packages

setup(
    name='get_time_package',
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
    ],
    entry_points={
        'console_scripts': [
            'get_time=namespace_get_time.get_time_no_pretty.get_time_module:main'
        ]
    }
)
