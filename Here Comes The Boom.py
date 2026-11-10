#=================================================
#========= Scripts By HowYouLikeMeNow ============
#=================================================
#=== Throws Explosion Pots perfectly everytime ===
#=================================================
#= Recommend setting up a Set Last Target hotkey =
#=================================================

import sys
import time
from datetime import datetime
from System.Collections.Generic import List
from System import Int32
import random
from System import Byte
import time
import re


delay_movement = 800
delay_chat = 350

ids_potions_explosion = 0x0F0D


hues_messages_potions_explosion = 11


def filter_serials(serials_target):

    fil = Mobiles.Filter()
    fil.Enabled = True
    fil.RangeMax = 12
    fil.IsHuman = True
    fil.IsGhost = False
    fil.Notorieties = List[Byte](bytes([1, 2, 3, 4, 5, 6]))
    mobiles = Mobiles.ApplyFilter(fil)

    for mobile in list(mobiles):
        if not mobile.Serial == serials_target:
            mobiles.Remove(mobile)

    return mobiles


def player_position():

    position = Player.Position
    player_x = position.X
    player_y = position.Y
    player_z = position.Z

    return player_x, player_y, player_z


def distance(serials_target):

    lists_mobiles = filter_serials(serials_target)

    if len(lists_mobiles) > 0:
        for mobile in lists_mobiles:
            if mobile.Serial == serials_target:
                if Player.DistanceTo(serials_target) <= 12:
                    return True

    return False


def is_friendly_target(serials_target):
    mobile = Mobiles.FindBySerial(serials_target)
    if mobile is None:
        return False
    return (Friend.IsFriend(serials_target)
            or mobile.InParty
            or mobile.Notoriety == 2)


def potions_find():

    items_potion = Items.FindByID(ids_potions_explosion, 0, Player.Backpack.Serial, True, False)

    return items_potion


def potions_prime(items_potion):

    cursor_wait()

    Items.UseItem(items_potion.Serial)
    Misc.Pause(250)
    cursor_cancel()


def potions_throw(items_potion):

    while not Journal.SearchByName('2', str(Player.Name)): 
        Misc.Pause(10)

    Items.UseItem(items_potion.Serial)


def throw_to_empty_tile():
    
    player_x, player_y, player_z = player_position()
    occupied = set([(player_x, player_y)])

    fil = Mobiles.Filter()
    fil.Enabled = True
    fil.RangeMax = 8
    for mobile in Mobiles.ApplyFilter(fil):
        occupied.add((mobile.Position.X, mobile.Position.Y))

    candidates = []
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            dist = max(abs(dx), abs(dy))
            if 2 <= dist <= 4:
                x, y = player_x + dx, player_y + dy
                if (x, y) not in occupied:
                    candidates.append((x, y))

    if candidates:
        x, y = random.choice(candidates)
    else:
        
        x, y = player_x, player_y + 4

    Target.TargetExecute(x, y, player_z)


def potions_target(serials_target, items_potion):
    Misc.Pause(775)
    if is_friendly_target(serials_target):
        throw_to_empty_tile()
        messages(hues_messages_potions_explosion, 'LAST TARGET IS FRIENDLY')
    elif not distance(serials_target):
        throw_to_empty_tile()
        messages(hues_messages_potions_explosion, 'TARGET OUT OF RANGE')
    else:
        Target.TargetExecute(serials_target)


def potions_count():

    if Items.BackpackCount(ids_potions_explosion, -1) <= 1:
        messages(hues_messages_potions_explosion, 'OUT OF EXPLO POTS')


def cursor_wait():

    if Target.HasTarget():
        while Target.HasTarget():
            Misc.Pause(10)


def cursor_cancel():

    if Target.HasTarget():
        Target.Cancel()


def messages(message_hue, message_content):

    Player.HeadMessage(message_hue, message_content)
    Misc.Pause(delay_chat)


def call(serials_target):

    if is_friendly_target(serials_target):
        messages(hues_messages_potions_explosion, 'LAST TARGET IS FRIENDLY')
        return

    items_potion = potions_find()
    if not items_potion:
        messages(hues_messages_potions_explosion, 'OUT OF EXPLO POTS')
        return

    success_distance = distance(serials_target)
    if not success_distance:
        messages(hues_messages_potions_explosion, 'TARGET OUT OF RANGE')
        return

    if items_potion and success_distance:
        potions_prime(items_potion)
        potions_throw(items_potion)
        potions_target(serials_target, items_potion)
        potions_count()


Journal.Clear()
serials_target = Target.GetLast()
call(serials_target)