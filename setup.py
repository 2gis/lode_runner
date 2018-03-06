from setuptools import find_packages, setup


setup(
    name='lode_runner',
    url='https://github.com/2gis/lode_runner',
    version='0.4.4',
    description='Nosetests runner plugins package',
    long_description='',
    author='Igor Pavlov',
    author_email='nwlunatic@yandex.ru',
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        "nose == 1.3.7"
    ],
    entry_points={
        'console_scripts': [
            'lode_runner = lode_runner.core:main',
            'lode_merge_xunit = lode_runner.lode_merge_xunit:main',
        ],
        'nose.plugins.0.10': [
            'dataprovider = lode_runner.plugins.dataprovider:Dataprovider',
            'xunit = lode_runner.plugins.xunit:Xunit',
            'multiprocess = lode_runner.plugins.multiprocess:MultiProcess',
            'testid = lode_runner.plugins.testid:TestId',
            'initializer = lode_runner.plugins.initializer:Initializer',
            'failer = lode_runner.plugins.failer:Failer',
            'class_skipper = lode_runner.plugins.class_skipper:ClassSkipper',
            'suppressor = lode_runner.plugins.suppressor:Suppressor'
        ]
    },
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing'
        ],
)
