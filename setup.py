from setuptools import setup, find_packages

setup(
    name='pywaveclus',
    version='0.1.0',
    description='Waveclus package for spike detection, feature extraction, and clustering in neuroscience data using wavelets and PCA.',
    author='Masoud Khani',
    author_email='khanim@uwm.edu',
    url='https://github.com/msdkhani/pywaveclus',
    packages=find_packages(),
    install_requires=[
        'spikeinterface',
        'numpy',
        'scipy',
        'pywt',
        'scikit-learn',
        'statsmodels',
        'matplotlib',
        'pyyaml',
        'spclustering'
    ],
)
