"""Draws the pixel-art bedroom for the season page.
Logical canvas is 400x225 (16:9); saved 4x as img/room.png. The page positions the TV screen,
cartridge shelf, lava lamp blobs and Roomba over this image using the same 400x225 coordinates.
Run from the repo root:  python3 tools/draw_room.py
"""
import random
from PIL import Image, ImageDraw, ImageFont

W, H, S = 400, 225, 4
INK = (16, 8, 32, 255)
random.seed(7)

FONT = ImageFont.truetype('fonts/Silkscreen-Regular.ttf', 8)
FONTB = ImageFont.truetype('fonts/Silkscreen-Bold.ttf', 8)


def rgba(c):
    return c if len(c) == 4 else (*c, 255)


def outline(layer):
    """1px ink outline around everything drawn on a layer (like the season's sprites)."""
    px = layer.load()
    w, h = layer.size
    out = layer.copy()
    op = out.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] > 0:
                        op[x, y] = INK
                        break
    return out


class Obj:
    """draw on a transparent layer, then outline it and paste it into the room"""
    def __init__(self, room, ol=True):
        self.room, self.ol = room, ol
        self.layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.layer)
        self.d.fontmode = '1'

    def __enter__(self):
        return self.d

    def __exit__(self, *a):
        lay = outline(self.layer) if self.ol else self.layer
        self.room.alpha_composite(lay)


def text(d, xy, s, fill, font=FONT, anchor='la'):
    d.text(xy, s, font=font, fill=rgba(fill), anchor=anchor)


room = Image.new('RGBA', (W, H), (0, 0, 0, 255))
d = ImageDraw.Draw(room)
d.fontmode = '1'

# ------------------------------------------------------------------ wall: 80s wallpaper
WALL, WALL2, WALL3 = (52, 34, 90), (60, 40, 104), (44, 28, 78)
d.rectangle((0, 0, W, 148), fill=WALL)
for x in range(0, W, 14):
    d.rectangle((x, 0, x + 5, 148), fill=WALL2)
    d.line((x + 6, 0, x + 6, 148), fill=WALL3)
# memphis confetti: tiny teal zigzags and pink dots
for y in range(10, 140, 18):
    for x in range((y // 18 % 2) * 9 + 3, W, 18):
        if (x * 7 + y * 3) % 5 == 0:
            d.point([(x, y), (x + 1, y - 1), (x + 2, y), (x + 3, y - 1)], fill=(63, 200, 200))
        elif (x + y) % 3 == 0:
            d.rectangle((x, y, x + 1, y + 1), fill=(220, 70, 180))
# picture rail near ceiling
d.rectangle((0, 3, W, 5), fill=(84, 58, 132))
d.line((0, 6, W, 6), fill=WALL3)

# ------------------------------------------------------------------ floor: carpet
FLOOR = (30, 52, 80)
d.rectangle((0, 149, W, H), fill=FLOOR)
for y in range(150, H):
    for x in range(0, W):
        r = random.random()
        if r < 0.06:
            d.point((x, y), fill=(38, 64, 96))
        elif r < 0.09:
            d.point((x, y), fill=(24, 42, 66))
# skirting board
d.rectangle((0, 144, W, 149), fill=(196, 182, 160))
d.line((0, 144, W, 144), fill=(232, 222, 204))
d.line((0, 149, W, 149), fill=(110, 96, 84))

# ------------------------------------------------------------------ window with night sky + curtains
with Obj(room) as o:
    o.rectangle((10, 16, 58, 64), fill=(226, 214, 196))           # frame
    o.rectangle((13, 19, 55, 61), fill=(14, 16, 44))              # sky
    for i in range(40):
        y = 19 + i
        if i > 28:
            o.line((13, y, 55, y), fill=(20 + (i - 28), 22 + (i - 28), 60 + (i - 28) * 2))
    o.ellipse((40, 23, 49, 32), fill=(250, 240, 190))              # moon
    o.ellipse((43, 22, 51, 30), fill=(14, 16, 44))
    for sx, sy in ((18, 24), (27, 30), (33, 21), (22, 40), (50, 40), (36, 36), (16, 33)):
        o.point((sx, sy), fill=(255, 255, 230))
    # far city skyline with lit windows
    for bx, bh in ((13, 10), (20, 14), (28, 8), (34, 16), (42, 11), (49, 13)):
        o.rectangle((bx, 61 - bh, bx + 6, 61), fill=(26, 24, 58))
        for wy in range(61 - bh + 2, 60, 3):
            if (bx + wy) % 4 == 0:
                o.point((bx + 2, wy), fill=(255, 210, 90))
            if (bx * 3 + wy) % 5 == 0:
                o.point((bx + 4, wy), fill=(255, 225, 74))
    o.line((34, 19, 34, 61), fill=(226, 214, 196))                 # mullions
    o.line((13, 40, 55, 40), fill=(226, 214, 196))
    o.rectangle((8, 64, 60, 67), fill=(200, 186, 164))             # sill
with Obj(room) as o:                                               # curtains
    o.rectangle((4, 12, 64, 15), fill=(150, 110, 70))
    for cx0, cx1 in ((5, 15), (53, 63)):
        o.rectangle((cx0, 15, cx1, 72), fill=(232, 80, 170))
        for x in range(cx0 + 2, cx1, 3):
            o.line((x, 16, x, 72), fill=(196, 52, 140))

# ------------------------------------------------------------------ poster 1: ROOMBA KING
with Obj(room) as o:
    o.rectangle((68, 12, 106, 62), fill=(24, 22, 62))
    o.rectangle((70, 14, 104, 60), outline=(255, 225, 74))
    # rays
    for i, (ex, ey) in enumerate(((72, 18), (102, 18), (72, 46), (102, 46), (87, 16))):
        o.line((87, 36, ex, ey), fill=(60, 50, 110))
    # crown
    o.polygon([(80, 30), (80, 23), (83, 27), (87, 21), (91, 27), (94, 23), (94, 30)], fill=(255, 225, 74))
    o.point((87, 26), fill=(255, 60, 70))
    # roomba (2x of the season sprite)
    o.ellipse((76, 30, 98, 44), fill=(120, 120, 140))
    o.ellipse((79, 32, 95, 41), fill=(190, 190, 210))
    o.ellipse((83, 34, 91, 39), fill=(60, 60, 75))
    o.rectangle((86, 36, 88, 37), fill=(60, 255, 120))
    o.rectangle((78, 42, 96, 44), fill=(70, 70, 90))
    text(o, (87, 47), 'ROOMBA', (255, 255, 255), FONTB, 'mt')
    text(o, (87, 54), 'KING', (255, 225, 74), FONTB, 'mt')
# tape
for tx, ty in ((67, 11), (101, 11)):
    d.rectangle((tx, ty, tx + 5, ty + 2), fill=(236, 230, 200))

# ------------------------------------------------------------------ poster 2: band poster "THE PAPERS"
with Obj(room) as o:
    o.rectangle((112, 20, 146, 70), fill=(255, 63, 209))
    o.polygon([(124, 24), (134, 24), (129, 32), (136, 32), (122, 46), (126, 35), (119, 35)], fill=(255, 225, 74))  # bolt
    text(o, (129, 47), 'THE', (16, 8, 32), FONT, 'mt')
    text(o, (129, 54), 'PAPERS', (255, 255, 255), FONTB, 'mt')
    o.rectangle((114, 63, 144, 68), fill=(16, 8, 32))
    text(o, (129, 63), 'TOUR 86', (63, 240, 224), FONT, 'mt')
for tx, ty in ((111, 19), (141, 19)):
    d.rectangle((tx, ty, tx + 5, ty + 2), fill=(236, 230, 200))

# ------------------------------------------------------------------ poster 3: LIMINAL (backrooms corridor)
with Obj(room) as o:
    x0, y0, x1, y1 = 226, 10, 274, 48
    o.rectangle((x0, y0, x1, y1), fill=(196, 178, 82))
    vx, vy = 250, 26                                   # vanishing point
    o.polygon([(x0 + 1, y1 - 9), (vx - 5, vy + 4), (vx + 5, vy + 4), (x1 - 1, y1 - 9)], fill=(150, 130, 70))  # floor
    o.polygon([(x0 + 1, y0 + 1), (vx - 5, vy - 4), (vx + 5, vy - 4), (x1 - 1, y0 + 1)], fill=(222, 212, 150))  # ceiling
    o.rectangle((vx - 5, vy - 4, vx + 5, vy + 4), fill=(110, 96, 48))   # far doorway
    o.line((x0 + 1, y0 + 1, vx - 5, vy - 4), fill=(170, 150, 70))
    o.line((x1 - 1, y0 + 1, vx + 5, vy - 4), fill=(170, 150, 70))
    o.line((x0 + 1, y1 - 9, vx - 5, vy + 4), fill=(130, 112, 56))
    o.line((x1 - 1, y1 - 9, vx + 5, vy + 4), fill=(130, 112, 56))
    o.rectangle((vx - 3, y0 + 4, vx + 3, y0 + 5), fill=(255, 255, 230))   # fluorescent tube
    o.rectangle((vx - 1, vy - 1, vx + 1, vy + 3), fill=(92, 224, 122))    # tiny green zombie far away
    o.point((vx, vy - 2), fill=(92, 224, 122))
    o.rectangle((x0 + 1, y1 - 8, x1 - 1, y1 - 1), fill=(16, 8, 32))
    text(o, (250, y1 - 8), 'LIMINAL', (255, 225, 74), FONTB, 'mt')
for tx, ty in ((225, 9), (269, 9)):
    d.rectangle((tx, ty, tx + 5, ty + 2), fill=(236, 230, 200))

# ------------------------------------------------------------------ poster 4: NO PUSH TO MAIN sign
with Obj(room) as o:
    o.rectangle((308, 10, 388, 52), fill=(244, 240, 228))
    o.rectangle((310, 12, 386, 50), outline=(220, 40, 50))
    o.ellipse((313, 18, 337, 42), fill=(220, 40, 50))
    o.ellipse((316, 21, 334, 39), fill=(244, 240, 228))
    # up arrow (a push) inside the no-sign
    o.polygon([(325, 23), (330, 29), (327, 29), (327, 36), (323, 36), (323, 29), (320, 29)], fill=(16, 8, 32))
    o.line((318, 37, 332, 23), fill=(220, 40, 50), width=3)
    text(o, (363, 17), 'NO PUSH', (220, 40, 50), FONTB, 'mt')
    text(o, (363, 26), 'TO MAIN', (16, 8, 32), FONTB, 'mt')
    text(o, (363, 38), 'ESP. FRIDAYS', (110, 100, 110), FONT, 'mt')
for tx, ty in ((307, 9), (383, 9)):
    d.rectangle((tx, ty, tx + 5, ty + 2), fill=(236, 230, 200))

# ------------------------------------------------------------------ cartridge shelf unit (cartridges are HTML on top)
with Obj(room) as o:
    WOOD, WOODD, WOODL = (138, 84, 46), (100, 58, 32), (170, 110, 64)
    o.rectangle((298, 58, 398, 170), fill=WOOD)
    o.rectangle((298, 58, 398, 61), fill=WOODL)
    o.rectangle((303, 64, 393, 147), fill=(46, 26, 22))           # inner back (cartridge area)
    for y in range(66, 147, 6):
        o.line((304, y, 392, y), fill=(52, 30, 26))
    o.rectangle((303, 148, 393, 151), fill=WOODL)
    o.rectangle((303, 152, 393, 166), fill=WOODD)                 # drawer
    o.rectangle((304, 153, 392, 165), outline=(80, 46, 26))
    o.rectangle((337, 156, 359, 162), fill=(230, 220, 190))
    text(o, (348, 156), 'CARTS', (16, 8, 32), FONT, 'mt')
    o.rectangle((298, 166, 300, 172), fill=WOODD)
    o.rectangle((396, 166, 398, 172), fill=WOODD)

# ------------------------------------------------------------------ bed (left)
with Obj(room) as o:
    o.rectangle((0, 92, 9, 194), fill=(170, 110, 64))             # headboard
    o.rectangle((2, 96, 7, 120), fill=(196, 132, 80))
    o.rectangle((9, 158, 126, 176), fill=(150, 94, 52))           # frame
    o.rectangle((12, 176, 16, 194), fill=(120, 72, 40))           # legs
    o.rectangle((118, 176, 122, 194), fill=(120, 72, 40))
    o.rectangle((9, 126, 126, 158), fill=(240, 236, 226))         # mattress / sheet
with Obj(room) as o:                                              # under-bed shadow (no outline)
    pass
d.rectangle((17, 177, 117, 194), fill=(14, 22, 38))
with Obj(room) as o:
    o.rounded_rectangle((11, 112, 40, 130), 4, fill=(250, 248, 240))   # pillow
    o.line((14, 127, 37, 127), fill=(214, 208, 196))
    # blanket with 80s triangle pattern
    o.polygon([(36, 122), (126, 122), (126, 166), (40, 166)], fill=(70, 200, 210))
    for x in range(42, 124, 10):
        o.polygon([(x, 166), (x + 5, 156), (x + 10, 166)], fill=(255, 63, 209))
    for x in range(46, 122, 12):
        o.rectangle((x, 132, x + 3, 135), fill=(255, 225, 74))
        o.line((x + 6, 144, x + 9, 141), fill=(16, 8, 32))
    o.rectangle((36, 122, 126, 127), fill=(240, 236, 226))         # folded sheet
    o.line((36, 127, 126, 127), fill=(200, 196, 186))
# plush on the bed: tiny pixel zombie plush (green)
with Obj(room) as o:
    o.rectangle((100, 110, 109, 121), fill=(92, 224, 122))
    o.rectangle((98, 114, 100, 118), fill=(92, 224, 122))
    o.rectangle((109, 114, 111, 118), fill=(92, 224, 122))
    o.point([(102, 113), (107, 113)], fill=(16, 8, 32))
    o.line((102, 117, 107, 117), fill=(40, 120, 60))
    o.rectangle((101, 108, 108, 110), fill=(70, 150, 80))

# ------------------------------------------------------------------ nightstand + lava lamp (blobs animate in HTML)
with Obj(room) as o:
    o.rectangle((128, 120, 146, 162), fill=(150, 94, 52))
    o.rectangle((128, 120, 146, 123), fill=(180, 120, 70))
    o.rectangle((131, 128, 143, 140), outline=(110, 66, 36))
    o.rectangle((136, 133, 138, 135), fill=(230, 200, 120))
    o.rectangle((131, 145, 143, 157), outline=(110, 66, 36))
    o.rectangle((136, 150, 138, 152), fill=(230, 200, 120))
with Obj(room) as o:
    o.polygon([(133, 112), (141, 112), (143, 119), (131, 119)], fill=(196, 170, 90))   # base
    o.polygon([(134, 99), (140, 99), (141, 111), (133, 111)], fill=(255, 92, 60))      # glass
    o.polygon([(135, 95), (139, 95), (140, 98), (134, 98)], fill=(196, 170, 90))       # cap
    o.line((134, 113, 140, 113), fill=(150, 126, 60))
# soft glow around the lamp on the wall
for rr, a in ((22, 18), (15, 22), (9, 26)):
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((137 - rr, 105 - rr, 137 + rr, 105 + rr), fill=(255, 110, 60, a))
    gm = Image.new('L', (W, H), 0)
    ImageDraw.Draw(gm).rectangle((0, 0, W, 119), fill=255)
    glow.putalpha(Image.composite(glow.getchannel('A'), Image.new('L', (W, H), 0), gm))
    # don't glow over the glass itself
    room.alpha_composite(glow)

# ------------------------------------------------------------------ dresser + CRT TV
with Obj(room) as o:
    o.rectangle((146, 132, 294, 164), fill=(150, 94, 52))
    o.rectangle((146, 132, 294, 136), fill=(180, 120, 70))
    for dx0 in (150, 222):
        o.rectangle((dx0, 140, dx0 + 68, 160), outline=(110, 66, 36))
        o.rectangle((dx0 + 30, 148, dx0 + 38, 150), fill=(230, 200, 120))
    o.rectangle((150, 164, 154, 168), fill=(110, 66, 36))
    o.rectangle((286, 164, 290, 168), fill=(110, 66, 36))
with Obj(room) as o:                                              # antenna
    o.line((176, 51, 164, 25), fill=(200, 200, 216))
    o.line((178, 51, 192, 23), fill=(200, 200, 216))
    o.ellipse((163, 23, 166, 26), fill=(255, 60, 70))
    o.ellipse((191, 21, 194, 24), fill=(255, 60, 70))
    o.rectangle((172, 49, 182, 53), fill=(60, 56, 70))
with Obj(room) as o:                                              # TV body
    o.rounded_rectangle((152, 52, 292, 133), 5, fill=(120, 76, 44))      # woodgrain cabinet
    for y in range(56, 130, 4):
        o.line((154, y, 290, y + (1 if y % 8 else 0)), fill=(132, 86, 50))
    o.rounded_rectangle((156, 56, 266, 130), 6, fill=(36, 34, 44))       # bezel
    o.rounded_rectangle((159, 59, 265, 127), 8, fill=(12, 18, 22))       # glass (HTML screen sits on top)
    o.rectangle((268, 56, 289, 130), fill=(60, 56, 70))                  # control panel
    o.ellipse((271, 60, 285, 74), fill=(200, 200, 216))
    o.ellipse((274, 63, 282, 71), fill=(130, 130, 150))
    o.ellipse((272, 78, 284, 90), fill=(200, 200, 216))
    o.ellipse((275, 81, 281, 87), fill=(130, 130, 150))
    for y in range(96, 124, 3):
        o.line((271, y, 286, y), fill=(30, 28, 38))                      # speaker grille
    o.rectangle((270, 126, 274, 128), fill=(60, 255, 120))               # power led
    o.rectangle((160, 133, 170, 136), fill=(60, 56, 70))
    o.rectangle((274, 133, 284, 136), fill=(60, 56, 70))

# ------------------------------------------------------------------ rug
with Obj(room) as o:
    o.ellipse((146, 176, 322, 220), fill=(120, 40, 110))
    o.ellipse((154, 180, 314, 216), fill=(160, 60, 150))
    o.ellipse((166, 185, 302, 211), fill=(255, 140, 60))
    o.ellipse((176, 189, 292, 207), fill=(160, 60, 150))

# ------------------------------------------------------------------ Atari-style console on the floor
AX0, AY0, AX1, AY1 = 188, 168, 242, 186
with Obj(room) as o:
    o.polygon([(AX0 + 4, AY0), (AX1 - 4, AY0), (AX1, AY0 + 6), (AX0, AY0 + 6)], fill=(28, 26, 32))    # top
    for x in range(AX0 + 6, AX1 - 5, 3):
        o.line((x, AY0 + 1, x, AY0 + 5), fill=(44, 42, 50))                                       # ridges
    o.rectangle((AX0, AY0 + 6, AX1, AY1), fill=(110, 64, 34))                                     # woodgrain front
    for y in range(AY0 + 7, AY1, 2):
        o.line((AX0 + 1, y, AX1 - 1, y), fill=(130, 80, 44) if y % 4 else (96, 54, 28))
    o.rectangle((AX0 + 18, AY0 - 2, AX1 - 18, AY0 + 2), fill=(10, 10, 14))                        # cartridge slot
    for i, sx in enumerate((AX0 + 4, AX0 + 9, AX1 - 12, AX1 - 7)):
        o.rectangle((sx, AY0 + 9, sx + 3, AY0 + 13), fill=(30, 28, 34))
        o.rectangle((sx + 1, AY0 + 9 + (i % 2) * 2, sx + 2, AY0 + 11 + (i % 2) * 2), fill=(210, 210, 220))
    o.rectangle((AX0 + 22, AY0 + 9, AX1 - 22, AY0 + 12), fill=(30, 28, 34))
    o.point((AX0 + 25, AY0 + 10), fill=(255, 60, 70))

# joystick cable from console to Unity's hands
cable = [(AX1, AY0 + 10), (246, 184), (250, 190), (251, 196), (254, 198)]
d.line(cable, fill=(16, 8, 32), width=1)

# ------------------------------------------------------------------ Unity (she/her), sitting cross-legged, back view, playing
UX, UY = 244, 146   # top-left of her 56x76 box
HAIR, HAIR2, HAIR3, HAIRL = (226, 212, 176), (198, 174, 128), (160, 130, 90), (246, 240, 218)
J1, J2, J3 = (156, 92, 144), (122, 68, 114), (186, 120, 172)
PANTS, PANTS2 = (40, 36, 54), (62, 56, 80)
SKIN = (238, 192, 152)
PINK = (255, 63, 209)


def U(x, y):
    return (UX + x, UY + y)


def ub(b):
    return (UX + b[0], UY + b[1], UX + b[2], UY + b[3])


with Obj(room) as o:
    # crossed legs (knees out to the sides)
    o.ellipse(ub((2, 56, 26, 72)), fill=PANTS)
    o.ellipse(ub((28, 56, 54, 72)), fill=PANTS)
    o.ellipse(ub((12, 52, 44, 74)), fill=PANTS)
    o.line((U(6, 60), U(14, 58)), fill=PANTS2)
    o.line((U(42, 58), U(50, 61)), fill=PANTS2)
    o.ellipse(ub((3, 64, 9, 69)), fill=PINK)          # socks peeking out
    o.ellipse(ub((47, 64, 53, 69)), fill=PINK)
    # torso (jacket)
    o.rounded_rectangle(ub((12, 26, 44, 60)), 6, fill=J1)
    o.rectangle(ub((36, 30, 43, 58)), fill=J2)
    o.ellipse(ub((9, 21, 47, 37)), fill=J1)
    o.line((U(12, 26), U(20, 23)), fill=J3)
    # left arm reaching to the joystick
    o.polygon([U(12, 27), U(4, 38), U(5, 46), U(11, 46), U(15, 36)], fill=J1)
    o.line((U(6, 38), U(12, 30)), fill=J3)
    # right elbow
    o.polygon([U(43, 28), U(50, 38), U(48, 46), U(42, 44)], fill=J2)
    # joystick: base, stick, red button
    o.rectangle(ub((0, 44, 13, 51)), fill=(26, 24, 30))
    o.line((U(1, 45), U(12, 45)), fill=(60, 58, 70))
    o.rectangle(ub((5, 36, 6, 44)), fill=(40, 38, 46))
    o.ellipse(ub((3, 32, 8, 37)), fill=(40, 38, 46))
    o.rectangle(ub((9, 46, 11, 48)), fill=(255, 60, 70))
    o.ellipse(ub((2, 38, 9, 45)), fill=SKIN)          # hand on the stick
    # head + long blonde hair down her back
    o.ellipse(ub((15, 1, 41, 27)), fill=HAIR)
    o.polygon([U(15, 14), U(41, 14), U(43, 34), U(41, 46), U(36, 43), U(32, 48), U(27, 44), U(22, 48), U(18, 43), U(13, 45), U(13, 32)], fill=HAIR)
    for sx, sy0, sy1 in ((20, 12, 42), (25, 10, 44), (31, 11, 45), (36, 13, 41)):
        o.line((U(sx, sy0), U(sx + 1, sy1)), fill=HAIR2)
    o.polygon([U(38, 14), U(41, 14), U(43, 34), U(41, 46), U(38, 42)], fill=HAIR3)
    o.line((U(19, 5), U(26, 3)), fill=HAIRL)
    o.line((U(17, 9), U(19, 6)), fill=HAIRL)
    o.point([U(22, 7), U(28, 5)], fill=HAIRL)
    # pink scrunchie
    o.rectangle(ub((24, 24, 32, 27)), fill=PINK)
    o.point([U(26, 25), U(29, 26)], fill=(255, 150, 230))

room.convert('RGB').resize((W * S, H * S), Image.NEAREST).save('img/room.png', optimize=True)

# ------------------------------------------------------------------ sprites: crowned roomba, favicon
roo = Image.new('RGBA', (16, 17), (0, 0, 0, 0))
rd = ImageDraw.Draw(roo)
rows = ['    ......    ', '  ..aaaaaa..  ', ' .aaaccccaaa. ', '.aaccddddccaa.', '.accddffddcca.',
        '.accddddddcca.', '.aaccccccccaa.', ' .eeaaaaaaee. ', '  ..eeeeee..  ', '    ......    ']
pal = {'.': INK, 'a': (120, 120, 140, 255), 'c': (190, 190, 210, 255), 'd': (60, 60, 75, 255),
       'e': (70, 70, 90, 255), 'f': (60, 255, 120, 255)}
for y, r in enumerate(rows):
    for x, c in enumerate(r):
        if c in pal:
            roo.putpixel((x + 1, y + 7), pal[c])
crown = ['k.k.k.k', 'kgkgkgk', 'kgggggk', 'kgrgrgk', 'kgggggk', 'kkkkkkk']
cp = {'k': INK, 'g': (255, 225, 74, 255), 'r': (255, 60, 70, 255)}
for y, r in enumerate(crown):
    for x, c in enumerate(r):
        if c in cp:
            roo.putpixel((x + 5, y + 1), cp[c])
roo.resize((16 * 8, 17 * 8), Image.NEAREST).save('img/roomba.png', optimize=True)
fav = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
fav.alpha_composite(roo.crop((0, 1, 16, 17)))
fav.resize((64, 64), Image.NEAREST).save('img/favicon.png', optimize=True)
print('ok')
