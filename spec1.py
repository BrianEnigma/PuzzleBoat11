#!/usr/bin/env python3
import requests
import sys
import re

URL = 'https://www.pandamagazine.com/island11/puzzles/spectral_analysis.php'
WORD = sys.argv[1] if len(sys.argv) > 1 else None

if WORD is None:
    print('Specify a word')
    sys.exit(1)

def extract(s: str):
    s = re.sub(r'<style>.*?</style>', '', s, flags=re.DOTALL)
    s = re.sub(r'<[^>]*>', '', s, flags=re.DOTALL)
    if s.find('Invalid subject') != -1:
        print('Invalid word given.')
        return None
    s = re.sub(r'^.*\.\.\.\.', '', s, flags=re.DOTALL)
    s = re.sub(r'Enter.*', '', s, flags=re.DOTALL)
    return s.strip()

try:
    response = requests.post(URL, data={'testword': WORD})
    response.raise_for_status()
    print(extract(response.text))
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
