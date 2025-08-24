# SSHUP

A Simple SSH Manager

## Usage:
```
Commands:
  sshup             Start the interactive menu
  sshup --edit      Open the config file in your default editor
  sshup --list      List configured servers
  sshup --cmd       Run a command on the host
  sshup --version   Get sshup version number
  sshup --help      Show this help message

Flags:
  -e, --edit    Edit the config file
  -l, --list    List all servers
  -c, --cmd     Run command on host
  -v, --version Show version number
  -h, --help    Show this help message
```

## Config:

First run will create a default config file in the below path, make sure to edit with the correct credentials:
```
~/.sshup/config.yaml
```

## Compatibility:
- **OS**: Windows 11, macOS, Linux, FreeBSD, OpenBSD
- **Shell**: Bash, zsh, sh
- **Python**: 3.9, 3.10, 3.11, 3.12

## Dev Setup

Install from local repo:
```
sudo pip3 install . --break-system-packages
```

## Features:
- [x] Interactive TUI
- [x] Cross Platform (Windows, Linux, Mac, BSD)
- [x] YAML Based Config
- [ ] `.ssh/config` Config Editing
- [x] Command Exection on Host
- [ ] Command Execution on Multiple Hosts Simultaneously
- [ ] Search & Filtering
- [ ] Grouping
- [ ] Autocompletion
- [ ] History
- [ ] Key Management

## ToDo:
- Version 1.0 [Roadmap](./docs/v1-roadmap.md)
