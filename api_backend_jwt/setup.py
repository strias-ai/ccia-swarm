from setuptools import setup, find_packages

setup(
    name='fastapi-sqlalchemy-jwt',
    version='0.1.0',
    description='API REST backend profesional con FastAPI, SQLite, SQLAlchemy ORM, JWT y logging',
    author='Tu Nombre',
    author_email='tu.email@example.com',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'passlib',
        'bcrypt',
        'python-jose[cryptography]',
        'python-rotating-file-handler',
        'pydantic',
        'loguru'
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'fastapi-sqlalchemy-jwt=fastapi_sqlalchemy_jwt.main:main'
        ]
    }
)