from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="grokbeast",
    version="5.0.0",
    author="Stark",
    author_email="stark@example.com",
    description="GrokBeast v5 - A problem hunting AI assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/grokbeast",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "grokbeast=grokbeast.src.chat_command_generator:main",
        ],
    },
) 