from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='jack_wong_library',  # Use a unique name, check availability first
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A simple Python utility library for mathematical and string operations',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/yourusername/my_library',
    py_modules=['jack_wong_library'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires='>=3.6',
    keywords='math string utilities calculator',
)
