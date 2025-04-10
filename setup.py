from setuptools import setup, find_packages

setup(
    name="ctcae-standardizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.103.1",
        "uvicorn>=0.23.2",
        "pandas>=1.5.3",
        "openpyxl>=3.1.2",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "langchain>=0.0.275",
        "langchain-core>=0.1.1",
        "langchain-iris>=0.1.0",
        "langchain-openai>=0.0.1",
        "openai>=1.0.0",
        "irisnative>=1.2.0"
    ],
    python_requires=">=3.8",
)