from setuptools import setup, find_packages

setup(
    name="euroncal_euroncal",    
    version="0.1.1",
    author="Arif Iqbal",
    author_email="ak041191@gmail.com",
    description="A simple calculator package",  
    long_description=open("README.md","r",encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "euroncal=euroncal.__init__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)