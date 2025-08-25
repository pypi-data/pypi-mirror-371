from setuptools import setup, find_packages

setup(
    name="dearning",
    version="1.1.5",
    description="Libraries membuat AI yang ringan",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Oriza",
    author_email="email@example.com",
    url="https://example.com",
    project_urls={
        "Homepage": "https://example.com",
        "Repository": "https://example.com/repo",
    },
    license="Apache-2.0",
    python_requires=">=3.7",
    packages=find_packages(include=["dearning", "Memory", "dearning.*", "Memory.*"]),
    package_data={
        "dearning": ["*.txt", "*.json", "*.md", "*.pdf"],  # termasuk tutorial_dearning.pdf
        "Memory": ["*.json", "*.txt", "*.dat"]
    },
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "dearning = dearning.__main__:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ]
)