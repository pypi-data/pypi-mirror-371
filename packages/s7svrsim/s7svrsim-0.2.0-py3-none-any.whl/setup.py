from setuptools import setup, find_packages

setup(
    name="s7svrsim", 
    version="0.1.1",  
    author="newbienewbie",   
    description="type hints for writing S7SvrSim scripts",   
    long_description=open("../README.md").read(),  
    long_description_content_type="text/markdown",  
    url="https://github.com/newbienewbie/s7svrsim-hints",  
    packages=find_packages(),   
    classifiers=[   
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",   
    install_requires=[   
    ],
)