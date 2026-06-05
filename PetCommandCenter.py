# ============================================================
# Scripts by HowYouLikeMeNow
#=============================================================
# Features:
# - Individual pet commands
# - All pet commands
# - Stable commands (Claim List / Stall Pet)
# - In-game pet management
#=============================================================
# Adding Pets:
# 1. Open the Pet Manager.
# 2. Click (add pet).
# 3. Target your pet.
# 4. The pet will be saved automatically.
#=============================================================
# Notes:
# - Right-click the gump to close it and stop the script.
# - Pet data is saved locally and persists between sessions.
# ============================================================

import json
import os

GUMP_ID = 987654
SAVE_FILE = "PetCommandCenter_Pets.json"

BTN_ADD_PET = 9001
BTN_BACK = 9002
BTN_MANAGE = 9003
BTN_CLAIM_LIST = 9004
BTN_STALL = 9005

PETS = []

OUTER_FRAME = 9270
INNER_PAGE = 9200
TEXT_HUE = 1152
DIVIDER_HUE = "#C8A45D"


def load_pets():
    global PETS
    if not os.path.exists(SAVE_FILE):
        PETS = []
        return

    try:
        with open(SAVE_FILE, "r") as f:
            PETS = json.load(f)
    except:
        PETS = []


def save_pets():
    with open(SAVE_FILE, "w") as f:
        json.dump(PETS, f, indent=4)


def say(text):
    Player.ChatSay(0, text)


def add_pet():
    Misc.SendMessage("Target the pet you want to add.", 68)
    serial = Target.PromptTarget("Select the pet to add")

    if serial == 0 or serial is None:
        Misc.SendMessage("No pet targeted.", 33)
        return

    mob = Mobiles.FindBySerial(serial)

    if mob is None:
        Misc.SendMessage("Could not find that mobile.", 33)
        return

    for pet in PETS:
        if pet["serial"] == serial:
            Misc.SendMessage("That pet is already added.", 53)
            return

    PETS.append({
        "name": mob.Name,
        "serial": serial
    })

    save_pets()
    Misc.SendMessage("Added pet: " + mob.Name, 68)


def remove_pet(serial):
    global PETS
    PETS = [p for p in PETS if p["serial"] != serial]
    save_pets()
    Misc.SendMessage("Pet removed.", 68)


def pet_command(pet, command):
    name = pet["name"]

    if command == "follow":
        say(name + " follow me")
    elif command == "kill":
        say(name + " kill")
    elif command == "stop":
        say(name + " stop")
    elif command == "stay":
        say(name + " stay")


def stall_pet():
    say("stall")
    Misc.SendMessage("Target the pet you want to stable.", 68)


def add_text_button(gd, x, y, bid, label):
    Gumps.AddButton(gd, x, y, 4005, 4007, bid, 1, 0)
    Gumps.AddLabel(gd, x + 38, y, TEXT_HUE, label)


def draw_divider(gd, x, y, width):
    Gumps.AddHtml(
        gd,
        x,
        y,
        width,
        14,
        "<BASEFONT COLOR={}>──────────────────────────────────────</BASEFONT>".format(DIVIDER_HUE),
        False,
        False
    )


def draw_main_gump():
    button_map = {}

    gd = Gumps.CreateGump(True, True, False, False)
    Gumps.AddPage(gd, 0)

    pet_count = max(len(PETS), 1)

    width = 575
    height = 215 + pet_count * 42

    Gumps.AddBackground(gd, 100, 100, width, height, OUTER_FRAME)
    Gumps.AddBackground(gd, 112, 112, width - 24, height - 24, INNER_PAGE)
    Gumps.AddAlphaRegion(gd, 118, 118, width - 36, height - 36)

    Gumps.AddLabel(gd, 335, 120, TEXT_HUE, "Pet Command Center")

    y = 148
    button_id = 1

    if len(PETS) == 0:
        draw_divider(gd, 125, y - 15, 540)
        Gumps.AddLabel(gd, 355, y + 8, 33, "No pets added.")
        y += 42
    else:
        for pet in PETS:
            draw_divider(gd, 125, y - 15, 540)

            Gumps.AddLabel(gd, 180, y + 7, TEXT_HUE, pet["name"][:10])

            commands = [
                ("Follow", "follow"),
                ("Kill", "kill"),
                ("Stop", "stop"),
                ("Stay", "stay")
            ]

            positions = [
              (245, y + 4),
              (340, y + 4),
              (430, y + 4),
              (520, y + 4)
            ]

            for i in range(len(commands)):
                label, command = commands[i]
                x, by = positions[i]

                add_text_button(gd, x, by, button_id, label)

                button_map[button_id] = {
                    "type": "pet_command",
                    "pet": pet,
                    "command": command
                }

                button_id += 1

            y += 42

    draw_divider(gd, 125, y - 5, 540)
    Gumps.AddLabel(gd, 355, y + 7, TEXT_HUE, "All Pets")
    y += 34

    all_commands = [
        ("All Follow", "all follow me"),
        ("All Kill", "all kill"),
        ("All Guard", "all guard me"),
        ("All Stop", "all stop"),
        ("All Stay", "all stay")
    ]

    all_x = [150, 250, 350, 455, 555]

    for i in range(len(all_commands)):
        label, command = all_commands[i]
        x = all_x[i]

        add_text_button(gd, x, y, button_id, label)

        button_map[button_id] = {
            "type": "all_command",
            "command": command
        }

        button_id += 1

    y += 38

    draw_divider(gd, 125, y - 5, 540)
    Gumps.AddLabel(gd, 360, y + 7, TEXT_HUE, "Stable")
    y += 34

    add_text_button(gd, 170, y, BTN_CLAIM_LIST, "Claim List")
    add_text_button(gd, 335, y, BTN_STALL, "Stall Pet")
    add_text_button(gd, 500, y, BTN_MANAGE, "Manage Pets")

    Gumps.SendGump(
        GUMP_ID,
        Player.Serial,
        160,
        160,
        gd.gumpDefinition,
        gd.gumpStrings
    )

    return button_map


def draw_manage_gump():
    button_map = {}

    gd = Gumps.CreateGump(True, True, False, False)
    Gumps.AddPage(gd, 0)

    pet_count = max(len(PETS), 1)

    width = 335
    height = 130 + pet_count * 34

    Gumps.AddBackground(gd, 100, 100, width, height, OUTER_FRAME)
    Gumps.AddBackground(gd, 112, 112, width - 24, height - 24, INNER_PAGE)
    Gumps.AddAlphaRegion(gd, 118, 118, width - 36, height - 36)

    Gumps.AddLabel(gd, 235, 120, TEXT_HUE, "Pet Manager")

    y = 150
    button_id = 5000

    if len(PETS) == 0:
        Gumps.AddLabel(gd, 230, y, 33, "No pets saved.")
        y += 36
    else:
        for pet in PETS:
            Gumps.AddLabel(gd, 140, y, TEXT_HUE, pet["name"][:22])

            add_text_button(gd, 310, y, button_id, "Remove")

            button_map[button_id] = {
                "type": "remove_pet",
                "serial": pet["serial"]
            }

            button_id += 1
            y += 34

    y += 12

    add_text_button(gd, 160, y, BTN_ADD_PET, "Add Pet")
    add_text_button(gd, 315, y, BTN_BACK, "Back")

    Gumps.SendGump(
        GUMP_ID,
        Player.Serial,
        160,
        160,
        gd.gumpDefinition,
        gd.gumpStrings
    )

    return button_map


load_pets()

current_page = "main"

while True:
    Gumps.CloseGump(GUMP_ID)

    if current_page == "main":
        button_map = draw_main_gump()
    else:
        button_map = draw_manage_gump()

    Gumps.WaitForGump(GUMP_ID, 60000)
    data = Gumps.GetGumpData(GUMP_ID)

    if data is None:
        Misc.SendMessage("Pet Command Center closed.", 68)
        break

    button = data.buttonid

    if button == 0:
        Misc.SendMessage("Pet Command Center closed.", 68)
        break

    if button == BTN_MANAGE:
        current_page = "manage"

    elif button == BTN_BACK:
        current_page = "main"

    elif button == BTN_ADD_PET:
        add_pet()
        current_page = "manage"

    elif button == BTN_CLAIM_LIST:
        say("claim list")

    elif button == BTN_STALL:
        stall_pet()

    elif button in button_map:
        action = button_map[button]

        if action["type"] == "pet_command":
            pet_command(action["pet"], action["command"])

        elif action["type"] == "all_command":
            say(action["command"])

        elif action["type"] == "remove_pet":
            remove_pet(action["serial"])
            current_page = "manage"

    Misc.Pause(250)