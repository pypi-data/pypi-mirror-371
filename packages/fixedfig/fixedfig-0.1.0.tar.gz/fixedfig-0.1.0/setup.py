from setuptools import setup, find_packages

setup(
    name="fixedfig",
    version="0.1.0",
    description="Global configuration of figure window size and position when using matplotlib.show()",
    packages=find_packages(),
    install_requires=["matplotlib"],
    python_requires=">=3.8",
)