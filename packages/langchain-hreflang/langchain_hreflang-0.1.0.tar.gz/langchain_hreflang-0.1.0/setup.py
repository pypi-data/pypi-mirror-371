"""Setup configuration for langchain-hreflang package."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="langchain-hreflang",
    version="0.1.0",
    author="Nick Jasuja",
    author_email="nikhilesh@gmail.com",
    description="LangChain tools for hreflang SEO analysis using hreflang.org API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/diffen/langchain-hreflang",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.12",
    install_requires=[
        "langchain>=0.1.0",
        "requests>=2.25.0",
        "pydantic>=2.0.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "twine>=3.0",
            "build>=0.7",
        ],
        "crewai": [
            "crewai>=0.1.0",
        ],
        "all": [
            "crewai>=0.1.0",
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
        ],
    },
    keywords=[
        "langchain", 
        "hreflang", 
        "seo", 
        "international", 
        "tools", 
        "ai", 
        "agents", 
        "crewai",
        "multilingual",
        "internationalization"
    ],
    project_urls={
        "Bug Reports": "https://github.com/diffen/langchain-hreflang/issues",
        "Source": "https://github.com/diffen/langchain-hreflang",
        "Documentation": "https://github.com/diffen/langchain-hreflang#readme",
        "Changelog": "https://github.com/diffen/langchain-hreflang/blob/main/CHANGELOG.md",
    },
    include_package_data=True,
    zip_safe=False,
)