                #=========================================
                #= Champion & Mini Boss Discord Alerts ===
                #=========================================
                #===== Scripts by HowYouLikeMeNow ========
                #=========================================
#==========================================================================
#= In-game book Gump for reporting Champion and Mini Boss UP/DOWN status. =
#========== Sends announcements to Alliance Chat and Discord ==============
#====== Champion DOWN alerts include a 4-hour respawn estimate. ===========
#==========================================================================
#=                                                                        =
#=                ##        #######   #######   ########                  =
#=                ##       ##     ## ##     ##     ##                     =
#=                ##       ##     ## ##            ##                     =
#=                ##       ##     ##  #######      ##                     =
#=                ##       ##     ##         ##    ##                     =
#=                ##       ##     ## ##     ##     ##                     =
#=                ########  #######   #######      ##                     =
#=                                                                        =
#========================================================================== 
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta


RELAY_URL = 'https://uo-spawn-alerts.howyoulikemenow1323.workers.dev/'
RELAY_TIMEOUT_SECONDS = 10
gumpNumber = 213640  

upDownList = ['Abyss (Champ)', 'Deceit (Champ)', 'Despise (Champ)', 'Double (Champ)', 'Destard (Champ)', 'Covetous (Champ)', 'Ice (Champ)', 'Orc (Champ)', 'Pirate (Champ)', 'Shame (Champ)', 'Terathan (Champ)', 'Wrong (Champ)', 'Lich Kahn (MiniBoss)', 'Arch D (MiniBoss)', 'Montor (MiniBoss)', 'Hythloth (MiniBoss)', 'Dreadwing (MiniBoss)', 'Akor (MiniBoss)', 'Fafnir (MiniBoss)', 'The Warden (MiniBoss)', 'Warlock (MiniBoss)', 'Medusa (MiniBoss)']
champions = [name for name in upDownList if '(Champ)' in name]
miniBosses = [name for name in upDownList if '(MiniBoss)' in name]


BTN_MINIMIZE = 9000
BTN_CHAMPIONS = 9001
BTN_MINIBOSSES = 9002
BTN_UP_BASE = 1000
BTN_DOWN_BASE = 2000

minimized = False
activeTab = 0  


def postRelayAnnouncement(name, isUp):
    """Send structured data to the Cloudflare Worker, never a webhook URL."""
    spawn_name = name.replace(' (Champ)', '').replace(' (MiniBoss)', '')
    payload = {
        'name': spawn_name,
        'status': 'UP' if isUp else 'DOWN',
        'character': Player.Name
    }
    data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        url=RELAY_URL,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'RazorEnhanced-SpawnAlerts/1.0'
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(request, timeout=RELAY_TIMEOUT_SECONDS) as response:
            if response.status == 200:
                return True
            print('Discord relay returned status: ' + str(response.status))
    except urllib.error.HTTPError as error:
        print('Discord relay HTTP error: ' + str(error.code))
    except urllib.error.URLError as error:
        print('Discord relay connection error: ' + str(error.reason))
    except Exception as error:
        print('Discord relay error: ' + str(error))
    return False


def announce(name, isUp):
    """Alliance Chat uses the player's local clock; Discord uses relay timestamps."""
    spawn_name = name.replace(' (Champ)', '').replace(' (MiniBoss)', '')
    spawn_type = 'Champ' if '(Champ)' in name else 'Boss'
    if isUp:
        message = spawn_name + ' ' + spawn_type + ' is UP!'
    elif '(Champ)' in name:
        future_time = datetime.now() + timedelta(hours=4)
        if future_time.second >= 30:
            future_time += timedelta(minutes=1)
        rounded_time = future_time.replace(second=0, microsecond=0)
        message = (spawn_name + ' ' + spawn_type + ' is DOWN! Next UP at ' +
                   rounded_time.strftime('%I:%M %p'))
    else:
        message = spawn_name + ' Boss is DOWN!'

    # Keep Alliance Chat independent: it works even when the relay fails.
    try:
        Player.ChatAlliance(message)
    except Exception as error:
        print('Alliance Chat error: ' + str(error))

    postRelayAnnouncement(name, isUp)



BOOK_IMAGE_ID = 0x2B00
BOOK_X, BOOK_Y = 0, 35
SCREEN_X, SCREEN_Y = 400, 400

NAV_BG = (55, 0, 296, 32, 430)
CHAMP_TAB_BUTTON = (65, 5)
CHAMP_TAB_TEXT = (98, 5)
MINI_TAB_BUTTON = (184, 5)
MINI_TAB_TEXT = (217, 5)
MINIMIZE_BUTTON = (312, 5)
NAV_ACTIVE_HUE, NAV_INACTIVE_HUE = 1152, 902

MINI_BG = (0, 0, 145, 35, 430)
MINI_TITLE = (8, 8)
MINI_EXPAND_BUTTON = (120, -9)

UP_BUTTON_ART = (250, 251)
DOWN_BUTTON_ART = (252, 253)
TEXT_HUE = 0
HEADER_HUE = 1109

# Each page: heading, heading X/Y, text X, UP X, DOWN X,
# first row Y, spacing between rows.
PAGE_LAYOUTS = {
    'champions': {
        'split': 6,
        'left':  ('CHAMPIONS', 91, 46, 65, 147, 170, 70, 27),
        'right': ('CHAMPIONS', 249, 46, 224, 300, 323, 70, 27),
    },
    'minibosses': {
        'split': 5,
        'left':  ('MINI BOSSES', 87, 48, 65, 147, 170, 75, 27),
        'right': ('MINI BOSSES', 245, 48, 224, 305, 328, 75, 27),
    },
}



def draw_background(gd, config):
    x, y, w, h, graphic = config
    Gumps.AddBackground(gd, x, y, w, h, graphic)


def draw_spawn_page(gd, names, layout):
    header, header_x, header_y, text_x, up_x, down_x, first_y, spacing = layout
    Gumps.AddLabel(gd, header_x, header_y, HEADER_HUE, header)

    for row, name in enumerate(names):
        y = first_y + row * spacing
        label = name.replace(' (Champ)', '').replace(' (MiniBoss)', '')
        button_index = upDownList.index(name)

        Gumps.AddLabel(gd, text_x, y, TEXT_HUE, label)
        Gumps.AddButton(gd, up_x, y,
                        UP_BUTTON_ART[0], UP_BUTTON_ART[1],
                        BTN_UP_BASE + button_index, True, False)
        Gumps.AddTooltip(gd, 3012171, name + ' is UP')
        Gumps.AddButton(gd, down_x, y,
                        DOWN_BUTTON_ART[0], DOWN_BUTTON_ART[1],
                        BTN_DOWN_BASE + button_index, True, False)
        Gumps.AddTooltip(gd, 3012171, name + ' is DOWN')


def drawGump():
    gd = Gumps.CreateGump(True, True, False, False)

    if minimized:
        draw_background(gd, MINI_BG)
        Gumps.AddLabel(gd, MINI_TITLE[0], MINI_TITLE[1], NAV_ACTIVE_HUE, 'Champs & Bosses')
        Gumps.AddButton(gd, MINI_EXPAND_BUTTON[0], MINI_EXPAND_BUTTON[1],
                        0x2B03, 0x2B03, BTN_MINIMIZE, True, False)
        Gumps.AddTooltip(gd, 3012171, 'Expand')
    else:
        draw_background(gd, NAV_BG)
        Gumps.AddButton(gd, CHAMP_TAB_BUTTON[0], CHAMP_TAB_BUTTON[1],
                        4005, 4007, BTN_CHAMPIONS, True, False)
        Gumps.AddLabel(gd, CHAMP_TAB_TEXT[0], CHAMP_TAB_TEXT[1],
                       NAV_ACTIVE_HUE if activeTab == 0 else NAV_INACTIVE_HUE,
                       'Champions')
        Gumps.AddButton(gd, MINI_TAB_BUTTON[0], MINI_TAB_BUTTON[1],
                        4005, 4007, BTN_MINIBOSSES, True, False)
        Gumps.AddLabel(gd, MINI_TAB_TEXT[0], MINI_TAB_TEXT[1],
                       NAV_ACTIVE_HUE if activeTab == 1 else NAV_INACTIVE_HUE,
                       'Mini Bosses')
        Gumps.AddButton(gd, MINIMIZE_BUTTON[0], MINIMIZE_BUTTON[1],
                        4017, 4019, BTN_MINIMIZE, True, False)
        Gumps.AddTooltip(gd, 3012171, 'Minimize')

        Gumps.AddImage(gd, BOOK_X, BOOK_Y, BOOK_IMAGE_ID)
        category = 'champions' if activeTab == 0 else 'minibosses'
        names = champions if activeTab == 0 else miniBosses
        config = PAGE_LAYOUTS[category]
        split = config['split']
        draw_spawn_page(gd, names[:split], config['left'])
        draw_spawn_page(gd, names[split:], config['right'])

    Gumps.CloseGump(gumpNumber)
    Gumps.SendGump(gumpNumber, Player.Serial, SCREEN_X, SCREEN_Y,
                   gd.gumpDefinition, gd.gumpStrings)

drawGump()

while True:
    gd = Gumps.GetGumpData(gumpNumber)
    if gd and gd.buttonid != -1:
        button = gd.buttonid
        
        gd.buttonid = -1

        if button == BTN_MINIMIZE:
            minimized = not minimized
        elif button == BTN_CHAMPIONS:
            activeTab = 0
            minimized = False
        elif button == BTN_MINIBOSSES:
            activeTab = 1
            minimized = False
        elif BTN_UP_BASE <= button < BTN_UP_BASE + len(upDownList):
            announce(upDownList[button - BTN_UP_BASE], True)
        elif BTN_DOWN_BASE <= button < BTN_DOWN_BASE + len(upDownList):
            announce(upDownList[button - BTN_DOWN_BASE], False)

        drawGump()
    else:
        Misc.Pause(100)
