MMG = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "title": {
            "type": "string"
        },
        "description": {
            "type": "string"
        },
        "story": {
            "type": "string"
        },
        "player": {
            "type": "object",
            "properties": {
                "position": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "minItems": 2,
                    "maxItems": 2
                }
            },
            "required": ["position"]
        },
        "victim": {
            "type": "string"
        },
        "time": {
            "type": "string",
            "pattern": "^(?:[01]\\d|2[0-3]):[0-5]\\d$"
        },
        "room": {
            "type": "string"
        },
        "killer": {
            "type": "string"
        }
    },
    "required": ["title", "description", "story", "player", "victim", "time", "room", "killer"]
}

NPCS = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string"
      },
      "description": {
        "type": "string"
      },
      "image": {
        "type": "string"
      },
      "x": {
        "type": "integer"
      },
      "y": {
        "type": "integer"
      },
      "icon": {
        "type": "string"
      },
      "backstory": {
        "type": "string"
      },
      "relationships": {
        "type": "object",
        "additionalProperties": {
          "type": "string",
          "enum": ["hostile", "neutral", "friendly"]
        }
      },
      "appearance": {
        "type": "string"
      },
      "psychological_profile": {
        "type": "string"
      },
      "possible_motive": {
        "type": "string"
      }
    },
    "required": [
      "name",
      "description",
      "image",
      "x",
      "y",
      "icon",
      "backstory",
      "relationships",
      "appearance",
      "psychological_profile",
      "possible_motive"
    ]
  }
}

ROOMS = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string"
      },
      "x": {
        "type": "integer"
      },
      "y": {
        "type": "integer"
      },
      "width": {
        "type": "integer"
      },
      "height": {
        "type": "integer"
      },
      "color": {
        "type": "string"
      }
    },
    "required": ["name", "x", "y", "width", "height", "color"]
  }
}

TIMELINE = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "additionalProperties": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "time": {
          "type": "string",
          "pattern": "^\\d{2}:\\d{2}-\\d{2}:\\d{2}$"
        },
        "location": {
          "type": "string"
        },
        "activity": {
          "type": "string"
        },
        "reason": {
          "type": "string"
        },
        "companions": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      },
      "required": ["time", "location", "activity", "reason", "companions"],
      "additionalProperties": False
    }
  }
}

HINTS = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "description": "Der Text der Aussage."
      },
      "x": {
        "type": "integer",
        "description": "Die x-Koordinate der Aussage."
      },
      "y": {
        "type": "integer",
        "description": "Die y-Koordinate der Aussage."
      },
      "misleading": {
        "type": "boolean",
        "description": "Gibt an, ob die Aussage irreführend ist."
      }
    },
    "required": ["text", "x", "y", "misleading"]
  }
}
