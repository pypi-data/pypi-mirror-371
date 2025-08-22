from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ntfybro",
    version="1.0.0",
    author="brodev.uz",
    author_email="contact@brodev.uz",
    description="Universal Ntfy notification package for Python projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://brodev.uz",
    project_urls={
        "Bug Tracker": "https://brodev.uz/issues",
        "Documentation": "https://brodev.uz/docs",
        "Source Code": "https://brodev.uz/source",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Communications",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    keywords="ntfy notifications push messaging alerts",
    include_package_data=True,
    zip_safe=False,
)