import codecs
from setuptools import setup, find_packages

entry_points = {
	'console_scripts': [
		'nti_run_performance_tests = nti.integrationtests.performance.eval.main:main',
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
		"License :: OSI Approved :: Apache Software License"
		"Programming Language :: Python"
	],
	install_requires = [
		'setuptools',
		'coverage',
		'httpie'
		#'mmstats', # neat idea, not currently used and pulls in many deps, so commented out until used
	],
	extras_require = {
		'PDF': ['pyobjc >= 2.5.1', 'pyobjc-core >= 2.5.1'] # Quartz is used for pdfs
	},
	packages = find_packages('src'),
	package_dir = {'': 'src'},
	include_package_data = True,
	namespace_packages=['nti',],
	zip_safe = False,
	entry_points = entry_points
)
