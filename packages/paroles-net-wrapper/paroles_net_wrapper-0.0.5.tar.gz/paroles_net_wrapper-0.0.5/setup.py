from setuptools import setup, find_packages

setup(
    name='paroles-net-wrapper',
    version='0.0.5',
    packages=find_packages(),
    py_modules=['paroles_net', 'utils', 'models'],
    install_requires=[
        'beautifulsoup4',
        'requests',
        'selenium'
    ],
    url='https://github.com/Starland9/paroles-net-wrapper.git',
    license='MIT',
    author='Starland9',
    author_email='landrysimo99@gmail.com',
    description='Ce projet permet de récupérer les paroles de chansons de paroles.net.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown'
)
