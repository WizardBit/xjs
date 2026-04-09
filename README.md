# 🪄 XJS

[![xjs](https://snapcraft.io/xjs/badge.svg)](https://snapcraft.io/xjs)

> [!NOTE]
> An updated fork of [xjs](https://github.com/nniehoff/xjs)
> To use with Juju 2.x use the legacy/stable channel

A tool for parsing seemingly complex juju 3.x status yaml/json files offline.
This eliminates the hassle of waiting for `juju status` in large environments.

## 👨‍💻 Installation

```bash
sudo snap install xjs
```

## ⌨️ Usage

With yaml:

```bash
juju status --format yaml > juju-status.yaml
xjs juju-status.yaml
```

With json:

```bash
juju status --format json > juju-status.json
xjs juju-status.json
```

Options:

```bash
Usage: xjs [OPTIONS] <status files>

  xjs parses a juju status yaml/json and displays the information in a user
  friendly form highlighting specific fields of specific interest.

Options:
  --application <application name>
                                  Show only the application with the specified
                                  name
  --controller <controller name>  Show only the controller with the specified
                                  name
  -h, --hide-scale-zero           Hide applications with a scale of 0
  -s, --hide-subordinate-units    Hide subordinate units
  -c, --include-containers        Include Container information
  --machine <machine name>        Show only the machine with the specified
                                  name
  --model <model name>            Show only the model with the specified name
  --no-color                      Remove color from output
  -a, --show-apps                 Show application information
  -m, --show-machines             Show machine information
  -d, --show-model                Show model information
  -n, --show-net                  Show network interface information
  -u, --show-units                Show unit information
  --subordinate <subordinate name>
                                  Show only the subordinate unit with the
                                  specified name
  --unit <unit name>              Show only the unit with the specified name
  --help                          Show this message and exit.
```
