from setuptools import setup, find_packages

entry_points = {
	'console_scripts': [
		"chat_client = nti.integrationtests.runners.chat_client",
		"run_integration_tests = nti.integrationtests.runners.run_integration_tests:main",
		"run_generalpurpose_tests = nti.integrationtests.runners.run_generalpurpose_tests:main",
	],
}

setup(
	name = 'nti.integrationtests',
	version = '0.0',
	
	description = 'NextThought Dataserver Integration tests',
	classifiers=[
			"Development Status :: 2 - Pre-Alpha",
			"Intended Audience :: Developers",
			"Operating System :: OS Independent",
			"Programming Language :: Python"
		],

	install_requires = [ 'nti.dataserver',
						 'coverage',
						],
	
	packages = find_packages('src'),
	package_dir = {'': 'src'},
	include_package_data = True,
	namespace_packages=['nti',],
	zip_safe = False,
	entry_points = entry_points
	)
