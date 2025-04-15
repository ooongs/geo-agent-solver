from setuptools import setup, find_packages

setup(
    name="geo-solver",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
        "psycopg2-binary",
        "pgvector",
        "sentence-transformers",
        "numpy",
        "python-dotenv",
        "sqlalchemy-utils",
    ],
    python_requires='>=3.6',
) 