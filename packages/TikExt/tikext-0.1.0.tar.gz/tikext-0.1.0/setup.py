from setuptools import setup, find_packages

setup(
    name='TikExt',
    version='0.1.0',
    packages=find_packages(),
    author='@D_B_HH @PPH9P',
    description='A simple Python library to extract username from email.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/TikExt',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)


