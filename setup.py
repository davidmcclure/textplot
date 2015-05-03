

from setuptools import setup, find_packages


setup(

    name='textplot',
    version='0.1.1',
    description='(Mental) maps of texts.',
    url='https://github.com/davidmcclure/textplot',
    license='MIT',
    author='David McClure',
    author_email='davidwilliammcclure@gmail.com',
    scripts=['bin/textplot'],
    packages=find_packages(),
    package_data={'textplot': ['data/*']},

    install_requires=[
        'scikit-learn',
        'numpy',
        'scipy',
        'matplotlib',
        'nltk',
        'networkx',
        'clint',
        'pytest',
        'click',
    ]

)
