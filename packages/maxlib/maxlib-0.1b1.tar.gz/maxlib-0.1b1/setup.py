from setuptools import setup, find_packages

setup(
    name="maxlib",
    version="0.1b1",
    packages=find_packages(),
    description="A utility library containing classes, errors, filters, and max functions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Sudo",
    author_email="sudo@onlysq.ru",
    url="https://github.com/xNoBanOnlyZXC/WebMaxLib",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "websockets",
        "requests",
    ],
)