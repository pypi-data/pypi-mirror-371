from setuptools import find_packages, setup

setup(
    name="flexistore",
    version="0.2.0",
    description="Cloud-agnostic storage interface with enhanced features and async support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Prakhar Agarwal",
    author_email="prakhara56@gmail.com",
    url="https://github.com/prakhara56/FlexiStore",
    packages=find_packages(where=".", include=["flexistore", "flexistore.*"]),
    install_requires=[
        "azure-storage-blob>=12.0.0",
        "boto3>=1.17.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "flexistore = flexistore.cli.main:main",
            "flexistore-cli = flexistore.cli.main:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Filesystems",
    ],
    keywords=["storage", "cloud", "azure", "aws", "s3", "blob", "async"],
)
