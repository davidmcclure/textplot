

from setuptools import setup, find_packages


setup(

    name='textplot',
    version='0.1.0',
    description='(Mental) maps of texts.',
    url='https://github.com/davidmcclure/textplot',
    license='Apache',
    author='David McClure',
    author_email='davidwilliammcclure@gmail.com',
    include_package_data=True,
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
