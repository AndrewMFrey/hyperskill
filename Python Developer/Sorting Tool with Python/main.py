import argparse

from collections import defaultdict


class SortingTool:
    def __init__(self, data_type: str, sorting_type: str, input_file: str, output_file: str):
        self.data_type = data_type
        self.sorting_type = sorting_type
        self.input_file = input_file
        self.output_file = open(output_file, 'w') if output_file else output_file
        self.lines = []
        self.read_input()
        if self.data_type == 'word':
            self.parse_word()
        elif self.data_type == "long":
            self.parse_long()
        else:
            self.parse_line()
        if self.output_file:
            self.output_file.close()

    def read_input(self):
        if self.input_file:
            with open(self.input_file, 'r') as infile:
                self.lines = infile.readlines()
        else:
            while True:
                try:
                    self.lines.append(input())
                except EOFError:
                    break

    def write_output(self, line: str):
        if self.output_file:
            self.output_file.write(f"{line}\n")
        else:
            print(line)

    def parse_long(self):
        """
        Parse provided lines as if they were ints. Prints an error message when unable to cast an item as an int.
        If natural sorting is enabled, sorts by input, then outputs all ints parsed in input.
        If countBy sorting is enabled, sorts by int, then int count, then outputs each int and its occurrence
        rate.

        :return:
        """
        int_dict = defaultdict(int)
        for line in self.lines:
            line_list = line.split()
            for line_int in line_list:
                try:
                    int_dict[int(line_int)] += 1
                except ValueError:
                    print(f'"{line_int}" is not a long. It will be skipped.')
        total = sum(int_dict.values())
        self.write_output(f"Total numbers: {total}.")
        if self.sorting_type == 'natural':
            all_sorted_ints = []
            for k, v in sorted(int_dict.items(),
                               key=lambda item: item[0]):
                for _ in range(v):
                    all_sorted_ints.append(str(k))
            sorted_ints = ' '.join(all_sorted_ints)
            self.write_output(f'Sorted data: {sorted_ints}')
        else:
            for k, v in sorted(
                    sorted(int_dict.items()),
                    key=lambda item: item[1]):
                occurrence_rate = int(float(v) / sum(int_dict.values()) * 100)
                self.write_output(f'{k}: {v} time(s), {occurrence_rate}%)')

    def parse_line(self):
        """
        Parse provided lines.
        If natural sorting is enabled, sorts by input, then outputs all ints parsed in input.
        If countBy sorting is enabled, sorts by line, then line count, then outputs each line and its
        occurrence rate.

        :return:
        """
        line_dict = defaultdict(int)
        for line in self.lines:
            line_dict[line.rstrip()] += 1
        total = sum(line_dict.values())
        self.write_output(f"Total lines: {total}.")
        if self.sorting_type == 'natural':
            all_sorted_lines = []
            for k, v in sorted(line_dict.items()):
                for _ in range(v):
                    all_sorted_lines.append(k)
            sorted_lines = '\n'.join(all_sorted_lines)
            self.write_output(f'Sorted data:\n{sorted_lines}')
        else:
            for k, v in sorted(
                    sorted(line_dict.items()),
                    key=lambda item: item[1]):
                occurrence_rate = int(float(v) / sum(line_dict.values()) * 100)
                self.write_output(f'{k}: {v} time(s), {occurrence_rate}%)')

    def parse_word(self):
        """
        Parse provided lines as words between white space.
        If natural sorting is enabled, sorts by word count, then outputs all words parsed in input.
        If countBy sorting is enabled, sorts by word, then word count, then outputs each int and its occurrence rate.

        :return:
        """
        word_dict = defaultdict(int)
        for line in self.lines:
            line_list = line.split()
            for line_word in line_list:
                word_dict[line_word] += 1
        total = sum(word_dict.values())
        self.write_output(f"Total words: {total}.")
        if self.sorting_type == 'natural':
            all_sorted_words = []
            for k, v in sorted(word_dict.items(),
                               key=lambda item: item[1]):
                for _ in range(v):
                    all_sorted_words.append(k)
            sorted_words = ' '.join(all_sorted_words)
            self.write_output(f'Sorted data: {sorted_words}')
        else:
            for k, v in sorted(
                    sorted(word_dict.items()),
                    key=lambda item: item[1]):
                occurrence_rate = int(float(v) / sum(word_dict.values()) * 100)
                self.write_output(f'{k}: {v} time(s), {occurrence_rate}%)')



if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-dataType',
                            nargs='?',
                            const=None,
                            choices=['long', 'line', 'word'],
                            default='long')
    arg_parser.add_argument('-sortingType',
                            nargs='?',
                            const=None,
                            choices=['natural', 'byCount'],
                            default='natural')
    arg_parser.add_argument('-inputFile')
    arg_parser.add_argument('-outputFile')
    args, unknown = arg_parser.parse_known_args()
    if unknown:
        for item in unknown:
            print(f"{item} is not a valid parameter. It will be skipped.")
    if not args.dataType:
        print('No data type defined!')
    if not args.sortingType:
        print('No sorting type defined!')
    if args.dataType and args.sortingType:
        SortingTool(data_type=args.dataType,
                    sorting_type=args.sortingType,
                    input_file=args.inputFile,
                    output_file=args.outputFile)