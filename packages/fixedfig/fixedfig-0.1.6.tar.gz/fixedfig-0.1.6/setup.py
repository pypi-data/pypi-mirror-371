from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="fixedfig",
    version="0.1.6",
    description="A wrapper for matplotlib's plt.show() that globally sets figure window size, position, and target screen.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["matplotlib", "pyglet==1.5.27"],
    python_requires=">=3.8",
)
