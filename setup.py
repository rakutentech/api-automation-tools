from setuptools import setup, find_packages


def readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()


requires = [
    'pytest',
    'pytest-xdist',
    'aiohttp',
    'pypeln',
    'numpy'
]


setup(
    name="api-automation-tools",
    version="1.0.0",
    author="Ashton Szabo",
    author_email="ashton.szabo@rakuten.com",
    description="Tools for API automation",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/rakutentech/api-automation-tools",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requires
)
