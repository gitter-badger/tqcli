from setuptools import setup

requirements = [l.split('=')[0] for l in open('requirements.txt', 'r').read().split('\n') if l]

setup(
    name='tqcli',
    version='1.0',
    description='TQCLI is the client application to use TranQuant services',
    url='http://github.com/tranquant/tqcli',
    author='Mehrdad Pazooki, Sean Glover, Rodrigo Abreu',
    author_email='mehrdad@tranquant.com',
    license='Apache 2.0',
    install_requires=requirements,
    packages=['tqcli', 'tqcli/batch', 'tqcli/config'],
    zip_safe=True
)