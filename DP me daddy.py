#===================================================
# Scripts by HowYouLikeMeNow                      ==
#===================================================
# Auto detects poisonable weapins in backpack.    ==
# If charges are less then 5 it will recharge.    ==
# Will continuously check for weapins to be DPed. ==
#===================================================
# Keep some Deadly Poison potions on you          ==
#===================================================
import re

WEAPON_IDS = [0x1401, 0x1405, 0x13FF, 0x0F52, 0x1441, 0x13B6]

POTION_IDS = [0x0F0A]
REAPPLY_AT = 5
POISON_COOLDOWN_MS = 7500
POISON_APPLY_WAIT_MS = 4000
LOOP_DELAY_MS = 5000
COOLDOWN_TIMER = "dp_weapon_poison_cooldown"


def props_lines(item):
    Items.WaitForProps(item, 1000)
    return [str(p) for p in Items.GetPropStringList(item.Serial)]


def deadly_poison_charges(item):
    for line in props_lines(item):
        match = re.search(r"Deadly Poison Charges:\s*(\d+)", line, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return 0


def find_deadly_poison_potion():
    bag = Player.Backpack
    Items.WaitForContents(bag, 1000)

    for item in bag.Contains:
        if item.ItemID not in POTION_IDS:
            continue

        combined = (str(item.Name) + " " + " ".join(props_lines(item))).lower()

        if "deadly poison" in combined:
            return item

    return None


def wait_poison_cooldown():
    if Timer.Check(COOLDOWN_TIMER):
        Misc.Pause(Timer.Remaining(COOLDOWN_TIMER))


def poison_weapon(weapon):
    wait_poison_cooldown()

    potion = find_deadly_poison_potion()
    if potion is None:
        return False

    Player.UseSkill("Poisoning", True)

    if not Target.WaitForTarget(5000, False):
        return False

    Target.TargetExecute(potion)
    Misc.Pause(500)

    if not Target.WaitForTarget(5000, False):
        return False

    Target.TargetExecute(weapon)

    Timer.Create(COOLDOWN_TIMER, POISON_COOLDOWN_MS)

    Misc.Pause(POISON_APPLY_WAIT_MS)
    Items.WaitForProps(weapon, 1000)

    return True


def monitor_backpack_weapons():
    bag = Player.Backpack
    Items.UseItem(bag)
    Items.WaitForContents(bag, 1000)

    while True:
        Items.WaitForContents(bag, 1000)

        for weapon in bag.Contains:
            if weapon.ItemID not in WEAPON_IDS:
                continue

            if deadly_poison_charges(weapon) < REAPPLY_AT:
                poison_weapon(weapon)
                break

        Misc.Pause(LOOP_DELAY_MS)


monitor_backpack_weapons()