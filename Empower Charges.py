#========================================
#====== Scripts By HowYouLikeMeNow ======
#========================================
#======== EMPOWER CHARGE COUNTER ========
#========================================
#===== Displays the lowest remaining ====
#= Empower charges on equipped clothing =
#========================================
#======= Updates every 2 seconds ========
#========= Right click to close =========
#========================================

import re
import time


GUMP_ID = 0x7A55F116

GUMP_X = 75
GUMP_Y = 75
GUMP_WIDTH = 70
GUMP_HEIGHT = 70
BACKGROUND_ID = 9270

EMPOWER_X = 10
EMPOWER_Y = 8

CHARGES_X = 12
CHARGES_Y = 22

COUNTER_X = 20
COUNTER_Y = 40

TITLE_HUE = 1152
BLUE_HUE = 89
GREEN_HUE = 68
YELLOW_HUE = 53
RED_HUE = 33

GREEN_THRESHOLD = 750
YELLOW_THRESHOLD = 300
SCAN_SECONDS = 2.0


EQUIPMENT_LAYERS = (
    'RightHand', 'LeftHand', 'Shoes', 'Pants', 'Shirt',
    'Head', 'Gloves', 'Ring', 'Neck', 'Waist',
    'InnerTorso', 'MiddleTorso', 'OuterTorso',
    'Arms', 'Cloak', 'Bracelet', 'Earrings',
    'OuterLegs', 'InnerLegs', 'Talisman'
)


def get_empower_charges(item):
    try:
        Items.WaitForProps(item.Serial, 250)
        props = Items.GetPropStringList(item.Serial) or []

        lines = [
            re.sub(r'<[^>]*>', ' ', str(p)).strip().lower()
            for p in props
        ]

        if not any('empower' in p for p in lines):
            return None

        patterns = (
            r'charges\s*remaining\s*[:=]?\s*(\d+)',
            r'empower(?:ed|ment)?\s*(?:charges?)?\s*[:=]?\s*(\d+)'
        )

        for pattern in patterns:
            for line in lines:
                match = re.search(pattern, line)
                if match:
                    return int(match.group(1))

    except:
        pass

    return None


def lowest_empower_charges():
    charges = []
    seen = set()

    for layer in EQUIPMENT_LAYERS:
        try:
            item = Player.GetItemOnLayer(layer)
            if not item or item.Serial in seen:
                continue

            seen.add(item.Serial)
            value = get_empower_charges(item)

            if value is not None:
                charges.append(value)
        except:
            pass

    return min(charges) if charges else None


def draw_counter(charges):
    value = 0 if charges is None else charges

    if charges is None:
        hue = BLUE_HUE
    elif value >= GREEN_THRESHOLD:
        hue = GREEN_HUE
    elif value >= YELLOW_THRESHOLD:
        hue = YELLOW_HUE
    else:
        hue = RED_HUE

    g = Gumps.CreateGump(True)
    g.gumpId = GUMP_ID

    Gumps.AddPage(g, 0)
    Gumps.AddBackground(
        g, 0, 0, GUMP_WIDTH, GUMP_HEIGHT, BACKGROUND_ID
    )
    Gumps.AddAlphaRegion(
        g, 5, 5, GUMP_WIDTH - 10, GUMP_HEIGHT - 10
    )

    Gumps.AddLabel(g, EMPOWER_X, EMPOWER_Y, TITLE_HUE, 'Empower')
    Gumps.AddLabel(g, CHARGES_X, CHARGES_Y, TITLE_HUE, 'Charges')
    Gumps.AddLabel(g, COUNTER_X, COUNTER_Y, hue, str(value))

    Gumps.SendGump(
        GUMP_ID, Player.Serial, GUMP_X, GUMP_Y,
        g.gumpDefinition, g.gumpStrings
    )


last_charges = None
last_scan = 0
gump_created = False

try:
    while Player.Connected:

        if gump_created:
            try:
                data = Gumps.GetGumpData(GUMP_ID)
                if data is not None and int(data.buttonid) == 0:
                    break
            except:
                pass

        if time.time() - last_scan >= SCAN_SECONDS:
            last_scan = time.time()
            charges = lowest_empower_charges()

            if not gump_created or charges != last_charges:
                try:
                    Gumps.ResetGump(GUMP_ID)
                except:
                    pass

                draw_counter(charges)
                last_charges = charges
                gump_created = True

        Misc.Pause(100)

finally:
    try:
        Gumps.CloseGump(GUMP_ID)
    except:
        pass