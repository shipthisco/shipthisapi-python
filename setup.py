import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='shipthisapi-python',  
     version='1.2.0',
     author="Mayur Rawte",
     author_email="mayur@shipthis.co",
     description="ShipthisAPI utility package",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/shipthisco/shipthisapi-python",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     entry_points={"console_scripts": []}
 )