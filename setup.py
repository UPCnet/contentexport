from setuptools import setup

setup(
    name='contentexport',
    version='0.1',
    description='Example for extending collective.exportimport',
    url='https://github.com/UPCnet/contentexport.git',
    author='Plone Team',
    author_email='ploneteam@upcnet.es',
    license='GPL version 2',
    packages=['contentexport'],
    include_package_data=True,
    zip_safe=False,
    entry_points={'z3c.autoinclude.plugin': ['target = plone']},
    install_requires=[
        "setuptools",
        "collective.exportimport",
        ],
    )
