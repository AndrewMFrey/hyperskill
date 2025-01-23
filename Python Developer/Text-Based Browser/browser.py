import sys
import os
import re
import requests

from bs4 import BeautifulSoup
from colorama import Fore


class TextBasedBrowser:
    def __init__(self, directory: str):
        self.headers = {'Accept-Language': 'en-US,en;q=0.5'}
        self.directory = directory
        self.keep_processing = True
        self.browser_history = []
        self.prior_key = ''
        self.valid_tags = ["p", "a", "ul", "al", "li",
                           "h1", "h2", "h3", "h4", "h5", "h6"]
        if os.path.exists(self.directory):
            pass
        else:
            os.mkdir(self.directory)
        while self.keep_processing:
            self.process_input()

    def process_input(self):
        # Drop to lower case
        input_text = input().lower()
        # Immediately exit if that's the case
        if input_text == "exit":
            self.keep_processing = False
            return
        else:
            if input_text == "back":
                input_text = self.browser_history.pop() if len(self.browser_history) > 0 else None
            if input_text is None:
                return
            if match := re.search(r'.+\..+', input_text):
                request = requests.get(f"https://{input_text}", headers=self.headers)
                # Keep only the text before the first '.'
                split_text = input_text.split(sep='.', maxsplit=1)[0] if input_text.split(sep='.', maxsplit=1) else input_text
                # Get our output path
                file_path = os.path.join(self.directory, split_text)
                if request.status_code == 200:
                    soup = BeautifulSoup(request.content, 'html.parser')
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as output_file:
                            print(''.join(output_file.readlines()))
                    else:
                        with open(file_path, 'w', encoding='utf-8') as output_file:
                            for text_match in soup.find_all(self.valid_tags):
                                if text_match.name == 'a':
                                    output_text = f"{Fore.BLUE}{text_match.text}"
                                else:
                                    output_text = f"{Fore.WHITE}{text_match.text}"
                                output_file.write(f"{output_text}\n")
                                print(output_text)
                    self.browser_history.append(self.prior_key)
                    self.prior_key = split_text
                else:
                    print("Invalid URL")
            else:
                print("Invalid URL")


if __name__ == '__main__':
    if len(sys.argv) == 2:
        TextBasedBrowser(directory=sys.argv[1])