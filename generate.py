import datetime
import json
import os

import streamlit as st

from common import ask_llm, to_json_string, save_as_file, get_image_and_save

DEBUG = True

def generate_case(location: str,
                  time: datetime.time,
                  base_directory_cases: str,
                  llm_model: str,
                  image_model: str) -> None:
    system_prompt = "Du bist Spiele-Designer für eine Murder Mystery Game."

    mmg_prompt = """
Es ist ein Mord geschehen. Der Spieler ist der Detektiv. 
Der Schauplatz der Tat ist {location}. Die Tat geschah um {time} Uhr. Erstelle einen Titel für das Spiel. 
Wer wurde ermordet? Wann geschah der Mord? Wer hat die Tat begangen? 
In welchem Raum hat sich die Tat ereignet?

Deine Antwort besteht nur aus der JSON-Datei mmg.json mit deinem Inhalt für diese Attributen:

title: Der Titel des Spiels.
description: Eine kurze Beschreibung des Spiels.
story: Die Hintergrundgeschichte des Mordfalls.
player:  "position": [0, 0] ,
victim: Der Name des Mordopfers.
time: Der Zeitpunkt des Mordes. Format hh:mm
room: Der Raum, in dem der Mord stattfand.
killer: Der Name des Mörders.
"""

    npcs_prompt = """
Erstelle eine JSON-Datei npcs.json mit 6 Personen. 
Eine davon ist der Täter und 5 sind mögliche Verdächtige, aber unschuldig. 
Für jede Person gibt es diese Attribute

name: Der Name der Person.
description: Eine kurze Beschreibung der Person.
image: Der Dateiname des Bildes der Person.
x: Die X-Koordinate der Person auf der Spielfläche. Zwischen 0 und 8
y: Die Y-Koordinate der Person auf der Spielfläche. Zwischen 0 und 8
icon: Ein Buchstabe, möglichst erster Buchstabe des Nachnamens
backstory: Die Hintergrundgeschichte der Person.
relationships: Die Beziehungen zu den anderen NPCs (neutral, friendly, hostile).
appearance: Eine Beschreibung des Aussehens der Person.
psychological_profile: Ein psychologisches Profil der Person.
possible_motive: Ein möglicher Grund, warum die Person verdächtigt wird.

Die Datei hat das Format "[element1, element2, ...]"
"""

    rooms_prompt = """
Es gibt 9 Räume. Erstelle die JSON-Datei rooms.json mit diesen Attributen

name: Der Name des Raums.
x: Die X-Koordinate des Raums auf der Spielfläche.
y: Die Y-Koordinate des Raums auf der Spielfläche.
width: Die Breite des Raums (immer 3).
height: Die Höhe des Raums (immer 3).
color: Die Farbe, die zur Darstellung des Raums verwendet wird (in Hex-Format).

Die Datei hat das Format "[element1, element2, ...]"

Die Spielfläche ist 9 x 9 Felder groß. Jeder Raum ist 3 x 3 groß.
"""

    timeline_prompt = """
Du sollst eine Tabelle für den zeitlichen Ablauf (von {start_time} bis {end_time})
vor dem Mord erstellen. Jede Spalte entspricht einen Zeitraum von einer halben Stunde. 
Jede Zeile entspricht einer beteiligten Person. 
Trage in jede Zelle der Tabelle ein: Wo war die Person zu diesem Zeitpunkt? 
Was hat sie getan und warum? Mit wem war Sie zusammen? 
Gib dies als JSON-Datei timeline.json aus.  
Attribute:
name: Der Name der Person.
Eine Liste der Aktivitäten der Person. Je Aktivität gibt es diese Attribute
    time: Der Zeitraum der Aktivität.
    location: Der Ort, an dem die Person sich befindet.
    activity: Was die Person tut.
    reason: Warum die Person diese Aktivität ausführt.
    companions: Mit wem die Person zusammen war.
    
Die Datei hat das Format ["person1": [... ], "person2": [...], ...]
"""

    hints_prompt = """
Erstelle eine JSON-Datei hints.json mit 10 Hinweisen. Vier Hinweise stimmen. 
Die restlichen sind falsch. Für jeden Hinweis gibt es diese Attribute

text: Der Text des Hinweises.
x: Die X-Koordinate des Hinweises auf der Spielfläche.
y: Die Y-Koordinate des Hinweises auf der Spielfläche.
misleading: Ob der Hinweis irreführend ist (true) oder nicht (false).

Die Datei hat das Format "[element1, element2, ...]"

Verteile diese auf der Spielefläche von 9 x 9.
"""
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # basis
    messages, mmg = ask_llm(messages, mmg_prompt.format(location=location, time=time), llm_model, DEBUG)
    mmg_json = json.loads(to_json_string(mmg))

    case_path = os.path.join(base_directory_cases, mmg_json["title"])
    os.mkdir(case_path)

    data_path = os.path.join(case_path, "data")
    os.mkdir(data_path)

    save_as_file(mmg, os.path.join(data_path, "mmg.json"))

    # npcs
    messages, npcs = ask_llm(messages, npcs_prompt, llm_model, DEBUG)
    save_as_file(npcs, os.path.join(data_path, "npcs.json"))

    # rooms
    messages, rooms = ask_llm(messages, rooms_prompt, llm_model, DEBUG)
    save_as_file(rooms, os.path.join(data_path, "rooms.json"))

    # timeline
    from datetime import datetime, timedelta

    dummy_date = datetime.combine(datetime.today(), time)
    new_time = dummy_date - timedelta(hours=2)

    messages, timeline = ask_llm(messages, timeline_prompt.format(start_time=new_time.strftime("%H:%M"),
                                                                  end_time=time.strftime("%H:%M")),
                                 llm_model,DEBUG)
    save_as_file(timeline, os.path.join(data_path, "timeline.json"))

    # hints
    messages, hints = ask_llm(messages, hints_prompt, llm_model, DEBUG)
    save_as_file(hints, os.path.join(data_path, "hints.json"))

    # images
    assets_path = os.path.join(case_path, "assets")
    os.mkdir(assets_path)

    generate_images(assets_path, messages, npcs, llm_model, image_model)

    st.rerun()


def generate_images(assets_path, messages, npcs, llm_model, image_model):

    title_prompt = """

    Erstelle eine JSON-Datei title.json, die eine Beschreibung für Dall-E enthält, 
    mit der dieses eine Titelbild für das Spiel generiert.
    Die Datei enthält das Attribut

    description: Beschreibung des Titelbildes für Dall-E
    """

    image_prompt = """
    Erstelle eine JSON-Datei images.json, die für jeden NPC eine Beschreibung für Dall-E enthält, 
    mit der dieses eine Bild von diesen für das Spiel generiert.
    Verwende bei der Beschreibung keine Namen.
    Die Datei enthält je NPC die Attribute

    name: Name des NPC
    decription: Beschreibung des Bildes für Dall-E

    Die Datei hat das Format "[element1, element2, ...]"
    """

    messages, title_json = ask_llm(messages, title_prompt, llm_model, DEBUG)
    title = json.loads(to_json_string(title_json))

    prompt = """
Du bist Grafik-Designer in einer Spielefirma und arbeitest an einem Murder Mystery Spiel mit. 
Entwirf das Titelbild. Beschreibung """ + title["description"]

    get_image_and_save(prompt, assets_path, 'title_image.jpg', image_model, DEBUG)
    messages, image_json = ask_llm(messages, image_prompt, llm_model, DEBUG)


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

        prompt = """
Du bist Grafik-Designer in einer Spielefirma und arbeitest an einem Murder Mystery Spiel mit. Erstelle
das Portrait einer Spielfigur. Beschreibung """ + description

        get_image_and_save(prompt, assets_path, file_name, image_model, DEBUG)
