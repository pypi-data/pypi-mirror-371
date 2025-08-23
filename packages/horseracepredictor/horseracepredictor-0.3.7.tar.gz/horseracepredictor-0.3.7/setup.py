from setuptools import setup, find_packages

setup(
    name='horseracepredictor',
    version='0.3.7',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'statsmodels',
        'scikit-learn',
    ],
    author='BLILLP',
    author_email='deviprasadgurrana@gmail.com',
    description='A package to predict horse race winners',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/BLILLP/horserace-nn.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
