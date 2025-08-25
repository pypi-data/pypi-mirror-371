# jupy_sqlite_extension

JupyterLab extension for SQLite execution based on cell metadata without magic

This extension is composed of a Python package named `jupy_sqlite_extension`
for the server extension and a NPM package named `jupy-sqlite-extension`
for the frontend extension.

## Requirements

- JupyterLab >= 4.4.0

## Install

To install the extension, execute:

```bash
pip install jupy_sqlite_extension
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall jupy_sqlite_extension
```

## Usage

This extension allows you to execute SQLite queries directly in notebook cells without magic commands. To use it:

### 1. Set Cell Metadata

For any code cell where you want to run SQL, you need to add metadata:

```json
{
  "sql_cell": true,
  "db_file": "path/to/your/database.db"
}
```

The DB file path must be relative to the notebook's directory for security.

Alternatively, you can set the language metadata:

```json
{
  "language": "sql",
  "db_file": "path/to/your/database.db"
}
```

### 2. Write Your SQL Query

Write your SQL query in the cell:

```sql
SELECT * FROM customers LIMIT 10;
```

### 3. Execute the Cell

Run the cell (Shift+Enter) and the extension will:
- Execute your SQL query against the specified database
- Display results in a formatted ASCII table for SELECT queries
- Show row count information for INSERT/UPDATE/DELETE operations
- Display any error messages if the query fails

### Important Notes

- **Database file paths must be relative** to the notebook's directory for security
- The database file must exist before running queries
- Results are limited to 25 rows by default (with truncation notice if exceeded)
- Only SQLite databases are supported

## Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter server extension list
```

If the server extension is installed and enabled, but you are not seeing
the frontend extension, check the frontend extension is installed:

```bash
jupyter labextension list
```

## Contributing

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the jupy_sqlite_extension directory
# Install package in development mode
pip install -e ".[test]"
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Server extension must be manually installed in develop mode
jupyter server extension enable jupy_sqlite_extension
# Rebuild extension Typescript source after making changes
jlpm build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
# Server extension must be manually disabled in develop mode
jupyter server extension disable jupy_sqlite_extension
pip uninstall jupy_sqlite_extension
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `jupy-sqlite-extension` within that folder.

### Testing the extension

#### Server tests

This extension is using [Pytest](https://docs.pytest.org/) for Python code testing.

Install test dependencies (needed only once):

```sh
pip install -e ".[test]"
# Each time you install the Python package, you need to restore the front-end extension link
jupyter labextension develop . --overwrite
```

To execute them, run:

```sh
pytest -vv -r ap --cov jupy_sqlite_extension
```

#### Frontend tests

This extension is using [Jest](https://jestjs.io/) for JavaScript code testing.

To execute them, execute:

```sh
jlpm
jlpm test
```

#### Integration tests

This extension uses [Playwright](https://playwright.dev/docs/intro) for the integration tests (aka user level tests).
More precisely, the JupyterLab helper [Galata](https://github.com/jupyterlab/jupyterlab/tree/master/galata) is used to handle testing the extension in JupyterLab.

More information are provided within the [ui-tests](./ui-tests/README.md) README.

### Packaging the extension

See [RELEASE](RELEASE.md)
