import requests
import os

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def llm_call(function_body, module_path, import_module):
    """
    Makes a call to the OpenAI API with the function body.

    Args:
        function_body (str): The body of the function to be passed to the OpenAI API.
    """

    # Set your OpenAI API key
    api_key = os.getenv('API_KEY')

    # Set the prompt text for the API call
    prompt = f"""
    # Python Test Case Generation

    ## Objective:
    Generate test cases for the provided function to ensure its correctness and reliability.

    ## Code to Test:
    ```python
    {function_body}

    Requirements:
    - Return only test cases including all necessary import statements.
    - The provided code is imported from '{import_module}' so whatever you are importing use only '{import_module}' to import class, functions and variables, don't use any random names.
    - Always use Python classes for organizing test cases.

    Guidelines:
    - Always patch the index_route render_template function from '{import_module}' and use with self.client approch.
    - Set up an application context with app.app_context() to avoid RuntimeError: Working outside of application context will, RuntimeError: Working outside of application context and RuntimeError: Working outside of request context.
    - Instead of making unnecessary to patch the request object or mock the database session use only self.client.
    - Ensure that the attribute access and modification are performed within the same with app_context() block to avoid the DetachedInstanceError
    - Configure Mock objects properly to mimic the behavior of real objects.
    - Mock imported libraries and modules to prevent errors.

    Notes:
    - Your generated test cases should cover various scenarios, including edge cases.
    - Ensure the test cases are well-structured, readable, and adhere to best practices.
    """

    try:
        # Make the API call

        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are an IT software Engineer. You are developing an python application. Given the following code write the unit test cases:"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.1
        )

        response = extract_python_code(completion.choices[0].message.content)
        write_python_code_to_file(module_path, response)

    except requests.exceptions.HTTPError as err:
        print("Error:", err)


def extract_python_code(response_content):
    """
    Extracts Python code block from the response content.

    Args:
        response_content (str): The content of the response from OpenAI.

    Returns:
        str: The extracted Python code block.
    """
    # Split the content by newlines
    lines = response_content.split('\n')

    # Initialize lists to store import statements, class/function definitions, and other code lines
    import_statements = []
    class_function_code = []

    # Flags to indicate whether we are inside a class or function definition
    inside_class = False
    inside_function = False

    # Iterate over each line in the response content
    for line in lines:
        # Check if the line starts with 'import' or 'from'
        if line.startswith(('import', 'from')):
            import_statements.append(line)
        # Check if the line starts with 'class'
        elif line.startswith('class'):
            class_function_code.append(line)
            inside_class = True
        # Check if the line starts with 'def'
        elif line.startswith('def'):
            class_function_code.append(line)
            inside_function = True
        # Add lines inside class/function definitions
        elif inside_class or inside_function:
            class_function_code.append(line)
        # Break if we encounter another 'class' or 'def' line
        elif inside_class or inside_function:
            break

    # Join the import statements, class/function definitions, and other code lines to form the Python code block
    python_code = '\n'.join(import_statements + class_function_code)

    python_code = python_code.strip().replace('```', '')

    return python_code


def write_python_code_to_file(file_path, python_code):
    """
    Write the extracted Python code into a new Python file inside a "test" folder with the same original file name suffix with "_test".

    Args:
        file_path (str): The original file path.
        python_code (str): The extracted Python code to be written into the new file.
    """
    # Extract the directory path and file name from the original file path
    directory_path, file_name = os.path.split(file_path)

    test_directory = os.path.join(os.path.dirname(directory_path), "test")
    if not os.path.exists(test_directory):
        os.makedirs(test_directory)

    # Create a new file path for the test file with the original file name suffixed with "_test"
    test_file_path = os.path.join(test_directory, file_name[:-3] + "_test.py")
    top_code = "import os\nimport sys\n\n# Add the parent directory of the app package to the Python path\nsys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\n\n"

    # Write the extracted Python code into the new Python file
    with open(test_file_path, "w") as test_file:
        test_file.write(top_code)
        test_file.write(python_code)


