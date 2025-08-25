from setuptools import setup, find_packages

with open(f'./package/readme.md', f'r') as f:
    long_description = f.read()
long_description = f'\n' + long_description.replace('\r', '')

setup(
    name='uurest',
    version='1.0.1',
    package_dir={"": "package"},
    long_description=long_description,
    long_description_content_type="text/markdown",
    description='uuRest library and its two main functions "call" and "fetch" are designed '
                'to allow users to rapidly scrape/automate web applications designed and developed by Unicorn Systems (Unicorn.com).',
    author='Jaromir Sivic',
    author_email='unknown@unknown.com',
    license="MIT",
    packages=find_packages(where="package"),
    keywords=['python', 'uuRest', 'Unicorn Systems', 'UAF', 'Unicorn Application Framework'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        'requests==2.32.2'
    ],
    extras_require={
        "dev": ["twine>=4.0.2"]
    },
    python_requires=">=3.8"
)
