import requests
import os

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def llm_call(function_body, module_path, file_name):
    print("Inside java llm")
    """
    Makes a call to the OpenAI API with the function body.

    Args:
        function_body (str): The body of the function to be passed to the OpenAI API.
    """

    # Set your OpenAI API key
    api_key = os.getenv('API_KEY')

    # Set the prompt text for the API call
    prompt = f"""
    # Java Test Case Generation

    ## Objective:
    Generate test cases for the provided function to ensure its correctness and reliability.

    ## Code to Test:
    ```java
    {function_body}

    Requirements:
    - Ensure that the test class name matches the class under test exactly for both the Java code and the corresponding test case.
    - For the given Java code, the test class should be named '{file_name}'.
    - Return only test cases including all necessary import statements.
    - Always organize test cases using Java classes.

    Guidelines:
    - Always mock dependencies using libraries like Mockito to isolate the code under test.
    - Set up mock objects using @Before or @BeforeEach methods to ensure they are properly configured before each test method.
    - Utilize JUnit assertions like assertEquals, assertTrue, assertFalse, etc., to validate expected behavior.
    - Use parameterized tests where applicable to cover various input scenarios.
    - Ensure the test cases are well-structured, readable, and adhere to best practices.

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
                 "content": "You are an IT software Engineer. You are developing an java application. Given the following code write the unit test cases:"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.1
        )

        response = extract_java_code(completion.choices[0].message.content)
        write_java_code_to_file(module_path, response)

    except requests.exceptions.HTTPError as err:
        print("Error:", err)


def extract_java_code(response_text):
    """
    Extracts Java code from a response text.

    Args:
        response_text (str): Text containing Java code.

    Returns:
        str: Extracted Java code.
    """
    java_code = ""
    in_java_block = False

    # Split the response text into lines and iterate through each line
    for line in response_text.split('\n'):
        # Check if the line starts with a marker indicating the start of a Java code block
        if line.strip().startswith("```java"):
            in_java_block = True
        # Check if the line starts with a marker indicating the end of a Java code block
        elif line.strip().startswith("```"):
            in_java_block = False
        # If inside a Java code block, append the line to the extracted Java code
        elif in_java_block:
            java_code += line + '\n'

    return java_code


def write_java_code_to_file(file_path, java_code):
    """
    Write the extracted Java code into a new Java file inside a "test" folder with the same original file name suffixed with "_test.java".

    Args:
        file_path (str): The original file path.
        java_code (str): The extracted Java code to be written into the new file.
    """
    # Extract the directory path and file name from the original file path
    directory_path, file_name = os.path.split(file_path)

    test_directory = os.path.join(os.path.dirname(directory_path), "test")
    if not os.path.exists(test_directory):
        os.makedirs(test_directory)

    # Create a new file path for the test file with the original file name suffixed with "Test.java"
    test_file_path = os.path.join(test_directory, file_name[:-5] + "Test.java")
    # test_file_path = os.path.join(test_directory, file_name)

    # Write the extracted Java code into the new Java file
    with open(test_file_path, "w") as test_file:
        test_file.write(java_code)