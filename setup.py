from setuptools import setup

setup(
    name='sst',
    version='1.0',
    packages=['sstruyen'],
    install_requires=[
        'Click',
        'colorama',
        'requests',
        'pyquery',
        'tinydb'
    ],
    entry_points='''
        [console_scripts]
        sst=sstruyen.cli:cli
    '''
)
