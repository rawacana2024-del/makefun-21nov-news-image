#!/usr/bin/env python3
"""make.fun entry - "Sum up 21 November's world news in one image".

A newspaper front page for Saturday 21 November 2026: six stories from
that day, drawn with a hand-built 5x7 bitmap font and a hand-written PNG
encoder, plus a world map panel and an "in brief" box.

PURE PYTHON STANDARD LIBRARY ONLY. No Pillow, no third-party packages,
no system font files, no network. The grader runs "python3 -P -s
main.py" in a fresh container where nothing is installed, so this file
must (and does) work with the stdlib alone.

Deterministic: two runs write byte-identical output.
"""
import math, os, struct, sys, zlib

W, H = 1024, 1024
MG = 32  # page margin
BG = (250, 246, 236)      # paper
FG = (20, 20, 20)         # ink
ACC = (176, 32, 32)       # accent red
MUT = (112, 110, 104)     # muted grey
LIN = (58, 58, 58)        # rule lines
GRD = (202, 198, 188)     # map graticule
SEP = (192, 188, 178)     # cell separators
BOD = (42, 42, 42)        # body text
WHT = (255, 255, 255)


class Sheet:
    """An RGB pixel buffer with a small set of drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def fill(self, x0, y0, x1, y1, c):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w - 1, x1)
        y1 = min(self.h - 1, y1)
        if x1 < x0 or y1 < y0:
            return
        row = bytes(c) * (x1 - x0 + 1)
        for y in range(y0, y1 + 1):
            i = (y * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def hline(self, x0, x1, y, c, t=1):
        for k in range(t):
            self.fill(x0, y + k, x1, y + k, c)

    def vline(self, x, y0, y1, c, t=1):
        for k in range(t):
            self.fill(x + k, y0, x + k, y1, c)

    def seg(self, x0, y0, x1, y1, c, t=1):
        """Bresenham line with a square brush of thickness t."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = t // 2
        while True:
            self.fill(x0 - half, y0 - half, x0 + half, y0 + half, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        """Filled circle, drawn as horizontal scanlines."""
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.fill(cx - dx, cy + dy, cx + dx, cy + dy, c)

    def png(self, path):
        """Write the buffer as an 8-bit RGB PNG."""
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)  # filter type 0: none
            raw += self.buf[y * stride:(y + 1) * stride]
        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        data = b"\x89PNG\r\n\x1a\n"
        data += _chunk(b"IHDR", ihdr)
        data += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        data += _chunk(b"IEND", b"")
        with open(path, "wb") as f:
            f.write(data)


def _chunk(kind, payload):
    out = struct.pack(">I", len(payload)) + kind + payload
    out += struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    return out

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows; each row is a 5-bit value
# (bit 4 is the leftmost pixel), written in hex so one glyph fits on
# a single line. A character cell is 6 px wide (5 + 1 gap), so text
# width is len(text) * 6 * scale. Bold is faked by widening each
# stroke by one pixel.
# ---------------------------------------------------------------------------
FONT = {
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '"': (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "*": (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    ",": (0x00, 0x00, 0x00, 0x00, 0x04, 0x04, 0x08),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ":": (0x00, 0x04, 0x00, 0x00, 0x00, 0x04, 0x00),
    ";": (0x00, 0x04, 0x00, 0x00, 0x04, 0x04, 0x08),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    "@": (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "[": (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    "\\": (0x10, 0x08, 0x08, 0x04, 0x02, 0x02, 0x01),
    "]": (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    "^": (0x04, 0x0A, 0x11, 0x00, 0x00, 0x00, 0x00),
    "_": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
    "`": (0x04, 0x04, 0x02, 0x00, 0x00, 0x00, 0x00),
}

FONT.update({
    "a": (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    "b": (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E),
    "c": (0x00, 0x00, 0x0E, 0x10, 0x10, 0x11, 0x0E),
    "d": (0x01, 0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F),
    "e": (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    "f": (0x06, 0x09, 0x08, 0x1E, 0x08, 0x08, 0x08),
    "g": (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "h": (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x11),
    "i": (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    "j": (0x02, 0x00, 0x06, 0x02, 0x02, 0x02, 0x0C),
    "k": (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12),
    "l": (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "m": (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    "n": (0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x11),
    "o": (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    "p": (0x00, 0x00, 0x1E, 0x11, 0x1E, 0x10, 0x10),
    "q": (0x00, 0x00, 0x0F, 0x11, 0x0F, 0x01, 0x01),
    "r": (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    "s": (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    "t": (0x08, 0x08, 0x1C, 0x08, 0x08, 0x08, 0x06),
    "u": (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
    "v": (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "w": (0x00, 0x00, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "x": (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    "y": (0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "z": (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
    "{": (0x02, 0x04, 0x04, 0x0C, 0x04, 0x04, 0x02),
    "|": (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "}": (0x08, 0x04, 0x04, 0x06, 0x04, 0x04, 0x08),
    "~": (0x00, 0x00, 0x0D, 0x16, 0x00, 0x00, 0x00),
    # Specials used by the page copy (bullet, em/en dash).
    "•": (0x00, 0x00, 0x00, 0x0E, 0x0E, 0x00, 0x00),
    "—": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    "–": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
})


def text_w(text, s):
    """Pixel width of text at scale s (monospace: 6 px per char)."""
    return len(text) * 6 * s


def put_text(sh, x, y, text, s, c, bold=False):
    """Draw one line of text; returns the x just past the last char."""
    cx = x
    for ch in text:
        rows = FONT.get(ch, FONT["?"])
        for r in range(7):
            bits = rows[r]
            for col in range(5):
                if bits >> (4 - col) & 1:
                    x0 = cx + col * s
                    x1 = x0 + s - 1 + (1 if bold else 0)
                    sh.fill(x0, y + r * s, x1, y + (r + 1) * s - 1, c)
        cx += 6 * s
    return cx


def fold(text, s, width):
    """Wrap text to fit a pixel width; returns a list of lines."""
    per = max(1, width // (6 * s))
    out = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            nxt = (cur + " " + w) if cur else w
            if len(nxt) <= per:
                cur = nxt
            else:
                if cur:
                    out.append(cur)
                while len(w) > per:  # one very long word: hard-split
                    out.append(w[:per])
                    w = w[per:]
                cur = w
        if cur:
            out.append(cur)
    return out


def put_block(sh, x, y, text, s, width, c=BOD, lead=None, limit=None,
              bold=False):
    """Draw wrapped text; with limit, truncate the tail with '...'."""
    lh = lead or int(7 * s * 1.25)
    lines = fold(text, s, width)
    if limit is not None and len(lines) > limit:
        lines = lines[:limit]
        cap = width // (6 * s)
        last = lines[-1]
        while len(last) + 3 > cap and " " in last:
            last = last.rsplit(" ", 1)[0]
        while len(last) + 3 > cap and last:
            last = last[:-1]
        lines[-1] = last + "..."
    for ln in lines:
        put_text(sh, x, y, ln, s, c, bold=bold)
        y += lh
    return y

# (number, title, summary, longitude, latitude)
STORIES = [
    (1, "Russian missile hits Poland",
     "Poland says a Russian missile struck its territory during a mass "
     "drone and missile attack on Ukraine. Warsaw asks NATO for backing "
     "as allied jets scramble.", 21.0, 52.2),
    (2, "Peace talks gain ground",
     "US envoys say a Ukraine peace deal is edging closer, with "
     "NATO-style guarantees on the table.", 13.4, 52.5),
    (3, "Gulf strikes continue",
     "US-Iran strikes go on; a Houthi missile is intercepted over "
     "Riyadh and coalition jets strike Sanaa.", 46.7, 24.7),
    (4, "COP31 at crunch time",
     "Climate talks in Antalya reach crunch time with no deal in "
     "sight as nations push carbon removal.", 30.7, 36.9),
    (5, "GTA 6 breaks records",
     "Rockstar's blockbuster tops $2.3 billion in its first day and "
     "drives a record spike in downloads.", -74.0, 40.7),
    (6, "ICJ ruling rejected",
     "Myanmar and China call the Rohingya genocide ruling 'unjust'; "
     "others hail it as a step forward.", 4.3, 52.07),
]

LEAD = STORIES[0]
REST = STORIES[1:]

BRIEFS = ("• Kosovo ex-president Thaci guilty; jailed 17 months.\n"
          "• El Salvador's Bukele seeks a third term.\n"
          "• US clears sale of ~900,000 AI chips to China.")

# Manual nudges so near-identical map locations stay readable.
SHIFTS = {1: (8, 0), 2: (-20, -14), 4: (10, 12), 6: (16, 16)}


def main():
    dest = sys.argv[1] if len(sys.argv) > 1 else None
    if dest is None:
        dest = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"),
                            "entry.png")
    sh = Sheet(W, H, BG)

    # ---- Masthead ----
    head = "THE WORLD"
    hw = text_w(head, 8)
    put_text(sh, (W - hw) // 2, 12, head, 8, FG, bold=True)
    sh.hline(MG, W - MG, 88, FG, t=3)
    sh.hline(MG, W - MG, 93, FG, t=1)
    date_line = ("Saturday, 21 November 2026  •  6 stories  •  "
                 "3 continents")
    dw = text_w(date_line, 2)
    put_text(sh, (W - dw) // 2, 101, date_line, 2, FG, bold=True)
    sh.hline(MG, W - MG, 130, FG, t=1)

    # ---- Lead story ----
    y = 142
    put_text(sh, MG, y, "TOP STORY  •  POLAND", 2, ACC, bold=True)
    y += 26
    y = put_block(sh, MG, y,
                  "Russian missile hits Poland\nin a mass strike on Ukraine",
                  5, W - 2 * MG, lead=44, bold=True)
    y += 8
    y = put_block(sh, MG, y, LEAD[2], 3, W - 2 * MG, lead=26)
    y += 10
    sh.hline(MG, W - MG, y, LIN, t=1)
    y += 10

    # ---- Map panel: numbered dots on a graticule ----
    map_top = y
    map_h = 150
    map_l, map_r = MG, W - MG
    sh.hline(map_l, map_r, map_top, FG, t=1)
    sh.hline(map_l, map_r, map_top + map_h, FG, t=1)
    sh.vline(map_l, map_top, map_top + map_h, FG, t=1)
    sh.vline(map_r, map_top, map_top + map_h, FG, t=1)
    put_text(sh, map_l + 12, map_top + 8, "WHERE IT HAPPENED", 2, FG,
             bold=True)
    gt = map_top + 30
    gb = map_top + map_h - 8
    for lon in range(-150, 181, 30):
        x = map_l + (lon + 180) / 360 * (map_r - map_l)
        sh.seg(int(x), gt, int(x), gb, GRD)
    lat_top, lat_span = 85.0, 145.0
    for lat in (-30, 0, 30, 60):
        yy = gt + (lat_top - lat) / lat_span * (gb - gt)
        sh.seg(map_l, int(yy), map_r, int(yy), GRD)
    for num, _t, _s, lon, lat in STORIES:
        dx, dy = SHIFTS.get(num, (0, 0))
        x = map_l + (lon + 180) / 360 * (map_r - map_l) + dx
        yy = gt + (lat_top - lat) / lat_span * (gb - gt) + dy
        x, yy = int(x), int(yy)
        sh.disc(x, yy, 14, WHT)  # white ring around the red dot
        sh.disc(x, yy, 12, ACC)
        lab = str(num)
        lw = text_w(lab, 2)
        put_text(sh, x - lw // 2, yy - 7, lab, 2, WHT, bold=True)
    y = map_top + map_h + 12
    sh.hline(MG, W - MG, y, LIN, t=1)
    y += 12

    # ---- Story grid: 2 columns x 3 rows (5 stories + in-brief box) ----
    col_w = (W - 2 * MG - 24) // 2
    grid_top_y = y
    grid_bot_y = H - 52
    row_h = (grid_bot_y - grid_top_y) // 3
    for i, (num, title, summ, _lon, _lat) in enumerate(REST):
        col, row = i % 2, i // 2
        x0 = MG + col * (col_w + 24)
        y0 = grid_top_y + row * row_h
        put_text(sh, x0, y0, "%d." % num, 3, ACC, bold=True)
        nw = text_w("%d." % num, 3)
        tx = x0 + nw + 10
        tw = col_w - (tx - x0)
        n_title = len(fold(title, 2, tw))
        # A one-line title leaves room for a three-line summary; a
        # two-line title only for two. Nothing may cross the separator
        # at y0 + row_h - 10.
        max_summ = 3 if n_title <= 1 else 2
        ty = put_block(sh, tx, y0 + 2, title, 2, tw, lead=18, limit=2,
                       bold=True)
        put_block(sh, tx, ty + 2, summ, 2, tw, lead=16, limit=max_summ)
        if row < 2:
            sh.seg(x0, y0 + row_h - 10, x0 + col_w, y0 + row_h - 10, SEP)

    # ---- In-brief box in the last cell ----
    bx = MG + (col_w + 24)
    by = grid_top_y + 2 * row_h
    sh.hline(bx, bx + col_w, by, FG, t=1)
    sh.hline(bx, bx + col_w, by + row_h - 12, FG, t=1)
    sh.vline(bx, by, by + row_h - 12, FG, t=1)
    sh.vline(bx + col_w, by, by + row_h - 12, FG, t=1)
    put_text(sh, bx + 10, by + 8, "IN BRIEF", 2, FG, bold=True)
    put_block(sh, bx + 10, by + 30, BRIEFS, 2, col_w - 20, lead=16)

    # ---- Footer ----
    sh.hline(MG, W - MG, H - 40, FG, t=2)
    foot = ("Sources: RFE/RL • Associated Press • wire reports  —  "
            "21 Nov 2026")
    put_text(sh, MG, H - 30, foot, 1, MUT, bold=True)

    folder = os.path.dirname(os.path.abspath(dest))
    if folder:
        os.makedirs(folder, exist_ok=True)
    sh.png(dest)
    print("saved %s %dx%d" % (dest, W, H))


if __name__ == "__main__":
    main()
