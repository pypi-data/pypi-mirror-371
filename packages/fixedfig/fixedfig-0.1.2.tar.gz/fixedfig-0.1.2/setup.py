from setuptools import setup, find_packages

setup(
    name="fixedfig",
    version="0.1.2",
    description="Global configuration of figure window size and position when using matplotlib.show()",
    packages=find_packages(),
    install_requires=["matplotlib", "pyglet==1.5.27"],
    python_requires=">=3.8",
)