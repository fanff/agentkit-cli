from setuptools import setup, find_packages

setup(
    name="akitbootstrap",
    version="0.1",
    packages=find_packages(),
    package_data={
        # Include any *.yaml or *.yml files found within any package under the "akitbootstrap" directory
        "": ["*.yaml", "*.yml"],
    },
    # Other parameters like install_requires, author, etc.
)
