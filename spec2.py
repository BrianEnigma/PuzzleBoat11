#!/usr/bin/env python3

import json
import os
import re
import requests
import sys

URL = 'https://www.pandamagazine.com/island11/puzzles/spectral_analysis.php'
WORD = sys.argv[1] if len(sys.argv) > 1 else None

if WORD is None:
    print('Specify a word')
    sys.exit(1)

class LetterAnalyzer:
    def __init__(self):
        self.positions = []
        if self.load_state() == False:
            self.initialize_state()

    def initialize_state(self):
        print('Initializing state...')
        # Letter to score mapping.
        scores = {}
        for i in range(26):
            scores[chr(ord('a') + i)] = -1
        # Positions has six elements.
        self.positions = []
        for i in range(6):
            self.positions.append(scores.copy())

    def save_state(self):
        print('Saving state...')
        with open('state.json', 'w') as f:
            f.write(json.dumps(self.positions))

    def load_state(self):
        if os.path.exists('state.json') == False:
            return False
        try:
            with open('state.json', 'r') as f:
                print('Loading saved state...')
                self.positions = json.loads(f.read())
            return True
        except:
            return False

    def add_word(self, word: str, result: str):
        if len(word) != 6 or len(result) != 6:
            print('Invalid string length')
            os.exit(1)
        for i in range(6):
            print('Saving letter {0} at position {1} as {2}'.format(word[i], i, result[i]))
            letter = word[i]
            value = result[i]
            self.positions[i][letter] = value

    def write_report(self):
        with open('report.md', 'w') as f:
            # Write headers
            f.write("|   | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | A | B | C | D | E | F | unknown |\n")
            f.write("| -:- | -:- | -:- | -:- | -:- | -:- | -:- | -:- | -:- | -:- | -:- | -:- | -:- | -:- | -:- | -:- | -:- | -:- |\n")
            # Each row
            for pos in range(6):
                f.write("| {0} | ".format(pos + 1))
                # The main 16 hex columns
                for score in range(16):
                    matches = ''
                    score_str = '{0:x}'.format(score).upper()
                    for letter in range(26):
                        letter_str = chr(ord('a') + letter)
                        if self.positions[pos][letter_str] == score_str:
                            matches += letter_str
                    f.write(' {0} | '.format(matches))
                no_match = ''
                for letter in range(26):
                    if self.positions[pos][chr(ord('a') + letter)] == -1:
                        no_match += chr(ord('a') + letter)
                f.write(' {0} | '.format(no_match))
                f.write("\n")


def extract(s: str):
    s = re.sub(r'<style>.*?</style>', '', s, flags=re.DOTALL)
    s = re.sub(r'<[^>]*>', '', s, flags=re.DOTALL)
    if s.find('Invalid subject') != -1:
        print('Invalid word given.')
        return None
    s = re.sub(r'^.*\.\.\.\.', '', s, flags=re.DOTALL)
    s = re.sub(r'Enter.*', '', s, flags=re.DOTALL)
    return s.strip()

analyzer = LetterAnalyzer()
response_string = None
try:
    response = requests.post(URL, data={'testword': WORD})
    response.raise_for_status()
    response_string = extract(response.text)
    print(response_string)
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

if response_string is not None:
    [score, value] = response_string.split(' ')
    value = value.replace('#', '').strip()
    analyzer.add_word(WORD, value)
    analyzer.save_state()
    analyzer.write_report()
    os.system('cat report.md| gawk -f format_table.awk > report2.md')
    os.rename('report2.md', 'report.md')
    os.system('cat report.md')
