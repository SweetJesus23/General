# ============================================================
# Scripts by HowYouLikeMeNow
#=============================================================
#  =Vendor sell script=
# Automaticlly sells all items from the selected bag.
# 1. Target the vendor you wish to sell to.
# 2. Target the bag you wish to sell from.
# 3. Items in selected bag will sell automaticlly
#=============================================================

GUMP_ID = 987654

vendor_serial = 0
bag_serial = 0


def u16(n):
    return [(n >> 8) & 0xFF, n & 0xFF]


def u32(n):
    return [(n >> 24) & 0xFF, (n >> 16) & 0xFF, (n >> 8) & 0xFF, n & 0xFF]


def make_sell_packet(vendor, sell_items):
    # 0x9F Sell Reply
    # cmd, length, vendor serial, item count, item serial + amount
    length = 1 + 2 + 4 + 2 + (len(sell_items) * 6)

    pkt = [0x9F]
    pkt += u16(length)
    pkt += u32(vendor)
    pkt += u16(len(sell_items))

    for serial, amount in sell_items:
        pkt += u32(serial)
        pkt += u16(amount)

    return pkt


def is_inside_bag(item, target_bag_serial):
    parent = item.Container

    while parent != 0:
        if parent == target_bag_serial:
            return True

        parent_item = Items.FindBySerial(parent)
        if parent_item is None:
            return False

        parent = parent_item.Container

    return False


def get_all_items_in_bag(bag):
    found = []

    Items.UseItem(bag)
    Items.WaitForContents(bag, 1500)

    for item in bag.Contains:
        if item.IsContainer:
            Items.UseItem(item)
            Items.WaitForContents(item, 1000)
            found += get_all_items_in_bag(item)

        found.append(item)

    return found


def auto_sell():
    global vendor_serial, bag_serial

    if vendor_serial == 0:
        Misc.SendMessage("No vendor selected.", 33)
        return

    if bag_serial == 0:
        Misc.SendMessage("No bag selected.", 33)
        return

    bag = Items.FindBySerial(bag_serial)

    if bag is None or not bag.IsContainer:
        Misc.SendMessage("Selected bag is invalid.", 33)
        return

    Misc.SendMessage("Opening sell bag...", 68)
    Items.UseItem(bag)
    Items.WaitForContents(bag, 1500)

    bag_items = get_all_items_in_bag(bag)

    if len(bag_items) == 0:
        Misc.SendMessage("Bag is empty.", 33)
        return

    Misc.SendMessage("Opening vendor sell list...", 68)

    if not Misc.UseContextMenu(vendor_serial, "Sell", 3000):
        Misc.SendMessage("Could not open vendor Sell option.", 33)
        return

    Misc.Pause(1000)

    sell_items = []

    for item in bag_items:
        if item.Serial == bag_serial:
            continue

        if not is_inside_bag(item, bag_serial):
            continue

        amount = item.Amount
        if amount <= 0:
            amount = 1

        sell_items.append((item.Serial, amount))

    if len(sell_items) == 0:
        Misc.SendMessage("No items found to sell.", 33)
        return

    pkt = make_sell_packet(vendor_serial, sell_items)
    PacketLogger.SendToServer(pkt)
    Player.HeadMessage(68, "Your Rich!")
    Misc.SendMessage("Sold {} item entries from selected bag.".format(len(sell_items)), 68)

def draw_gump():
    gd = Gumps.CreateGump(True, True, True, False)
    Gumps.AddPage(gd, 0)

    # Full background image
    Gumps.AddImage(gd, 0, 0, 0x2B00)

    # Decoration
    Gumps.AddImage(gd, 110, 15, 0x9C57)
    Gumps.AddImage(gd, 86, 75, 0x2328)
    
    Gumps.AddLabel(gd, 62, 45, 0, "$ Get Rich Quick! $")

    # Button 1
    Gumps.AddButton(gd, 255, 75, 0x99C, 0x99C, 1, 1, 0)
    Gumps.AddLabel(gd, 242, 55, 1152, "Pick A Vendor")

    # Button 2
    Gumps.AddButton(gd, 255, 135, 0x99C, 0x99C, 2, 1, 0)
    Gumps.AddLabel(gd, 250, 115, 1152, "Pick A Bag")

    Gumps.SendGump(GUMP_ID, Player.Serial, 200, 200, gd.gumpDefinition, gd.gumpStrings)


def handle_button(button):
    global vendor_serial, bag_serial

    if button == 1:
        Misc.SendMessage("Target vendor.", 68)
        vendor_serial = Target.PromptTarget("Target vendor")
        Misc.SendMessage("Vendor set: 0x{:X}".format(vendor_serial), 68)

    elif button == 2:
        Misc.SendMessage("Target bag.", 68)
        bag_serial = Target.PromptTarget("Target bag")
        Misc.SendMessage("Bag set: 0x{:X}".format(bag_serial), 68)

        if vendor_serial != 0 and bag_serial != 0:
            auto_sell()


draw_gump()

while True:
    Gumps.WaitForGump(GUMP_ID, 1000)

    gd = Gumps.GetGumpData(GUMP_ID)
    if gd is not None and gd.hasResponse:
        button = gd.buttonid

        if button == 0:
            Misc.SendMessage("Get Rich Quick closed.", 33)
            break

        Gumps.CloseGump(GUMP_ID)
        handle_button(button)
        Misc.Pause(300)
        draw_gump()

    Misc.Pause(100)