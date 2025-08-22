from setuptools import setup, find_packages
import os

# Read README file
readme_path = os.path.join(os.path.dirname(__file__), "README_playwright.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "A Playwright adaptation of HumanCursor for human-like mouse movements"

setup(
    name="humancursor-playwright",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "playwright>=1.30.0",
        "numpy>=1.19.0",
        "pytweening>=1.0.4",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ]
    },
    author="HumanCursor Playwright Fork",
    author_email="example@example.com",
    description="A Playwright adaptation of HumanCursor for human-like mouse movements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/humancursor-playwright",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/humancursor-playwright/issues",
        "Source": "https://github.com/yourusername/humancursor-playwright",
        "Original HumanCursor": "https://github.com/zajcikk/HumanCursor",
        "HumanCursor-Botasaurus": "https://github.com/youroriginalrepo/humancursor-botasaurus",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    keywords="playwright automation human cursor mouse movement web testing",
    entry_points={
        "console_scripts": [
            # Add any CLI tools if needed in the future
        ],
    },
)