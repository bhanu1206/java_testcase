import os
import sys
import ast
from .llmCall import llm_call


def extract_functions_and_variables(filename):
    """
    Extracts functions and variables from a Python file.

    Args:
        filename (str): Path to the Python file.

    Returns:
        dict: A dictionary containing function names as keys and function bodies as values.
        set: A set containing variable names.
    """
    functions_and_classes = {}
    global_variables = {}

    with open(filename, 'r') as file:
        file_content = file.read()
        tree = ast.parse(file_content, filename=filename)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_body = ast.get_source_segment(file_content, node)
                functions_and_classes[node.name] = function_body

            elif isinstance(node, ast.ClassDef):
                class_body = ast.get_source_segment(file_content, node)
                functions_and_classes[node.name] = class_body

            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variable_name = target.id
                        global_variables[variable_name] = ast.get_source_segment(file_content, node)

    return functions_and_classes, file_content


# def combine_functions_with_calls(functions, module_path):
#     """
#     Combines functions if one function calls another.

#     Args:
#         functions (dict): A dictionary containing function names and their bodies.

#     Returns:
#         dict: A dictionary containing all function names and their combined bodies.
#     """
#     combined_functions = {}
#     for func_name, func_body in functions.items():
#         for called_func in functions.keys():
#             if called_func in func_body and called_func != func_name:
#                 func_body = func_body + "\n" + functions[called_func]

#         combined_functions[func_name] = func_body
#         # calling llm with function body
#         #llm_call(func_body, module_path)

#     return combined_functions

def merge_all_functions(functions, file_content, module_path):
    file_name = os.path.splitext(os.path.basename(module_path))[0]

    module_dir = os.path.dirname(module_path)

    module_name = os.path.basename(module_dir)

    import_module = f"{module_name}.{file_name}"

    extracted_code = ""

    # # Add variable assignments
    # for var_name, var_value in variables.items():
    #     extracted_code += f"{var_name} = {var_value}\n"

    # for func_name, func_body in functions.items():
    #     extracted_code+=func_body
    #     extracted_code+="\n\n"
    # print(extracted_code)

    llm_call(file_content, module_path, import_module)


def process_python_file(file_path):
    """
    Processes a Python file.

    Args:
        file_path (str): Path to the Python file.

    Returns:
        dict: A dictionary containing all function names and their combined bodies.
        set: A set containing all variable names.
    """
    functions, file_content = extract_functions_and_variables(file_path)
    merged_functions = merge_all_functions(functions, file_content, file_path)
    return functions, file_content