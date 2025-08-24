from setuptools import setup, find_packages

setup(
    name="whatsextract",
    version="1.0.1",
    description="WhatsExtract API client for Python",
    long_description=open("README.rst", "r", encoding="utf-8").read(),
    long_description_content_type="text/x-rst",
    author="WhatsExtract",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "aiohttp>=3.9.5",
        "pandas>=2.0.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries",
    ],
)
