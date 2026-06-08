# =============================================
# Scripts by HowYouLikeMeNow
# =============================================
# Heals lowest/closest pet
# Smart enough to not heal pets
# that are not close to you.
# Lets you add/remove pets on a list.
#==============================================
# Gump open = setup/manage pets
# Gump closed = healing starts
# =============================================
# Recommend stoping any bandage timer scripts.
#==============================================

from System.IO import File, Path

BANDAGE_ID = 0x0E21
HEAL_RANGE = 1
BANDAGE_DELAY = 5000
IDLE_DELAY = 250

GUMP_ID = 918274
CONFIG_FILE = Path.Combine(Misc.ConfigDirectory(), "uof_pet_healer_pets.txt")

pets = []
healing_active = False


def load_pets():
    result = []

    if not File.Exists(CONFIG_FILE):
        return result

    for line in File.ReadAllLines(CONFIG_FILE):
        parts = line.split("|")
        try:
            serial = int(parts[0])
            name = parts[1] if len(parts) > 1 else str(serial)
            result.append({"serial": serial, "name": name})
        except:
            pass

    return result


def save_pets():
    lines = []
    for pet in pets:
        lines.append(str(pet["serial"]) + "|" + pet["name"])

    File.WriteAllLines(CONFIG_FILE, lines)


def pet_saved(serial):
    for pet in pets:
        if pet["serial"] == serial:
            return True
    return False


def add_pet():
    serial = Target.PromptTarget("Target pet to add.")

    if serial <= 0:
        return

    mob = Mobiles.FindBySerial(serial)

    if mob is None:
        return

    if pet_saved(serial):
        return

    name = mob.Name if mob.Name else str(serial)

    pets.append({"serial": serial, "name": name})
    save_pets()


def remove_pet(index):
    if index >= 0 and index < len(pets):
        pets.pop(index)
        save_pets()


def get_pet_display_name(pet):
    mob = Mobiles.FindBySerial(pet["serial"])

    if mob is not None and mob.Name is not None and mob.Name != "":
        pet["name"] = mob.Name
        save_pets()
        return mob.Name

    return pet["name"]


def draw_main_gump():
    gd = Gumps.CreateGump(True, True, True, False)
    Gumps.AddPage(gd, 0)

    
    Gumps.AddImage(gd, 0, 0, 0x2B2F)# Background
    Gumps.AddImage(gd, 250, 135, 0x408)# Dog
    Gumps.AddImage(gd, 68, 20, 0x772C)# The Star
    Gumps.AddLabel(gd, 270, 20, 1152, "The")
    Gumps.AddLabel(gd, 240, 36, 1152, "- Pet Clinic -")
   
    Gumps.AddButton(gd, 235, 70, 4005, 4007, 1, 1, 0)
    Gumps.AddLabel(gd, 275, 70, 0, "-Add Pet-")

    Gumps.AddButton(gd, 235, 105, 4005, 4007, 2, 1, 0)
    Gumps.AddLabel(gd, 275, 105, 0, "-Pet List-")

    Gumps.SendGump(GUMP_ID, Player.Serial, 200, 200, gd.gumpDefinition, gd.gumpStrings)


def draw_pet_list_gump():
    height = 120 + (len(pets) * 28)

    if height < 150:
        height = 150

    gd = Gumps.CreateGump(True, True, True, False)
    Gumps.AddPage(gd, 0)

    Gumps.AddImage(gd, 0, 0, 0x4E2)
    Gumps.AddLabel(gd, 112, 15, 1152, "--Saved Pets--")

    y = 55

    if len(pets) == 0:
        Gumps.AddLabel(gd, 112, y, 1150, "No pets saved.")
        y += 28
    else:
        for i, pet in enumerate(pets):
            display_name = get_pet_display_name(pet)

            Gumps.AddButton(gd, 45, y, 0x9A1, 0x9A0, 100 + i, 1, 0)
            Gumps.AddLabel(gd, 125, y, 0, "" + display_name)
            y += 28

    Gumps.AddButton(gd, 35, y + 10, 0xFAE, 0xFB0, 3, 1, 0)
    Gumps.AddLabel(gd, 75, y + 10, 0, "Back")

    Gumps.SendGump(GUMP_ID, Player.Serial, 200, 200, gd.gumpDefinition, gd.gumpStrings)


def handle_button(button):
    global healing_active

    if button == 0:
        healing_active = True
        return

    Gumps.CloseGump(GUMP_ID)

    if button == 1:
        add_pet()
        Misc.Pause(300)
        draw_main_gump()

    elif button == 2:
        Misc.Pause(300)
        draw_pet_list_gump()

    elif button == 3:
        Misc.Pause(300)
        draw_main_gump()

    elif button >= 100:
        remove_pet(button - 100)
        Misc.Pause(300)
        draw_pet_list_gump()


def distance_to_player(mob):
    dx = abs(Player.Position.X - mob.Position.X)
    dy = abs(Player.Position.Y - mob.Position.Y)
    return max(dx, dy)


def is_current_mount(mob):
    try:
        return Player.Mount is not None and Player.Mount.Serial == mob.Serial
    except:
        return False


def valid_pet(mob):
    if mob is None:
        return False

    if not mob.Visible:
        return False

    if mob.IsGhost:
        return False

    if mob.Hits <= 0:
        return False

    if mob.HitsMax <= 0:
        return False

    if mob.Hits >= mob.HitsMax:
        return False

    if is_current_mount(mob):
        return False

    if distance_to_player(mob) > HEAL_RANGE:
        return False

    return True


def best_pet():
    candidates = []

    for pet in pets:
        mob = Mobiles.FindBySerial(pet["serial"])

        if not valid_pet(mob):
            continue

        hp_percent = float(mob.Hits) / float(mob.HitsMax)
        dist = distance_to_player(mob)

        candidates.append((hp_percent, dist, mob))

    if len(candidates) == 0:
        return None

    candidates.sort(key=lambda x: (x[0], x[1]))
    return candidates[0][2]


def find_bandage():
    return Items.FindByID(BANDAGE_ID, -1, Player.Backpack.Serial, 1, False)


def heal_pet(pet):
    bandage = find_bandage()

    if bandage is None:
        return False

    Items.UseItem(bandage)

    if Target.WaitForTarget(1500, False):
        Target.TargetExecute(pet.Serial)
        return True

    return False


pets = load_pets()
draw_main_gump()

while True:

    if not healing_active:
        Gumps.WaitForGump(GUMP_ID, 1000)

        gd = Gumps.GetGumpData(GUMP_ID)
        if gd is not None and gd.hasResponse:
            handle_button(gd.buttonid)

        Misc.Pause(100)
        continue

    pet = best_pet()

    if pet is not None and heal_pet(pet):
        Misc.Pause(BANDAGE_DELAY)
    else:
        Misc.Pause(IDLE_DELAY)