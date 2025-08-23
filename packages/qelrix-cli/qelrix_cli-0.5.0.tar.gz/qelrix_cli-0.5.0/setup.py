from setuptools import setup, find_packages

setup(
    name='qelrix-cli',
    version='0.5.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'rich',
        'pyperclip'
    ],
    entry_points={
        'console_scripts': [
            'qelrix=qelrix_cli.cli:main',
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A command-line interface for interacting with Gemini AI.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/qelrix-cli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)


