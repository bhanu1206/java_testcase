import os
import sys
import javalang

from .llmCall import llm_call


def extract_method_body(node):
    """
    Recursively extracts the method body from a MethodDeclaration node.

    Args:
        node (javalang.tree.MethodDeclaration): MethodDeclaration node.

    Returns:
        str: Method body as a string.
    """
    method_body = ''
    for statement in node.body:
        if isinstance(statement, javalang.tree.BlockStatement):
            method_body += extract_method_body(statement)
        else:
            method_body += statement.__str__() + ';'
    return method_body


def extract_class_body(node):
    """
    Recursively extracts the body of a ClassDeclaration node.

    Args:
        node (javalang.tree.ClassDeclaration): ClassDeclaration node.

    Returns:
        str: Class body as a string.
    """
    class_body = ''
    for declaration in node.body:
        class_body += declaration.__str__() + ';'
    return class_body


def extract_class_variables(node):
    """
    Extracts variables from a ClassDeclaration node.

    Args:
        node (javalang.tree.ClassDeclaration): ClassDeclaration node.

    Returns:
        dict: A dictionary containing variable names as keys and their type as values.
    """
    class_variables = {}
    for field_declaration in node.body:
        if isinstance(field_declaration, javalang.tree.FieldDeclaration):
            for declarator in field_declaration.declarators:
                class_variables[declarator.name] = field_declaration.type.name
    return class_variables


def extract_functions_and_variables(filename):
    """
    Extracts methods, classes, and variables from a Java file using javalang.

    Args:
        filename (str): Path to the Java file.

    Returns:
        dict: A dictionary containing method names as keys and method bodies as values.
        dict: A dictionary containing class names as keys and their bodies as values.
        dict: A dictionary containing class names as keys and a dictionary of their variables as values.
        set: A set containing variable names.
    """
    functions = {}
    classes = {}
    variables = set()

    try:
        with open(filename, 'r') as file:
            file_content = file.read()

        tree = javalang.parse.parse(file_content)

        for path, node in tree:
            if isinstance(node, javalang.tree.MethodDeclaration):
                method_name = node.name
                method_body = extract_method_body(node)
                functions[method_name] = method_body
            elif isinstance(node, javalang.tree.ClassDeclaration):
                class_name = node.name
                class_body = extract_class_body(node)
                class_variables = extract_class_variables(node)
                classes[class_name] = {
                    'body': class_body,
                    'variables': class_variables
                }
            elif isinstance(node, javalang.tree.VariableDeclarator):
                variables.add(node.name)

    except FileNotFoundError:
        print(f"File '{filename}' not found.")
    except javalang.parser.JavaSyntaxError as e:
        print(f"Error parsing Java file '{filename}': {e}")

    return functions, file_content


def merge_all_functions(functions, file_content, module_path):
    file_name = os.path.splitext(os.path.basename(module_path))[0]

    extracted_code = ""

    # # Add variable assignments
    # for var_name, var_value in variables.items():
    #     extracted_code += f"{var_name} = {var_value}\n"

    # for func_name, func_body in functions.items():
    #     extracted_code+=func_body
    #     extracted_code+="\n\n"
    # print(extracted_code)

    llm_call(file_content, module_path, file_name)


def process_java_file(file_path):
    """
    Processes a Java file.

    Args:
        file_path (str): Path to the Java file.

    Returns:
        dict: A dictionary containing all method names and their combined bodies.
        set: A set containing all variable names.
    """

    functions, file_content = extract_functions_and_variables(file_path)
    merged_functions = merge_all_functions(functions, file_content, file_path)
    return functions, file_content