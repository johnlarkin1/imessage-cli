from setuptools import (
    find_packages,
    setup
)

setup(
    name="messages",
    version='0.1',
    py_modules=['messages'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'Click',
        'nltk'
    ],
    entry_points='''
        [console_scripts]
        messages=messages.cli:cli
    ''',
)