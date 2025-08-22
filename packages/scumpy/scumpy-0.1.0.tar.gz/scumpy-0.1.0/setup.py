from setuptools import setup, find_packages

setup(
    name='scumpy',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'sympy',
        'numpy',
        'scipy',
        'pyperclip',
    ],
    author='Scumpy Team',
    description='A library for solving mathematical problems and saving solutions to clipboard.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your_username/scumpy',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

