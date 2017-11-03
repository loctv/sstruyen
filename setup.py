from setuptools import setup

setup(
    name='sst',
    version='1.0',
    py_modules=['main'],
    install_requires=[
        'Click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        sst=main:cli
    '''
)
