from setuptools import setup, find_packages

setup(
    name='commit-companion',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'click',
        'openai',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'commit-companion=commit_companion.cli:cli',
        ],
    },
    author='Zack Nelson',
    description='Generate AI-powered Git commit messages from diffs.',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    license='MIT',
    python_requires='>=3.7',
)