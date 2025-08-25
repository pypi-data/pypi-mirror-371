from setuptools import setup, find_packages
import os

# Читаем содержимое README файла
def read_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    return ""

setup(
    name="raystack",
    version="0.1.0",
    author="Vladimir",
    author_email="your.email@example.com",
    description="RayStack пакет с содержимым из test.txt",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/raystack",
    packages=["stack"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    package_data={"stack": ["*.txt"]},
) 