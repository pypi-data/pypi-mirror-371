from setuptools import setup, find_packages

setup(
    name="smartcleaner",
    version="0.1.0",
    description="Smart auto-cleaning tool for Pandas DataFrames",
    author="Vishwa",
    packages=find_packages(),
    install_requires=["pandas", "numpy", "scipy"],
    python_requires=">=3.8",
)
