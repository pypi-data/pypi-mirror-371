from setuptools import setup, find_packages

setup(
    name="pickme",
    version="0.0.1",
    author="Tanmay Sachan",
    author_email="tnmysachan@gmail.com",
    description="Smart optimizing LLM router",
    long_description="PickMe is a WIP smart LLM query router that gets better with use.",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.11",
    ],
    license="BSD-3-Clause",
    license_files=('LICENSE')
)
