from setuptools import setup

setup(
    name='contentexportgw4',
    version='0.1',
    description='Example for extending collective.exportimport',
    url='https://github.com/UPCnet/contentexportgw4.git',
    author='Plone Team',
    author_email='ploneteam@upcnet.es',
    license='GPL version 2',
    packages=['contentexportgw4'],
    include_package_data=True,
    zip_safe=False,
    entry_points={'z3c.autoinclude.plugin': ['target = plone']},
    install_requires=[
        "setuptools",
        "collective.exportimport",
        ],
    )
