import ast
import os
import re
import sys

from collections import defaultdict


class StaticCodeAnalyzerAST(ast.NodeVisitor):
    """
    AST Implementation to scan for parameters, variables, and default values.
    """
    def __init__(self):
        self.stats = {
            "variables": defaultdict(list),
            "parameters": defaultdict(list),
            "is_constant_default": defaultdict(list),
        }

    def visit_Name(self, node):
        """
        Stores variable names found during assignment and lines numbers.

        :param node: AST node
        :return:
        """
        if isinstance(node.ctx, ast.Store):
            self.stats["variables"][node.lineno].append(node.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """
        Stores parameter names and line numbers. If the parameter is part of a default value, determines if it is
        constant or not (mutable).

        :param node: AST node
        :return:
        """
        for arg in node.args.args:
            self.stats["parameters"][arg.lineno].append(arg.arg)
        for default in node.args.defaults:
            self.stats["is_constant_default"][node.lineno].append(isinstance(default, ast.Constant))
        self.generic_visit(node)

    def get_parameters(self, line_no: int) -> list:
        """
        Returns a list of parameters for a given line number.

        :param line_no: Line number that is being analyzed as an index to the list.
        :return: List of parameters at the given line number.
        """
        return self.stats["parameters"][line_no]

    def get_variables(self, line_no: int) -> list:
        """
        Returns a list of variables for a given line number.

        :param line_no: Line number that is being analyzed as an index to the list.
        :return: List of variables at the given line number.
        """
        return self.stats["variables"][line_no]

    def get_mutable_defaults(self, line_no: int) -> str|None:
        """
        Returns any mutable defaults for a parameter found at a given line number.
        :param line_no: Line number that is being analyzed as an index to the list.
        :return: str containing a mutable default value.
        """
        for parameter, is_default in zip(self.get_parameters(line_no), self.stats["is_constant_default"][line_no]):
            if is_default:
                pass
            else:
                return parameter

class StaticCodeAnalyzer:
    """
    Static Code Analyzer to scan for lines that do not align to PEP8.
    """
    def __init__(self, path: str):
        self.i = 0
        self.line = ''
        self.empty_line_count = 0
        self.path = path
        with open(self.path, 'r') as infile:
            # Instantiate our AST implementation and load our input file.
            self.sca_ast = StaticCodeAnalyzerAST()
            self.sca_ast.visit(ast.parse(infile.read()))
            # Reset the file back to the start to iterate through.
            infile.seek(0)
            for self.i, self.line in enumerate(infile):
                # increment self.i for printing purposes
                self.i += 1
                # strip out any ending white space
                self.line = self.line.rstrip()
                if self.line:
                    # For non-empty lines, perform validations based on PEP8
                    self.check_line_length()
                    self.check_indentation()
                    self.check_semicolon()
                    self.check_comment_spaces()
                    self.check_todo()
                    self.check_empty_line_count()
                    self.check_def_spacing()
                    self.check_class_def_case()
                    self.check_function_def_case()
                    self.check_arg_case()
                    self.check_variable_case()
                    self.check_mutable_default_arg()
                else:
                    # Increment the empty line counter
                    # Will violate during check_empty_line_count() if the count is above 2.
                    self.empty_line_count += 1

    def check_line_length(self):
        # Line length must be below 80 characters.
        if len(self.line) >= 80:
            print(f"{self.path}: Line {self.i}: S001 Too long")

    def check_indentation(self):
        # If the length of our input line minus the input line after lstrip() is a multiple of 4, we're good.
        if (len(self.line) - len(self.line.lstrip())) % 4 == 0:
            pass
        else:
            print(f"{self.path}: Line {self.i}: S002 Indentation is not a multiple of four")

    def check_semicolon(self):
        # Semicolons are only valid as part of a comment or in a string.
        if match := re.search(r'^([^#])*;(?!\S)', self.line):
            print(f"{self.path}: Line {self.i}: S003 Unnecessary semicolon")

    def check_comment_spaces(self):
        # Strip out anything after the first comment character
        line_split = self.line.split('#')
        uncommented_line = line_split[0]
        # Check for the gap between the last character and what would have been the comment character
        if (len(line_split) > 1 and
                uncommented_line and
                (len(uncommented_line) - len(uncommented_line.rstrip())) < 2):
            print(f"{self.path}: Line {self.i}: S004 At least two spaces required before inline comments")

    def check_todo(self):
        # Scan for any comment containing "TODO" with any case.
        if re.search(r"#.*TODO", self.line, re.IGNORECASE):
            print(f"{self.path}: Line {self.i}: S005 TODO found")

    def check_empty_line_count(self):
        # More than two consecutive blank lines is illegal.
        if self.empty_line_count > 2:
            print(f"{self.path}: Line {self.i}: S006 More than two blank lines used before this line")
        self.empty_line_count = 0

    def check_def_spacing(self):
        # Class and function definitions must have only one space between the class/def and name.
        # We use lstrip() to remove any leading whitespace to make our lives easier.
        if match := re.search(r"(class|def)\s{2,}\S+", self.line.lstrip()):
            print(f"{self.path}: Line {self.i}: S007 Too many spaces after '{match.group(1)}'")

    def check_class_def_case(self):
        # Classes must use CamelCase.
        # We use lstrip() to remove any leading whitespace to make our lives easier.
        if match := re.search(r"(class\s)((\S+_\S+)|([a-z_]+)):", self.line.lstrip()):
            print(f"{self.path}: Line {self.i}: S008 Class name '{match.group(2)}' should use CamelCase")

    def check_function_def_case(self):
        # Functions must use snake_case.
        # We use lstrip() to remove any leading whitespace to make our lives easier.
        if match := re.search(r"def\s(\S*[A-Z]\S*)\(", self.line.lstrip()):
            print(f"{self.path}: Line {self.i}: S009 Function name '{match.group(1)}' should use snake_case")

    def check_arg_case(self):
        # Iterates through our AST data for parameters for the given line.
        # Parameters must use snake_case.
        for parameter in self.sca_ast.get_parameters(self.i):
            if re.search(r"\S*[A-Z]\S*", parameter):
                print(f"{self.path}: Line {self.i}: S010 Argument name '{parameter}' should use snake_case")
                break

    def check_variable_case(self):
        # Iterates through our AST data for variables for the given line.
        # Parameters must use snake_case.
        for variable in self.sca_ast.get_variables(self.i):
            if re.search(r"\S*[A-Z]\S*", variable):
                print(f"{self.path}: Line {self.i}: S011 Variable '{variable}' in function should be snake_case")
                break

    def check_mutable_default_arg(self):
        # Call the function to get mutable defaults.
        # If anything is returned, there needs to be an error.
        if self.sca_ast.get_mutable_defaults(self.i):
            print(f"{self.path}: Line {self.i}: S012 Default argument value is mutable")


if __name__ == '__main__':
    if os.path.isfile(sys.argv[1]):
        StaticCodeAnalyzer(sys.argv[1])
    else:
        for file in os.listdir(sys.argv[1]):
            StaticCodeAnalyzer(os.path.join(sys.argv[1], file))