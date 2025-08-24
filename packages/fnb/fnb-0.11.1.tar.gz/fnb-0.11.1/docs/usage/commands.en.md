# Basic Commands

The fnb tool provides the following main commands for backup workflow management.

## init

Use this command first to create fnb configuration files (`fnb.toml` and `.env`).

```bash
fnb init [kind] [--force]
```

Generates initial configuration files in the current directory.

**Arguments**:

- `kind` - Type of configuration to generate: `all` (default), `config`, or `env`

**Options**:

- `--force`, `-f` - Overwrite existing configuration files without confirmation

**Examples**:

```bash
# Generate all configuration files
fnb init

# Generate only config file
fnb init config

# Generate only environment file
fnb init env

# Force overwrite existing files
fnb init --force
```

## status

Display a summary of all configured fetch and backup tasks.

```bash
fnb status [--config PATH]
```

Shows the current status of all enabled tasks, including source and target paths.

**Options**:

- `--config`, `-c` - Path to configuration file (auto-detected if not specified)

**Examples**:

```bash
# Show status with auto-detected config
fnb status

# Use specific config file
fnb status --config /path/to/config.toml
```

## version

Display the current version of the fnb tool.

```bash
fnb version
```

Shows the installed version number for troubleshooting and support.

## fetch

Fetch data from a remote server to local storage using rsync over SSH.

```bash
fnb fetch LABEL [--dry-run] [--create-dirs] [--ssh-password PASSWORD] [--config PATH]
```

Downloads data from a remote server based on the task configuration.

**Arguments**:

- `LABEL` - Task label that identifies the fetch configuration in the config file

**Options**:

- `--dry-run`, `-n` - Preview the operation without making changes
- `--create-dirs`, `-f` - Create target directory if it doesn't exist
- `--ssh-password`, `-p` - SSH password for authentication (overrides .env)
- `--config`, `-c` - Path to configuration file

**Examples**:

```bash
# Fetch logs from remote server
fnb fetch logs

# Preview fetch operation
fnb fetch logs --dry-run

# Fetch with SSH password and auto-create directories
fnb fetch logs --ssh-password mypass --create-dirs
```

## backup

Backup local data to external storage or cloud destinations using rsync.

```bash
fnb backup LABEL [--dry-run] [--create-dirs] [--config PATH]
```

Copies data from local storage to external destinations.

**Arguments**:

- `LABEL` - Task label that identifies the backup configuration in the config file

**Options**:

- `--dry-run`, `-n` - Preview the operation without making changes
- `--create-dirs`, `-f` - Create source and target directories if they don't exist
- `--config`, `-c` - Path to configuration file

**Examples**:

```bash
# Backup logs to external storage
fnb backup logs

# Preview backup operation
fnb backup logs --dry-run

# Backup with auto-create directories
fnb backup logs --create-dirs
```

## sync

Execute both fetch and backup operations sequentially for a given label.

```bash
fnb sync LABEL [--dry-run] [--create-dirs] [--ssh-password PASSWORD] [--config PATH]
```

Runs both fetch (remote → local) and backup (local → external) in sequence.

**Arguments**:

- `LABEL` - Task label that must exist in both fetch and backup configurations

**Options**:

- `--dry-run`, `-n` - Preview both operations without making changes
- `--create-dirs`, `-f` - Create directories for both operations if needed
- `--ssh-password`, `-p` - SSH password for fetch operation
- `--config`, `-c` - Path to configuration file

**Examples**:

```bash
# Complete sync pipeline
fnb sync logs

# Preview complete sync pipeline
fnb sync logs --dry-run

# Sync with authentication and directory creation
fnb sync logs --ssh-password mypass --create-dirs
```

## Global Options

All commands support these global options:

- `--help` - Show command help and usage information
- `--config PATH` - Specify configuration file path (auto-detected by default)

## Configuration File

The `fnb.toml` configuration file defines tasks in sections:

- `[fetch.LABEL]` - Remote fetch tasks
- `[backup.LABEL]` - Local backup tasks

Each task requires: `label`, `summary`, `host`, `source`, `target`, `options`, and `enabled` fields.

## Error Handling

Common error scenarios and solutions:

- **Config file not found**: Run `fnb init` to create initial configuration
- **Task label not found**: Check task labels with `fnb status`
- **SSH authentication failed**: Verify SSH credentials and host connectivity
- **Directory not found**: Use `--create-dirs` option to create missing directories
- **Permission denied**: Check file permissions and ownership

For detailed configuration examples, see the [Configuration Guide](configuration.md).