import datetime
import json
import os

import streamlit as st
from jsonschema.validators import Draft7Validator

import prompt
import proof_data

from common import ask_llm, to_json_string, save_as_file, get_image_and_save, read_json

DEBUG = True


def generate_case(location: str,
                  time: datetime.time,
                  base_directory_cases: str,
                  llm_model: str,
                  image_model: str,
                  do_proof:bool = False) -> None:
    messages = [
        {
            "role": "system",
            "content": prompt.SYSTEM_GENERATE
        }
    ]

    # basis
    messages, mmg = ask_llm(messages, prompt.MMG.format(location=location, time=time), llm_model, DEBUG)
    mmg_json = json.loads(to_json_string(mmg))

    case_path = os.path.join(base_directory_cases, mmg_json["title"])
    os.mkdir(case_path)

    data_path = os.path.join(case_path, "data")
    os.mkdir(data_path)

    save_as_file(mmg, os.path.join(data_path, "mmg.json"))

    # npcs
    messages, npcs = ask_llm(messages, prompt.NPCS, llm_model, DEBUG)
    save_as_file(npcs, os.path.join(data_path, "npcs.json"))

    # rooms
    messages, rooms = ask_llm(messages, prompt.ROOMS, llm_model, DEBUG)
    save_as_file(rooms, os.path.join(data_path, "rooms.json"))

    # timeline
    from datetime import datetime, timedelta

    dummy_date = datetime.combine(datetime.today(), time)
    new_time = dummy_date - timedelta(hours=2)

    messages, timeline = ask_llm(messages, prompt.TIMELINE.format(start_time=new_time.strftime("%H:%M"),
                                                                  end_time=time.strftime("%H:%M")),
                                 llm_model, DEBUG)
    save_as_file(timeline, os.path.join(data_path, "timeline.json"))

    # hints
    messages, hints = ask_llm(messages, prompt.HINTS, llm_model, DEBUG)
    save_as_file(hints, os.path.join(data_path, "hints.json"))

    #proof
    if do_proof:
        proof(data_path)

    # images
    assets_path = os.path.join(case_path, "assets")
    os.mkdir(assets_path)

    generate_images(assets_path, data_path, messages, npcs, llm_model, image_model)

    st.rerun()


def generate_images(assets_path, data_path, messages, npcs, llm_model, image_model):
    # title
    messages, title_json = ask_llm(messages, prompt.TITLE_IMAGE, llm_model, DEBUG)
    title = json.loads(to_json_string(title_json))

    get_image_and_save(prompt.CREATE_TITLE_IMAGE.format(description=title["description"]),
                       assets_path, 'title_image.jpg', image_model, DEBUG)

    # npcs
    messages, image_json = ask_llm(messages, prompt.NPCS_IMAGE, llm_model, DEBUG)
    images = json.loads(to_json_string(image_json))

    for j in json.loads(to_json_string(npcs)):
        name = j["name"]
        file_name = j["image"]
        description = ""

        for k in images:
            if k['name'] == name:
                description = k['description']
                break

        if len(description) == 0:
            description = j["description"] + " " + j["appearance"]

        get_image_and_save(prompt.CREATE_NPCS_IMAGE.format(description=description),
                           assets_path, file_name, image_model, DEBUG)

    # rooms
    with open(os.path.join(data_path, "rooms.json")) as f:
        d = json.load(f)

    for j in d:
        name = j["name"]
        file_name = j["image"]
        description = j["description"]

        get_image_and_save(prompt.CREATE_ROOMS_IMAGE.format(name=name,
                                                            description=description),
                           assets_path,
                           file_name, 'dall-e-3', DEBUG)


def proof(data_path: str):
    files = [
        {
            "name": "mmg.json",
            "proof": proof_data.MMG
        },
        {
            "name": "npcs.json",
            "proof": proof_data.NPCS
        },
        {
            "name": "rooms.json",
            "proof": proof_data.ROOMS
        },
        {
            "name": "timeline.json",
            "proof": proof_data.TIMELINE
        },
        {
            "name": "hints.json",
            "proof": proof_data.HINTS
        }
    ]

    for i in files:
        st.write(f'Datei {i["name"]}')

        # Validator mit dem gegebenen Schema erstellen
        validator = Draft7Validator(i["proof"])

        # JSON-Daten in ein Python-Dictionary umwandeln
        data = read_json(os.path.join(data_path, i["name"]))

        # Validierungsfehler sammeln
        errors = sorted(validator.iter_errors(data),
                        key=lambda e: e.path)

        # Alle Fehler ausgeben
        if errors:
            st.write("Validierungsfehler gefunden:")
            for error in errors:
                st.write(f"Fehler: {error.message}")
                if error.path:
                    st.write(f"Pfad: {'/'.join(map(str, error.path))}")
                print()
        else:
            st.write("JSON-Daten sind valide.")
