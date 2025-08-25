# mdformat-vuepress

An [mdformat](https://github.com/executablebooks/mdformat) plugin to preserve VuePress-style `:::` containers when formatting Markdown files.

## Installation

```bash
pip install mdformat-vuepress
```

Or with uv:

```bash
uv add mdformat-vuepress
```

## Usage

After installation, the plugin will automatically be available to mdformat. VuePress-style containers will be preserved during formatting:

```markdown
::: tip
This is a tip container that will be preserved.
:::

::: warning
This is a warning container.
:::

::: danger
This is a danger container.
:::
```

## Features

- Preserves VuePress container syntax (`:::`)
- Maintains container content formatting
- Compatible with mdformat's formatting rules
- Supports all VuePress container types

## Development

This plugin is built using the mdformat plugin system and uses markdown-it-py for parsing.

## License

MIT License - see [LICENSE](LICENSE) file for details.