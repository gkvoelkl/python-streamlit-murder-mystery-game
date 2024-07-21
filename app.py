import random
from typing import List

import streamlit as st
from openai import OpenAI

from common import *
from generate import generate_case
from prompt import FIRST_TALK

st.session_state.ollama_path = 'http://localhost:11434/v1'
st.session_state.image_model = 'dall-e-3'

BASE_DIRECTORY_CASES = 'cases/'

CELL_SIZE = 40
GRID_SIZE = 9

st.set_page_config(layout="wide")


def init(case_name: str) -> None:
    if "mmg" not in st.session_state:
        st.session_state.mmg = read_json(BASE_DIRECTORY_CASES + '/' + case_name + '/data/mmg.json')

    if "npcs" not in st.session_state:
        st.session_state.npcs = read_json(BASE_DIRECTORY_CASES + '/' + case_name + '/data/npcs.json')

    if "rooms" not in st.session_state:
        st.session_state.rooms = read_json(BASE_DIRECTORY_CASES + '/' + case_name + '/data/rooms.json')

    if "hints" not in st.session_state:
        st.session_state.hints = read_json(BASE_DIRECTORY_CASES + '/' + case_name + '/data/hints.json')

    if "timeline" not in st.session_state:
        st.session_state.timeline = read_json(BASE_DIRECTORY_CASES + '/' + case_name + '/data/timeline.json')

    if 'player_position' not in st.session_state:
        st.session_state.player_position = st.session_state.mmg["player"]["position"]

    if 'found_hints' not in st.session_state:
        st.session_state.found_hints = []

    if 'accusation' not in st.session_state:
        st.session_state.accusation = False

    if 'ending_reached' not in st.session_state:
        st.session_state.ending_reached = False


def display_board():
    svg_string = """
<svg width="360" height="360" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="100" x="10" y="10" rx="20" ry="20" fill="blue" />
    <!-- Hintergrund und Spielfeld zeichnen -->
    <rect x="0" y="0" width="360" height="360" fill="gray"/>
 """

    for room in st.session_state.rooms:
        for x in range(room['x'], room['x'] + room['width']):
            for y in range(room['y'], room['y'] + room['height']):
                color = room['color']
                svg_string = (svg_string + '\n' +
                              f'<rect x="{x * CELL_SIZE}" y="{y * CELL_SIZE}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{color}" stroke="black" stroke-width="1"/>'
                              )

    svg_string = svg_string + f"""
    <!-- Player (D) -->
    <text x="{st.session_state.player_position[0] * CELL_SIZE + 0.5 * CELL_SIZE}" y="{st.session_state.player_position[1] * CELL_SIZE + 0.5 * CELL_SIZE}" fill="blue" font-size="24" text-anchor="middle" dominant-baseline="central">D</text>
    """

    for npc in st.session_state.npcs:
        svg_string = (svg_string + '\n' +
                      f'<text x="{npc["x"] * CELL_SIZE + 0.5 * CELL_SIZE}" y="{npc["y"] * CELL_SIZE + 0.5 * CELL_SIZE}" fill="black" font-size="24" text-anchor="middle" dominant-baseline="central">{npc["icon"]}</text>'
                      )

    svg_string = svg_string + """
</svg>
    """
    st.image(svg_string, width=CELL_SIZE * GRID_SIZE)


def move_player(direction):
    if direction == "up" and st.session_state.player_position[1] > 0:
        st.session_state.player_position[1] -= 1
    elif direction == "down" and st.session_state.player_position[1] < GRID_SIZE:
        st.session_state.player_position[1] += 1
    elif direction == "left" and st.session_state.player_position[0] > 0:
        st.session_state.player_position[0] -= 1
    elif direction == "right" and st.session_state.player_position[0] < GRID_SIZE:
        st.session_state.player_position[0] += 1
    st.rerun()


def display_hint():
    for hint in st.session_state.hints:
        if st.session_state.player_position == [hint["x"], hint["y"]]:
            if hint["text"] not in st.session_state.found_hints:
                st.session_state.found_hints.append(hint["text"])
                st.markdown(f"**Hinweis gefunden:** {hint['text']}")


def change_chatbot_style():
    # Set style of chat input so that it shows up at the bottom of the column
    chat_input_style = f"""
    <style>
        .stChatInput {{
          position: fixed;
          bottom: 0rem;
        }}
    </style>
    """
    st.markdown(chat_input_style, unsafe_allow_html=True)


@st.experimental_dialog("Talk to", width="large")
def conversation(npc):
    st.image(BASE_DIRECTORY_CASES + '/' + st.session_state.case_name + '/assets/' + npc["image"], width=200)
    st.markdown(f"**{npc['name']}**: {npc['description']}")

    # -- erstes Gespräch mit Detektiv
    if "messages" not in npc:
        if npc["name"] == st.session_state.mmg['killer']:
            taeter_verdaechtig = "Du bist der Täter. Das darfst du den Spieler(Detektiv) auf keinen Fall verraten."
        else:
            taeter_verdaechtig = "Du bist zwar verdächtig, aber du hast nichts getan."

        timeline = ""
        for j in st.session_state.timeline[npc['name']]:
            timeline += f'Um {j["time"]} bis du im {j["location"]}\n'
            timeline += f'Deine Aktivität: {j["activity"]}\n'
        timeline += "\n"

        content = FIRST_TALK.format(
            name=npc['name'],
            description=npc["description"],
            story=st.session_state.mmg['story'],
            backstory=npc["backstory"],
            appearance=npc["appearance"],
            psychological_profile=npc["psychological_profile"],
            possible_motive=npc["possible_motive"],
            taeter_verdaechtig=taeter_verdaechtig,
            timeline=timeline
        )

        npc["messages"] = [
            {
                'role': 'system',
                'content': content
            }
        ]

    else:  # -- alle weiteren Gespräche mit dem Detektiv
        content = f""" Aktuelle Spielsituation: Du hast bereits mit dem  Spieler(Detektiv) gesprochen. Er verwickelt 
        dich erneut in ein Gespräch."""
        npc['messages'].append(
            {
                'role': 'system',
                'content': content
            }
        )

    # -- Frage des Detektiv
    change_chatbot_style()
    if prompt := st.chat_input("Deine Frage"):
        npc['messages'].append(  # save prompt
            {
                'role': "user",
                'content': prompt
            }
        )

    for message in npc['messages']:  # Display the prior chat messages
        if message['role'] != "system":
            with st.chat_message(message['role']):
                st.write(message['content'])

    # -- Antwort des LLMs
    if npc['messages'][-1]['role'] != "assistant" and npc['messages'][-1]['role'] != "system":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.client.chat.completions.create(
                    model=st.session_state.model,
                    messages=npc['messages']
                )
                p = response.choices[0].message.content
                st.write(p)
                message = {
                    'role': "assistant",
                    'content': p
                }
                npc['messages'].append(message)  # Add response to message history


def interact_npc():
    for npc in st.session_state.npcs:
        if (st.session_state.player_position[0] == npc["x"] and
                st.session_state.player_position[1] == npc["y"]):
            conversation(npc)


def update_npcs():
    for npc in st.session_state.npcs:
        if random.random() < 0.1:  # 10 % Chance pro Tick, dass sich ein NPC bewegt
            direction = random.choice(["up", "down", "left", "right"])
            if direction == "up" and npc["y"] > 0:
                npc["y"] -= 1
            elif direction == "down" and npc["y"] < 9:
                npc["y"] += 1
            elif direction == "left" and npc["x"] > 0:
                npc["x"] -= 1
            elif direction == "right" and npc["x"] < 9:
                npc["x"] += 1


def get_current_room() -> str:
    player_x = st.session_state.player_position[0]
    player_y = st.session_state.player_position[1]

    room_name = 'unbekannt'
    room_image = ''

    for room in st.session_state.rooms:
        if room['x'] <= player_x < room['x'] + room['width']:
            if room['y'] <= player_y < room['y'] + room['height']:
                room_name = room['name']
                room_image = room['image']
                break

    return room_name, room_image


def get_persons() -> List[str]:
    return [i["name"] for i in st.session_state.npcs]


if "case_name" not in st.session_state:
    st.title("Murder Mystery Game 🔎")

if "model" not in st.session_state:
    with st.form("Model"):
        model = st.selectbox(
            "Bitte wählen Sie das gewünschte LLM aus",
            ("gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "llama3", "gemma2")
        )
        submitted = st.form_submit_button("Weiter")
        if submitted:
            st.session_state.model = model

if "model" in st.session_state and "client" not in st.session_state:
    if st.session_state.model.startswith("gpt"):
        try:
            st.session_state.client = OpenAI(
                api_key=st.secrets.openai_key
            )
        except:
            with st.form("API key"):
                st.write(
                    "Für die Kommunikation mit ChatGPT wird ein API Key benötigt. Diesen erhalten Sie auf openai.com")
                st.write("Sie können den Schlüssel in der Datei .streamlit/secrets.toml hinterlegen.")
                api_key = st.text_input("Bitte API key eingeben")
                submitted = st.form_submit_button("Weiter")
                if submitted:
                    st.session_state.client = OpenAI(
                        api_key=api_key
                    )

    else:
        st.session_state.client = OpenAI(
            base_url=st.session_state.ollama_path,
            api_key='ollama'  # required, but unused
        )

if "client" in st.session_state and "case_name" not in st.session_state:
    st.write("Wählen Sie den Fall aus, den Sie als Detektiv lösen wollen.")

    cases = get_subdirectories(BASE_DIRECTORY_CASES)

    selected_case = st.selectbox("Wählen Sie einen Fall aus:", cases)
    button_play = st.button("Spielen")

    if selected_case:
        if button_play:
            st.session_state.case_name = selected_case
            init(st.session_state.case_name)
            st.rerun()

    with st.form("Neuen Fall generieren"):
        location_val = st.text_input("Ort, an dem die Tat geschehen ist")
        time_val = st.time_input("Tat-Zeitpunkt")
        do_proof = st.checkbox("JSON-Dateien prüfen")

        submitted = st.form_submit_button("Generieren")
        if submitted:
            generate_case(location_val, time_val, BASE_DIRECTORY_CASES, st.session_state.model,
                          st.session_state.image_model, do_proof)

if "client" in st.session_state and "case_name" in st.session_state:
    st.title(st.session_state.mmg["title"] + ' 🔎')
    st.write(st.session_state.mmg["description"])
    st.write("Du bist der Detektiv :blue[D], befrage die Verdächtigen.")

    st.sidebar.title(st.session_state.mmg["title"] + " 🔎")
    st.sidebar.image(BASE_DIRECTORY_CASES + "/" + st.session_state.case_name + "/assets/title_image.jpg", width=200)

    if st.sidebar.button("Anklage erheben"):
        st.session_state.accusation = True

    if st.session_state.accusation:
        npcs = get_persons()
        guess = st.selectbox("Wen beschuldigst du?", npcs)
        button_pressed = st.button("Bestätigen")
        if button_pressed and guess:
            if guess.lower() == st.session_state.mmg["killer"].lower():
                st.session_state.ending = '**Du hast die richtige Person gefunden! Gerechtigkeit wurde erreicht.**'
            else:
                st.session_state.ending = "**Du hast die falsche Person verdächtigt. Der Mörder bleibt auf freiem Fuß.**"
            st.session_state.ending_reached = True

    if not st.session_state.ending_reached:
        col4, col5 = st.columns([1, 1], gap="small")
        with col4:
            room_name, room_image = get_current_room()
            st.write(f"Du befindest dich im Raum: {room_name}")
            if len(room_image) > 0:
                st.image(BASE_DIRECTORY_CASES + "/" + st.session_state.case_name + "/assets/" + room_image,
                         width=320)

        with col5:
            display_board()
            col1, col2, col3 = st.columns([1, 1, 1], gap="small")
            with col1:
                if st.button('⬅️'):
                    move_player("left")
            with col2:
                if st.button('⬆️'):
                    move_player("up")
                if st.button('⬇️'):
                    move_player("down")
            with col3:
                if st.button('➡️'):
                    move_player("right")

        interact_npc()
        update_npcs()
        display_hint()

    else:
        st.markdown(st.session_state.ending)
        st.write("Spiel beendet.")
