import os

from javaHandler.javaExtraction import process_java_file
from pythonHandler.pythonExtraction import process_python_file


def process_directory(directory):
    """
    Processes all files in a directory and its subdirectories.

    Args:
        directory (str): Path to the directory.

    Returns:
        dict: A dictionary containing all function/method names and their combined bodies.
        set: A set containing all variable names.
    """
    all_functions = {}
    all_variables = set()

    for root, _, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_name.endswith('.py'):
                functions, variables = process_python_file(file_path)
                all_functions.update(functions)
                # all_variables.update(variables)
            elif file_name.endswith('.java'):
                methods, variables = process_java_file(file_path)
                all_functions.update(methods)
                # all_variables.update(variables)


def gen_test(path):
    process_directory(path)
