from setuptools import setup, find_packages

setup(
    name="pranky-mailer",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description="A Django app to send emails via multiple providers with logging and quota management",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/prankycoders/pranky_mailer",
    author="Ankit Bhardwaj",
    author_email="ankitbhardwaj007@gmail.com",
    install_requires=[
        "Django>=3.2",
        "boto3>=1.26",
        "requests>=2.28",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
