# CLI for POFile.io

An easy-to-use CLI tool for translating PO files with POFile.io.

## Description

This CLI tool automatically locates `.po` files in your project and fills in missing translations using the POFile.io API service. It's designed to streamline the process of managing translations in software projects.

## Getting Started

### Prerequisites

- Python 3.7 or later

### Installation

1. Activate your project's virtual environment.
2. Install the CLI with:

    ```bash
    pip install pofile-cli
    ```

   This will make the `pofile` command available.

3. Create an account at [POFile.io](https://pofile.io), log in, and copy your API key from the dashboard.

4. Set your API key by exporting it as an environment variable (recommended) or passing it directly with each command:

    ```bash
    export POFILE_API_KEY=<your_api_key>
    ```

### Usage

To populate all `.po` files in the current project with translations, use:

```bash
pofile populate
```

#### Additional Options

**Specify a Directory:** To search for .po files in a specific directory, provide the path:

```bash
pofile populate <directory>
```

**Set Maximum Directory Depth:** Control how deep the tool searches within nested directories:

```bash
pofile populate --dir-depth <depth>
```

**Skip Confirmation Prompt:** Automatically proceed without a confirmation prompt:

```bash
pofile populate -y
```

**Use an API Key Directly:** If you prefer not to use an environment variable, you can specify your API key:

```bash
pofile populate --api-key <your_api_key>
```

## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.