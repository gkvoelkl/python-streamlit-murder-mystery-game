FIRST_TALK = """
Du bist {name}, ein NPC in einem Murder Mystery Game. Der Spieler ist der Detektiv
Beschreibung des NPC: {description}
Geschichte : {story}
Aktuelle Spielsituation: Der Spieler(Detektiv) trifft dich das erste Mal und verwickelt dich in ein Gespräch.
Mehr zu dir: {backstory} {appearance}
Dein aktueller Zustand: {psychological_profile} 
Dein mögliches Motiv: {possible_motive}
{taeter_verdaechtig}

{timeline}
"""

SYSTEM_GENERATE = "Du bist Spiele-Designer für ein Murder Mystery Game."

MMG = """
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

Bitte stelle sicher, dass das JSON gültig und korrekt formatiert ist.

Erzeuge eine JSON-Struktur wie diese:
{
  "title": "dummy",
  "description": "dummy",
  "story": "dummy,
  "player": {
    "position": [0, 0]
  },
  "killer": "Dummy"
}
"""

NPCS = """
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

ROOMS = """
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

TIMELINE = """    
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

HINTS = """    
Erstelle eine JSON-Datei hints.json mit 10 Hinweisen. Vier Hinweise stimmen. 
Die restlichen sind falsch. Für jeden Hinweis gibt es diese Attribute

text: Der Text des Hinweises.
x: Die X-Koordinate des Hinweises auf der Spielfläche.
y: Die Y-Koordinate des Hinweises auf der Spielfläche.
misleading: Ob der Hinweis irreführend ist (true) oder nicht (false).

Die Datei hat das Format "[element1, element2, ...]"

Verteile diese auf der Spielefläche von 9 x 9.
"""

TITLE_IMAGE = """
Erstelle eine JSON-Datei title.json, die eine Beschreibung für Dall-E enthält, 
mit der dieses eine Titelbild für das Spiel generiert.
Die Datei enthält das Attribut

description: Beschreibung des Titelbildes für Dall-E
"""

CREATE_TITLE_IMAGE = """
Dist Grafik-Designer in einer Spielefirma und arbeitest an einem Murder Mystery Spiel. 
Entwirf das Titelbild. Beschreibung {description}
"""

NPCS_IMAGE = """
Erstelle eine JSON-Datei images.json, die für jeden NPC eine Beschreibung für Dall-E enthält, 
mit der dieses eine Bild von diesen für das Spiel generiert.
Verwende bei der Beschreibung keine Namen.
Die Datei enthält je NPC die Attribute

name: Name des NPC
decription: Beschreibung des Bildes für Dall-E

Die Datei hat das Format "[element1, element2, ...]"
"""

CREATE_NPCS_IMAGE = """
Du bist Grafik-Designer in einer Spielefirma und arbeitest an einem Murder Mystery Spiel. Erstelle
das Portrait einer Spielfigur. Beschreibung {description}
"""

CREATE_ROOMS_IMAGE = """
Du bist Grafik-Designer in einer Spielefirma und arbeitest an einem Murder Mystery Spiel. Erstelle
das Bild eines bestimmen Raumes in diesem Spiel in möglichst isometrischer Perspektive. 

Name: {name} 

Beschreibung: {description}
"""