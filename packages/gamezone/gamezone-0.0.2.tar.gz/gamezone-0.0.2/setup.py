from setuptools import setup, find_packages

setup(
    name='gamezone',
    version='0.0.2',
    author='Shreeya Singh',
    author_email='shreeyasingh2404@gmail.com',
    description='A collection of classic arcade games built with Python and Turtle Graphics.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/shreeya2424/pygamezone',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        
    ],
    # Corrected license file path
    # license_file='LICENSE',
)
