from setuptools import setup, find_packages

setup(
    name="healthcheck-cli",
    version="1.0.0",
    description="A CLI tool to monitor API endpoints health",
    author="Aglili Selorm Cecil",
    author_email="cecilselorm34@gmail.com",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0", 
        "httpx>=0.24.0",
        "aiohttp>=3.8.0",
    ],
    entry_points={
        "console_scripts": ["healthcheck=healthcheck_cli.main:app"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
)