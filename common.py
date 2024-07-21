import streamlit as st
import os
import requests
import json

from typing import Tuple


def get_subdirectories(directory):
    """Return a list of subdirectories in the given directory."""
    try:
        subdirectories = [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]
        return subdirectories
    except Exception as e:
        st.error(f"Error reading directory: {e}")
        return []


def save_as_file(content: str, filename: str) -> None:
    with open(filename, 'w') as f:
        f.write(to_json_string(content))


def read_json(file: str) -> str:
    with open(file) as f:
        return json.load(f)


def to_json_string(value: str) -> str:
    return value.replace('```json', '').replace('```', '').strip()


def download_image(url, file_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path
    except requests.exceptions.RequestException as e:
        st.error(f"Fehler beim Herunterladen des Bildes: {e}")
        return None


def get_image_and_save(prompt: str, assets_path: str,
                       file_name: str, llm_model: str,
                       debug: bool = False) -> None:
    with st.spinner("Thinking..."):
        picture = st.session_state.client.images.generate(
            model=llm_model,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
    image_url = picture.data[0].url
    if debug:
        st.write(prompt)
        st.image(image_url, width=360)
    download_image(image_url, os.path.join(assets_path, file_name))


def test_llm(llm_model: str) -> None:
    print(f"client {st.session_state.client.base_url} {st.session_state.client.api_key}")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The LA Dodgers won in 2020."},
    ]

    ask_llm(messages, "Where was it played", llm_model, debug=True)


def ask_llm(messages, prompt: str, llm_model: str, debug=True) -> Tuple[any, str]:
    messages.append({
        'role': "user",
        'content': prompt
    })
    with st.spinner("Thinking..."):
        if debug:
            print(f"prompt {llm_model} {prompt}")
        response = st.session_state.client.chat.completions.create(
            model=llm_model,
            messages=messages
        )
        p = response.choices[0].message.content
        if debug:
            st.write(p)
        messages.append({
            'role': "assistant",
            'content': p
        })

    return messages, p
