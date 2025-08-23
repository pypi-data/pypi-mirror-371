from setuptools import setup, find_packages

VERSION = '1.0.0' 
DESCRIPTION = 'uwgds: A Python package for creating GDS files'

# Setting up
setup(
        name="uwgds", 
        version=VERSION,
        author="Ameya Velankar",
        author_email="<velankar@uw.edu>",
        description=DESCRIPTION,
        packages=find_packages(),
        install_requires=["numpy","matplotlib","gdsfactory"], 

        keywords=['python', 'gds'],
        classifiers= []
)