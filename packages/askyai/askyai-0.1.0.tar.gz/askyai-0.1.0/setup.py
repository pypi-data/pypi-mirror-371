from setuptools import setup, find_packages

setup(
    name="askyai",
    version="0.1.0",
    author="Huy alex",
    author_email="huyhuynhgia243@gmail.com",
    description="Libary for Making Ai",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    install_requires=[
        "openai"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
