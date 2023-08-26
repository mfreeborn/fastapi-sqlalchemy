import re
from pathlib import Path

from setuptools import setup

with open(Path("fastapi_sqlalchemy") / "__init__.py", encoding="utf-8") as fh:
    version = re.search(r'__version__ = "(.*?)"', fh.read(), re.M).group(1)

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="FastAPI-SQLAlchemy-improved",
    version=version,
    url="https://github.com/Ewen-Zippedscript/fastapi-sqlalchemy",
    project_urls={
        "Code": "https://github.com/Ewen-Zippedscript/fastapi-sqlalchemy",
        "Issue tracker": "https://github.com/Ewen-Zippedscript/fastapi-sqlalchemy/issues",
    },
    license="MIT",
    author="Ewen Lorimer",
    author_email="ewen@zippedscript.com",
    description="Adds simple SQLAlchemy support with multiple databases to FastAPI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["fastapi_sqlalchemy"],
    package_data={"fastapi_sqlalchemy": ["py.typed"]},
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=["starlette>=0.12.9", "SQLAlchemy>=1.2", "fastapi>=0.52.0"],
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


# build commands: python setup.py sdist bdist_wheel && python -m twine upload dist/* -u __token__ -p <token>
