import os

from setuptools import setup, find_packages

def get_requirements(file_path: str) -> list[str]:
    "This function will return the list of packages"
    print(f"Looking for requirements file at: {os.path.abspath(file_path)}")
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()

    requirements = [
        requirement.replace("\n", "") for requirement in requirements
    ]  # noqa
    if "-e ." in requirements:
        requirements.remove("-e .")
    return requirements


setup(
    name='common-sense',
    version='0.1.0',
    description='Because common sense is not so common. Now it is — in Python!',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Happy Sharma",
    author_email="happycse54@gmail.com",
    url='https://github.com/Happy-Kumar-Sharma/common-sense',
    packages=find_packages(),
    install_requires=get_requirements("requirements.txt"),
    python_requires='>=3.7',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
