# typer

Typing practice in your terminal. Like [monkeytype](https://monkeytype.com), but in the CLI.

```
brew tap willgerstung/typecli
brew install typer
```

Then just run:

```
typer
```

## Usage

```
typer              # interactive mode menu
typer -t 15        # 15 second test
typer -t 60        # 60 second test
typer -w 25        # 25 word test
```

## Controls

| Key       | Action        |
|-----------|---------------|
| `tab`     | restart test  |
| `esc`     | back to menu  |
| `q`       | quit (results)|

## Install from source

```
pip install .
```

## Zero dependencies

Pure Python. Only uses `curses` (built-in). Works on macOS and Linux out of the box.
