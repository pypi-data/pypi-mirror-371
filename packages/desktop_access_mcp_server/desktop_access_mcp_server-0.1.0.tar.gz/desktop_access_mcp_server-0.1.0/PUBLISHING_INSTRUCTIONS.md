# How to Publish to PyPI

## Prerequisites

1. Create an account on PyPI (https://pypi.org/account/register/) if you don't have one
2. Generate an API token:
   - Go to https://pypi.org/manage/account/
   - Scroll down to "API tokens"
   - Click "Add API token"
   - Give it a name like "desktop-access-mcp-server"
   - Set scope to "Upload packages"
   - Copy the token (you won't see it again)

## Publishing Steps

1. Create a `.pypirc` file in your home directory with your credentials:
   ```ini
   [distutils]
   index-servers = pypi

   [pypi]
   username = __token__
   password = pypi-your-api-token-here
   ```

2. Alternatively, you can use twine with environment variables:
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-your-api-token-here
   ```

3. Upload the package:
   ```bash
   cd /home/hemang/Documents/GitHub/desktop-access-mcp-server
   twine upload dist/*
   ```

## Verification

After publishing, you can verify the package is available at:
https://pypi.org/project/desktop-access-mcp-server/

## Installing Your Published Package

Once published, users can install your package with:
```bash
pip install desktop-access-mcp-server
```

Or use it directly with uvx:
```bash
uvx desktop-access-mcp-server
```