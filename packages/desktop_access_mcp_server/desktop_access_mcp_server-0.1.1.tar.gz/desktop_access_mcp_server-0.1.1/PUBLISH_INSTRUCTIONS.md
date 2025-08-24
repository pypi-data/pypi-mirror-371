# To publish the package to PyPI, run the following command:
# python -m flit publish

# If you need to specify a repository or have multiple repositories configured:
# python -m flit publish --repository pypi

# Make sure you have your PyPI credentials configured in ~/.pypirc or use tokens.
# The .pypirc file should look like this:
#
# [distutils]
# index-servers = pypi
#
# [pypi]
# repository = https://upload.pypi.org/legacy/
# username = __token__
# password = pypi-your-api-token-here

# For test PyPI:
# [distutils]
# index-servers = pypi testpypi
#
# [pypi]
# repository = https://upload.pypi.org/legacy/
# username = __token__
# password = pypi-your-production-token-here
#
# [testpypi]
# repository = https://test.pypi.org/legacy/
# username = __token__
# password = pypi-your-test-token-here