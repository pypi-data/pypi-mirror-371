from setuptools import setup, find_packages

setup(
    name="universal_uicreator",
    version="1.0.0",
    author="Raymond Flanary",
    author_email="",
    description="Universal UI Creator Model: ultra-lightweight, futuristic, cross-language UI framework.",
    long_description=open("README.md").read() if __import__('os').path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    license="Proprietary",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: Other/Proprietary License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: User Interfaces",
    ],
    python_requires='>=3.7',
)
