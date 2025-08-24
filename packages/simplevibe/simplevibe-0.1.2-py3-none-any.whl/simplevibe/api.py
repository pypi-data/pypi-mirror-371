import os
import json
import requests
from typing import Union, List
from pprint import pprint


def llama3(
    messages: Union[str, List[dict]],
    image_paths: Union[str, List[str], None] = None,
    upload_files: bool = True,
    url: str = "http://127.0.0.1:42070",
    temperature: float = 0.7,
    max_new_tokens: int = 2000,
    top_k: int = 50,
    top_p: float = 0.9,
    add_generation_prompt: bool = True
):
    """
    Function to interact with the Llama3 backend API.
    Parameters:
    - messages: List of message dictionaries or a JSON string.
    e.g. [{"role": "user", "content": "hello"}] or 
    - image_paths: List of image file paths or a single path as a string.
    - upload_files: If False, the server will look for the files at the given paths.
    - url: The API endpoint URL.
    - temperature: Sampling temperature for the model.
    - max_new_tokens: Maximum number of new tokens to generate.
    - top_k: Top-k sampling parameter.
    - top_p: Top-p (nucleus) sampling parameter.
    Returns:
    - JSON response from the API.
    e.g. {
        'eta': 0.3324270248413086,
        'input_token_length': 36,
        'output_token_length': 18,
        'result': '<|begin_of_text|>'
        }
    """

    data = {
        "messages": json.dumps(messages),
        "temperature": temperature,
        "max_new_tokens": max_new_tokens,
        "top_k": top_k,
        "top_p": top_p,
        "add_generation_prompt": str(add_generation_prompt).lower()
    }

    files = None

    if image_paths:
        if isinstance(image_paths, str):
            image_paths = [image_paths]

        if upload_files:
            # Send actual image files
            files = [
                ("images", (f"image_{i}.png", open(path, "rb"), "image/png"))
                for i, path in enumerate(image_paths)
            ]
        else:
            data["file_path"] = json.dumps(image_paths)

    response = requests.post(url, data=data, files=files)

    if files:
        for _, file_tuple in files:
            file_tuple[1].close()

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return {"error": f"Request failed with status {response.status_code}"}


if __name__ == "__main__":
    # Example usage of llama3_api
    messages = [{"role": "user", "content": "Hello, how are you?"}]
    image_paths = None  # Replace with paths to images if needed
    try:
        response = llama3(
            messages=messages,
            image_paths=image_paths,
            temperature=0.8,
            max_new_tokens=150,
            top_k=40,
            top_p=0.85
        )
        pprint(response)
    except Exception as e:
        print(f"An error occurred: {e}")