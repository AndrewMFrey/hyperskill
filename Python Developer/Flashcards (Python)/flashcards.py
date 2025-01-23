import sys
import random
import re
import argparse

from io import StringIO


class AddDuplicateCardError(Exception):
    def __init__(self, card: str):
        super().__init__(f'''The card "{card}" already exists. Try again:''')


class AddDuplicateDefinitionError(Exception):
    def __init__(self, definition: str):
        super().__init__(f'''The definition "{definition}" already exists. Try again:''')


class AskMismatchedGuessError(Exception):
    def __init__(self, correct: str, mismatch: str):
        super().__init__(f'''Wrong. The right answer is "{correct}", but your definition is correct for "{mismatch}".''')


class AskWrongAnswerError(Exception):
    def __init__(self, correct_answer: str):
        super().__init__(f'''Wrong. The right answer is "{correct_answer}"''')


class RemoveCardError(Exception):
    def __init__(self, card: str):
        super().__init__(f'''Can't remove "{card}": there is no such card.''')


class TerminalLogger:
    def __init__(self):
        """
        Class built to simultaneously:
            - read from stdin, then copy to a logging file stream
            - write output to stdout and to a logging file stream
        """
        self.terminal_in = sys.stdin
        self.terminal_out = sys.stdout
        self.in_memory_log = StringIO()

    def read(self) -> str:
        terminal_text = self.terminal_in.readline()
        self.in_memory_log.write(terminal_text)
        return terminal_text.rstrip()

    def write(self, text=''):
        text = str(text) + '\n'
        self.terminal_out.write(text)
        self.in_memory_log.write(text)

    def save_log(self) -> str:
        return self.in_memory_log.getvalue()


class FlashCards:
    def __init__(self, args: dict):
        self.card_dict = {}
        random.seed()
        self.memory_log = TerminalLogger()
        self.auto_import = args.get('import_from')
        if self.auto_import:
            self.import_file(self.auto_import)
        self.auto_export = args.get('export_to')
        self.process_choices()

    def process_choices(self):
        while True:
            self.memory_log.write("Input the action (add, remove, import, export, ask, exit, log, hardest card, "
                                  "reset stats):")
            choice = self.memory_log.read()
            if choice == "add":
                self.add_card()
            elif choice == "remove":
                self.remove_card()
            elif choice == "import":
                self.import_file()
            elif choice == "export":
                self.export_file()
            elif choice == "ask":
                self.ask()
            elif choice == "log":
                self.log_text()
            elif choice == "hardest card":
                self.hardest_card()
            elif choice == "reset stats":
                self.reset_stats()
            elif choice == "exit":
                self.memory_log.write("Bye bye!")
                if self.auto_export:
                    self.export_file(self.auto_export)
                return
            self.memory_log.write()

    def add_card(self):
        self.memory_log.write("The card:")
        while True:
            try:
                card = self.memory_log.read()
                if card in self.card_dict:
                    raise AddDuplicateCardError(card)
            except AddDuplicateCardError as err:
                self.memory_log.write(err)
            else:
                break
        self.memory_log.write("The definition of the card:")
        while True:
            try:
                definition = self.memory_log.read()
                for key in self.card_dict.keys():
                    if definition in self.card_dict.get(key).get("definition"):
                        raise AddDuplicateDefinitionError(definition)
            except AddDuplicateDefinitionError as err:
                self.memory_log.write(err)
            else:
                break
        self.card_dict[card] = {"definition": definition,
                                "mistakes": 0}
        self.memory_log.write(f'''The pair ("{card}":"{definition}") has been added.''')

    def remove_card(self):
        try:
            self.memory_log.write("Which card?")
            card = self.memory_log.read()
            if card not in self.card_dict:
                raise RemoveCardError(card)
        except RemoveCardError as err:
            self.memory_log.write(err)
        else:
            self.card_dict.pop(card)
            self.memory_log.write("The card has been removed.")

    def import_file(self, import_from: str = None):
        if import_from:
            import_file_name = import_from
        else:
            self.memory_log.write("File name:")
            import_file_name = self.memory_log.read()
        n = 0
        try:
            with open(import_file_name, "r", encoding="utf-8") as import_file:
                for line in import_file:
                    line_split = re.split(r'\|', line)
                    self.card_dict[line_split[0]] = {"definition": line_split[1],
                                                     "mistakes": int(line_split[2])}
                    n += 1
        except FileNotFoundError:
            self.memory_log.write("File not found.")
        else:
            self.memory_log.write(f"{n} cards have been loaded.")

    def export_file(self, export_to: str = None):
        if export_to:
            export_file_name = export_to
        else:
            self.memory_log.write("File name:")
            export_file_name = self.memory_log.read()
        with open(export_file_name, "w", encoding="utf-8") as export_file:
            for key in self.card_dict:
                export_file.write(f"{key}|"
                                  f"{self.card_dict.get(key).get("definition")}|"
                                  f"{self.card_dict.get(key).get("mistakes")}\n")
        self.memory_log.write(f"{len(self.card_dict)} cards have been saved.")

    def ask(self):
        self.memory_log.write("How many times to ask?")
        times = int(self.memory_log.read())
        for _ in range(times):
            card = random.choice(sorted(self.card_dict))
            self.memory_log.write(f'''Print the definition of "{card}":''')
            try:
                card_answer = self.memory_log.read()
                if card_answer == self.card_dict.get(card).get("definition"):
                    self.memory_log.write("Correct!")
                else:
                    self.card_dict[card]["mistakes"] += 1
                    for key in self.card_dict:
                        if card_answer == self.card_dict.get(key).get("definition"):
                            raise AskMismatchedGuessError(self.card_dict.get(card)
                                                          .get("definition"),
                                                          self.card_dict.get(key)
                                                          .get("definition"))
                    else:
                        raise AskWrongAnswerError(self.card_dict.get(card).get("definition"))
            except (AskMismatchedGuessError, AskWrongAnswerError) as err:
                self.memory_log.write(err)

    def log_text(self):
        self.memory_log.write("File name:")
        log_path = self.memory_log.read()
        with open(log_path, 'w') as log_out:
            log_out.write(self.memory_log.save_log())
        self.memory_log.write("The log has been saved.")

    def hardest_card(self):
        max_value = 0
        max_cards = []
        output_cards = ''
        for key in self.card_dict:
            if self.card_dict.get(key).get("mistakes") == 0:
                pass
            elif self.card_dict.get(key).get("mistakes") > max_value:
                max_value = self.card_dict.get(key).get("mistakes")
                max_cards = [key]
            elif self.card_dict.get(key).get("mistakes") == max_value:
                max_cards.append(key)
        for card in max_cards:
            output_cards += f'''"{card}", '''
        output_cards = output_cards[:-2]
        if len(max_cards) == 0:
            self.memory_log.write("There are no cards with errors.")
        elif len(max_cards) == 1:
            self.memory_log.write(f"""The hardest card is {output_cards}. You have {max_value} errors answering it.""")
        elif len(max_cards) >= 2:
            self.memory_log.write(f"""The hardest cards are {output_cards}.""")

    def reset_stats(self):
        for key in self.card_dict:
            self.card_dict[key]["mistakes"] = 0
        self.memory_log.write("Card statistics have been reset.")


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--import_from")
    arg_parser.add_argument("--export_to")
    FlashCards(vars(arg_parser.parse_args()))