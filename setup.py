from setuptools import setup, find_packages

setup(
    name="pulsardb",
    version="0.1.0",
    description="Pulsar Observation Database",
    author="David Kaplan",
    author_email="kaplan@uwm.edu",
    url="",
    packages=find_packages(),
    entry_points={},
    install_requires=["astropy", "pandas", "loguru", "requests"],
    python_requires=">=3.7",
    #package_data={"simpleRM": ["data/*.*"]},
    #include_package_data=True,
    zip_safe=False,
)
