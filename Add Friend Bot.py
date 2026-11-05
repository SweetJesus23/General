#=========================================================
#           ☺ Scripts by HowYouLikeMeNow ☺              ==
#=========================================================
# This will automatically any guild or alliance members ==
# to your friends list.                                 ==
#=========================================================
# Set to auto start at login or to a hotkey.            ==
# Will play quietly in the background.                  ==
#=========================================================

#====Before Running Script=====
#===========SET UP=============
# 1. Agents tab             ===
# 2. Friends tab            ===
# 3. Make a new list        ===
# 4. Title it guildalliance ===
#==============================


FRIEND_LIST_NAME = "guildalliance"
SCAN_RANGE = 18
SCAN_DELAY_MS = 1000
GREEN_FRIEND_NOTORIETY = 2

def get_nearby_green_players():
    f = Mobiles.Filter()
    f.Enabled = True
    f.RangeMax = SCAN_RANGE
    f.IsHuman = 1
    f.Friend = -1
    f.Notorieties.Add(GREEN_FRIEND_NOTORIETY)
    return Mobiles.ApplyFilter(f)

while True:
    try:
        for mob in get_nearby_green_players():
            if mob is None:
                continue

            if mob.Serial == Player.Serial:
                continue

            if Friend.IsFriend(mob.Serial):
                continue

            name = mob.Name
            if name is None or name == "":
                name = "Unknown"

            Friend.AddPlayer(FRIEND_LIST_NAME, name, mob.Serial)

        Misc.Pause(SCAN_DELAY_MS)

    except:
        Misc.Pause(3000)