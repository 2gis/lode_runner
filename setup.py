from setuptools import find_packages, setup


setup(
    name='lode_runner',
    url='https://github.com/2gis/lode_runner',
    version='0.1',
    description='Nosetests runner plugins package',
    long_description='',
    author='Igor Pavlov',
    author_email='nwlunatic@yandex.ru',
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        "nose == 1.3.0",
        "nose-testconfig",
    ],
    entry_points={
        'console_scripts': [
            'lode_runner = lode_runner.lode_runner:main',
            'lode_merge_xunit = lode_runner.lode_merge_xunit:main',
        ],
        'nose.plugins.0.10': [
            'dataprovider = lode_runner.dataprovider:Dataprovider',
            'xunit = lode_runner.xunit:Xunit',
            'priority = lode_runner.priority:AttributeSelector',
            'multiprocess = lode_runner.multiprocess:MultiProcess',
            'testid = lode_runner.testid:TestId',
            'initializer = lode_runner.initializer:Initializer',
        ]
    },
)
