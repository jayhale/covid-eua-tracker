from setuptools import setup

setup(
    name='covid-euas-tracker',
    version='0.0.0',
    description='Data load and transform for FDA COVID-19 EUAs',
    url='http://github.com/jayhale/covid-euas-tracker',
    author='Jay Hale',
    license='MIT',
    py_modules=['tools'],
    install_requires=['beautifulsoup4', 'Click', 'dateparser', 'pyyaml', 'requests'],
    extras_require={'dev': ['black', 'flake8']},
    entry_points='''
        [console_scripts]
        euas=tools.cli:cli
    ''',
)
