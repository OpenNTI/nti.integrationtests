from setuptools import setup, find_packages

entry_points = {
			
	'console_scripts': [
		"nti_chat_client = nti.integrationtests.runners.chat_client:main",
		"nti_run_integration_tests = nti.integrationtests.runners.run_integration_tests:main",
		"nti_run_general_purpose_tests = nti.integrationtests.runners.run_generalpurpose_tests:main"
	],
}

setup(
	name = 'nti.integrationtests',
	version = '0.0',
	author = 'NTI',
	description = 'NextThought Dataserver Integration tests',
	classifiers=[
			"Development Status :: 2 - Pre-Alpha",
			"Intended Audience :: Developers",
			"Operating System :: OS Independent",
			"Programming Language :: Python"
		],

	install_requires = [ 'nti.dataserver',
						 'coverage',
						 'repoze.profile'
						],
	
	packages = find_packages('src'),
	package_dir = {'': 'src'},
	include_package_data = True,
	namespace_packages=['nti',],
	zip_safe = False,
	entry_points = entry_points
	)
