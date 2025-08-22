from setuptools import setup, find_packages

setup(
    name='powder_ens_commons',
    version='0.1.0',
    description='A simple data/model commons package for POWDER experiments',
    author='Mumtahin Habib',
    author_email='mumtahin.mazumder@utah.edu',
    url='https://gitlab.flux.utah.edu/mumtahin_habib/powder_ens_commons',
    packages=find_packages(),
    install_requires=[
        'requests',
        'tqdm',
        'numpy',
        'pandas',
        'rasterio',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)

