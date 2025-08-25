from setuptools import find_packages, setup

setup(
    name='pydtree',
    version='1.0.2',
    description='Python library for building and traversing trees',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='DogiFnf',
    author_email='dogifnf@gmail.com',
    url='https://github.com/DogiFnf/DTree',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
