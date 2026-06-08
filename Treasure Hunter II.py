# ============================================================
# Scripts by HowYouLikeMeNow
# With help from Matson
#=============================================================
#        =Treasure Chest Script=
# 1. Identify all armor/weapons in the chest.
# 2. Loot Gems, Reagents, and Scrolls from the chest.
# 3. Loot Weapons and Armor from the chest.
# 4. Loot Gold from the chest.
# F.Y.I. RDA Frags will be looted while looting Gems.
# You will still have to loot Relics by hand.
#=============================================================
import re

GUMP_ID = 863776
GUMP_X = 400
GUMP_Y = 400

GOLD_IDS = [0x0EED, 0x0EEC]

GEMS = [0x0F25, 0x0F19, 0x0F13, 0x0F16, 0x0F21, 0x0F26, 0x0F15, 0x0F2D, 0x0F10]
REAGENTS = [0x0F86, 0x0F8C, 0x0F88, 0x0F7B, 0x0F85, 0x0F8D, 0x0F7A, 0x0F84]

SCROLLS = [
    0x1F2D, 0x1F2E, 0x1F2F, 0x1F30, 0x1F31, 0x1F32, 0x1F33, 0x1F34,
    0x1F35, 0x1F36, 0x1F37, 0x1F38, 0x1F39, 0x1F3A, 0x1F3B, 0x1F3C,
    0x1F3D, 0x1F3E, 0x1F3F, 0x1F40, 0x1F41, 0x1F42, 0x1F43, 0x1F44,
    0x1F45, 0x1F46, 0x1F47, 0x1F48, 0x1F49, 0x1F4A, 0x1F4B, 0x1F4C,
    0x1F4D, 0x1F4E, 0x1F4F, 0x1F50, 0x1F51, 0x1F52, 0x1F53, 0x1F54,
    0x1F55, 0x1F56, 0x1F57, 0x1F58, 0x1F59, 0x1F5A, 0x1F5B, 0x1F5C,
    0x1F5D, 0x1F5E, 0x1F5F, 0x1F60, 0x1F61, 0x1F62, 0x1F63, 0x1F64,
    0x1F65, 0x1F66, 0x1F67, 0x1F68, 0x1F69, 0x1F6A, 0x1F6B, 0x1F6C
]

LOOT_IDS = GEMS + REAGENTS + SCROLLS

GUMP_BACKGROUND = 0x58E
DECORATION_1 = 0x151
DECORATION_2 = 0x259
DECORATION_3 = 0x264C

BTN_IDENTIFY = -97
BTN_LOOT = -98
BTN_GOLD = -99
BTN_GEAR = -96


def updateGump():
    gd = Gumps.CreateGump(True, True, False, False)
    Gumps.AddPage(gd, 1)

    Gumps.AddImage(gd, 0, 0, GUMP_BACKGROUND)
    Gumps.AddImage(gd, 40, 100, DECORATION_1)
    Gumps.AddImage(gd, 365, 150, DECORATION_2)
    Gumps.AddImage(gd, 163, 58, DECORATION_3)
    
   
    Gumps.AddLabel(gd, 162, 114, 1322, "Welcome Treasure Hunter")
    Gumps.AddBackground(gd, 127, 132, 220, 2, 5054)

    Gumps.AddButton(gd, 135, 145, 0x845, 0x846, BTN_IDENTIFY, 1, 0)
    Gumps.AddHtml(gd, 165, 146, 180, 20, '<BASEFONT COLOR="#FFD700">Identify Items</BASEFONT>', False, False)

    Gumps.AddButton(gd, 135, 165, 0x845, 0x846, BTN_LOOT, 1, 0)
    Gumps.AddHtml(gd, 165, 166, 220, 20, '<BASEFONT COLOR="#FFD700">Loot Gems/Regs/Scrolls</BASEFONT>', False, False)

    Gumps.AddButton(gd, 135, 185, 0x845, 0x846, BTN_GEAR, 1, 0)
    Gumps.AddHtml(gd, 165, 186, 220, 20, '<BASEFONT COLOR="#FFD700">Loot Weapons/Armor</BASEFONT>', False, False)

    Gumps.AddButton(gd, 135, 205, 0x845, 0x846, BTN_GOLD, 1, 0)
    Gumps.AddHtml(gd, 165, 206, 180, 20, '<BASEFONT COLOR="#FFD700">Pull Gold</BASEFONT>', False, False)

    Gumps.SendGump(GUMP_ID, Player.Serial, GUMP_X, GUMP_Y, gd.gumpDefinition, gd.gumpStrings)


def getChest(msg):
    Player.HeadMessage(1151, msg)
    serial = Target.PromptTarget(msg, 0)
    chest = Items.FindBySerial(serial)

    if chest == None:
        Player.HeadMessage(33, "Not found.")
        return None

    if chest.IsContainer == False:
        chest = Items.FindBySerial(chest.Container)

    if chest == None:
        Player.HeadMessage(33, "Invalid container.")
        return None

    Items.UseItem(chest)
    Misc.Pause(1000)
    Items.WaitForContents(chest, 2000)
    return chest


def getBag(msg):
    Player.HeadMessage(1151, msg)
    serial = Target.PromptTarget(msg, 0)
    bag = Items.FindBySerial(serial)

    if bag == None:
        Player.HeadMessage(33, "Bag not found.")
        return None

    Items.UseItem(bag)
    Misc.Pause(650)
    Items.WaitForContents(bag, 1000)
    return bag


def findIDWand():
    if Player.CheckLayer("LeftHand"):
        Player.UnEquipItemByLayer("LeftHand", 650)

    if Player.CheckLayer("RightHand"):
        Player.UnEquipItemByLayer("RightHand", 650)

    Misc.Pause(650)

    for item in Player.Backpack.Contains:
        Items.WaitForProps(item, 1000)
        if "identification" in str(item.Properties).lower():
            Player.EquipItem(item)
            Misc.Pause(650)
            return item

    Player.HeadMessage(33, "No identification wand found.")
    return None


def identifyItems():
    chest = getChest("Target treasure chest")
    if chest == None:
        return

    wand = findIDWand()
    if wand == None:
        return

    count = 0

    for item in chest.Contains:
        Items.WaitForProps(item, 1000)
        props = str(item.Properties).lower()

        if "unidentified" in props:
            Items.UseItem(wand)
            Misc.Pause(650)
            Target.TargetExecute(item)
            Misc.Pause(750)
            count += 1

    Player.HeadMessage(1151, "Identified: " + str(count))


def lootGemsRegsScrolls():
    chest = getChest("Target treasure chest")
    if chest == None:
        return

    bag = getBag("Target destination bag")
    if bag == None:
        return

    moved = 0

    for loot_id in LOOT_IDS:
        item = Items.FindByID(loot_id, -1, chest.Serial)
        while item:
            Items.Move(item.Serial, bag.Serial, -1)
            Misc.Pause(650)
            moved += 1
            item = Items.FindByID(loot_id, -1, chest.Serial)

    Player.HeadMessage(1151, "Looted: " + str(moved))

def pullGold():
    chest = getChest("Target treasure chest")
    if chest == None:
        return

    moved = 0

    for gold_id in GOLD_IDS:
        gold = Items.FindByID(gold_id, -1, chest.Serial)
        while gold != None:
            Items.Move(gold, Player.Backpack.Serial, -1)
            Misc.Pause(650)
            moved += 1
            gold = Items.FindByID(gold_id, -1, chest.Serial)

    Player.HeadMessage(1151, "Gold stacks moved: " + str(moved))


def lootWeaponsArmor():
    chest = getChest("Target treasure chest")
    if chest == None:
        return

    bag = getBag("Target destination bag")
    if bag == None:
        return

    words = [
        "sword", "axe", "mace", "bow", "crossbow", "dagger", "katana",
        "spear", "halberd", "kryss", "war fork", "hammer", "staff",
        "club", "bardiche", "scimitar", "cutlass", "helm", "gorget",
        "tunic", "leggings", "gloves", "sleeves", "shield", "armor",
        "mail", "plate", "leather", "ringmail", "chainmail", "buckler"
    ]

    moved = 0

    for item in chest.Contains:
        Items.WaitForProps(item, 1000)
        Misc.Pause(100)

        name = str(item.Name).lower()
        props = str(item.Properties).lower()

        for word in words:
            if word in name or word in props:
                Items.Move(item, bag.Serial, -1)
                Misc.Pause(650)
                moved += 1
                break

    Player.HeadMessage(1151, "Gear moved: " + str(moved))


Gumps.CloseGump(GUMP_ID)
updateGump()

lastReset = 0

while True:
    Misc.Pause(1000)

    gd = Gumps.GetGumpData(GUMP_ID)

    if gd == None:
        Player.HeadMessage(68, "Farewell Treasure Hunter.")
        break

    if gd:

        if gd.buttonid == BTN_IDENTIFY:
            identifyItems()
            updateGump()

        elif gd.buttonid == BTN_LOOT:
            lootGemsRegsScrolls()
            updateGump()

        elif gd.buttonid == BTN_GOLD:
            pullGold()
            updateGump()

        elif gd.buttonid == BTN_GEAR:
            lootWeaponsArmor()
            updateGump()

        elif gd.buttonid == 0:
            Gumps.CloseGump(GUMP_ID)
            Player.HeadMessage(68, "Farewell Treasure Hunter.")
            break