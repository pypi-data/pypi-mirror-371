import argparse
import sys

VOWEL_MAP = {
    'a': '1', 'e': '2', 'i': '3', 'o': '4', 'u': '5',
    'A': '1', 'E': '2', 'I': '3', 'O': '4', 'U': '5',
}

def to_okkie(text: str, concat: bool = False) -> str:
    """
    Convert input text into okkie language.
    """
    tokens = []
    for ch in text:
        if ch.isalpha():
            if ch in VOWEL_MAP:
                tokens.append(VOWEL_MAP[ch])
            else:
                tokens.append(f"{ch}okkie")
        else:
            tokens.append(ch)

    if concat:
        return ''.join(tokens)
    else:
        result = []
        for tok in tokens:
            if tok.isspace():
                result.append(tok)
            else:
                if result and not result[-1].endswith((' ', '\n', '\t')):
                    result.append(' ')
                result.append(tok)
        return ''.join(result).lstrip()

def main():
    parser = argparse.ArgumentParser(description="Convert text into okkie language.")
    parser.add_argument("text", nargs="*", help="Text/words to convert. Empty = read from stdin.")
    parser.add_argument("--concat", action="store_true", help="Output without spaces between tokens.")
    args = parser.parse_args()

    if args.text:
        input_text = ' '.join(args.text)
    else:
        input_text = sys.stdin.read()

    print(to_okkie(input_text, concat=args.concat))
