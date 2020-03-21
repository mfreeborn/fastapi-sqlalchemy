import re

from setuptools import setup

with open("README.rst", "rt", encoding="utf-8") as f:
    long_description = f.read()

with open("fastapi_sqlalchemy/__init__.py", "rt", encoding="utf-8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read(), re.M).group(1)


setup(
    name="FastAPI-SQLAlchemy",
    version=version,
    url="https://github.com/mfreeborn/fastapi-sqlalchemy",
    project_urls={
        "Code": "https://github.com/mfreeborn/fastapi-sqlalchemy",
        "Issue tracker": "https://github.com/mfreeborn/fastapi-sqlalchemy/issues",
    },
    license="MIT",
    author="Michael Freeborn",
    author_email="michaelfreeborn1@gmail.com",
    description="Adds simple SQLAlchemy support to FastAPI",
    long_description=long_description,
    packages=["fastapi_sqlalchemy"],
    python_requires=">=3.7",
    install_requires=["starlette >=0.12.9,<=0.12.9", "SQLAlchemy>=1.2"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
