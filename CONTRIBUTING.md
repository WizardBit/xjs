## Development Setup

```sh
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Styling checks

```sh
pip install flake8 pycodestyle
pycodestyle xjs/
flake8 xjs/
```

## Building the Snap

```sh
sudo snap install snapcraft --classic

snapcraft pack

sudo snap install --devmode xjs_*.snap
```
