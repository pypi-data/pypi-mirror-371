from setuptools import setup, find_packages

setup(
    name="create-prisma-app",   # <--- package name (pip install name)
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "create-prisma-app=create_prisma_app.cli:main",
        ],
    },
)
