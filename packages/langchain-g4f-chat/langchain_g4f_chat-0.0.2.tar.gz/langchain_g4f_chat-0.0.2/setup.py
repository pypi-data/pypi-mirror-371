"""Setup configuration for langchain-g4f package."""

import os
from setuptools import setup

# Get the current directory
current_dir = os.path.abspath(os.path.dirname(__file__))

# Read the README file
try:
    with open(os.path.join(current_dir, 'README.md'), 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Comprehensive G4F integration for LangChain with all capabilities"

# Define version directly to avoid import issues during build
__version__ = "0.0.2"

# Define requirements
INSTALL_REQUIRE = [
    "langchain-core>=0.3.74",
    "g4f>=0.6.1.4",
    "pydantic>=2.0",
    "typing-extensions>=4.0.0",
]

EXTRA_REQUIRE = {
    'all': [
        "langchain-openai>=0.3.31",
        "langchain-groq>=0.3.7",
        "pillow",  # For image processing
        "aiohttp",  # For async operations
        "requests",  # For HTTP requests
    ],
    'openai': [
        "langchain-openai>=0.3.31",
    ],
    'groq': [
        "langchain-groq>=0.3.7",
    ],
    'images': [
        "pillow",
    ],
    'dev': [
        "pytest>=6.0",
        "pytest-asyncio",
        "black",
        "flake8",
        "mypy",
    ],
    'test': [
        "pytest>=6.0",
        "pytest-asyncio",
    ],
}

# Package description
DESCRIPTION = "Comprehensive G4F integration for LangChain with all capabilities"

# Setting up
setup(
    name='langchain-g4f-chat',
    version=__version__,
    author='AIMLDev726',
    author_email='aistudentlearn4@gmail.com',
    description=DESCRIPTION,
    long_description_content_type='text/markdown',
    long_description=long_description,
    packages=['langchain_g4f', 'langchain_g4f.text', 'langchain_g4f.core', 'langchain_g4f.images'],
    package_data={
        'langchain_g4f': ['*.md', '*.txt'],
    },
    include_package_data=True,
    install_requires=INSTALL_REQUIRE,
    extras_require=EXTRA_REQUIRE,
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords=[
        'langchain',
        'g4f',
        'gpt4free',
        'ai',
        'llm',
        'chatbot',
        'openai',
        'groq',
        'chat',
        'completion',
        'tool-calling',
        'structured-output',
    ],
    license='MIT',
    zip_safe=False,
)
