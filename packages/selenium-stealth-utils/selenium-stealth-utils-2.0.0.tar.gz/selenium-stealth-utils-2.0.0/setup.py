from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="selenium-stealth-utils",
    version="2.0.0",
    author="Advanced Web Tools",
    author_email="advanced.webtools@example.com",
    description="Advanced web automation utilities with enhanced browser security and network protection features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/advanced-webtools/selenium-stealth-utils",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Security",
    ],
    python_requires=">=3.7",
    install_requires=[
        "selenium>=4.0.0",
        "selenium-stealth>=1.0.0",
        "requests>=2.25.0",
        "colorama>=0.4.4",
        "beautifulsoup4>=4.9.0",
        "psutil>=5.8.0",
    ],
    keywords="selenium, automation, browser, security, network, webdriver, testing",
    project_urls={
        "Bug Reports": "https://github.com/advanced-webtools/selenium-stealth-utils/issues",
        "Source": "https://github.com/advanced-webtools/selenium-stealth-utils",
        "Documentation": "https://github.com/advanced-webtools/selenium-stealth-utils#readme",
    },
)
