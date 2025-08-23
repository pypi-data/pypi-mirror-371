from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='antishlop-cli',
    version='1.1.0',
    description='Anti-vibe coding and security agent',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Arjun Bajpai',
    author_email='ArjunBajpai@tutamail.com',
    packages=['antishlopcli'],
    entry_points={
        'console_scripts': [
            'antishlop=antishlopcli.cli:main',
        ],
    },
    install_requires=[
        'openai',
        'colorama',
        'rich',
        'python-dotenv',
        'langchain==0.3.23',
        'langchain-openai==0.3.12',
        'langgraph==0.2.67',
        'typing-extensions',
        'tiktoken',
        'chromadb',
        'langchain-chroma'
    ]
)