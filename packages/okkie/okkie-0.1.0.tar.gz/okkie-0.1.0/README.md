# okkie

Convert text into **okkie language**, a playful word game:

- Consonants → letter + "okkie"
- Vowels → replaced by numbers:
  - a = 1
  - e = 2
  - i = 3
  - o = 4
  - u = 5

## Installation

From PyPI:

```bash
pip install okkie
```

## Usage

```bash
okkie Hello world
# → Hokkie 2 lokkie lokkie 4 wokkie 4 rokkie lokkie dokkie

okkie music
# → mokkie 5 sokkie 3 sokkie

okkie programming
# → pokkie rokkie 4 gokkie rokkie 1 mokkie mokkie 3 nokkie gokkie
```

### Options

* `--concat`: output without spaces between tokens

Example:

```bash
okkie --concat Hello
# → Hokkie2lokkielokkie4
```
