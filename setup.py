from setuptools import find_packages, setup

setup(
    name='lode_runner',
    version='0.1',
    description='Nosetests runner upgrade',
    long_description='',
    author='Igor Pavlov',
    author_email='nwlunatic@yandex.ru',
    packages=find_packages(),
    install_requires=[
        'nose',
        'nose-testconfig',
    ],
    scripts=['bin/lode_runner'],
)