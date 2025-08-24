from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="selenium-stealth-helper",
    version="1.1.0",
    author="Web Automation Team",
    author_email="web.automation@example.com",
    description="Enhanced Selenium stealth automation tools with Cloudflare bypass capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/web-automation/selenium-stealth-helper",
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
    keywords="selenium, stealth, automation, cloudflare, bypass, webdriver",
    project_urls={
        "Bug Reports": "https://github.com/web-automation/selenium-stealth-helper/issues",
        "Source": "https://github.com/web-automation/selenium-stealth-helper",
        "Documentation": "https://github.com/web-automation/selenium-stealth-helper#readme",
    },
)
