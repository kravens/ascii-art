#!/usr/bin/env python
# -*- coding: utf-8 -*- #############  C O I N J O I N . N L  #############
#  An animated ASCII CoinJoin: many tangled, colour-coded inputs stream    #
#  through the green MIXING ZONE and come out as uniform, unlinkable        #
#  outputs.  Great privacy for cheap mining fees.   https://coinjoin.nl     #
###########################################################################
import sys, os, time, math, random
M = math
os.system("")
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

W, H = 112, 36
X_IN, X_MIX, X_OUT = 20, 55, 90
TOP, BOT = 5, 31
CY = (TOP + BOT) / 2

# ---- palette ----------------------------------------------------------------------
BG     = (10, 12, 16)
BRAND  = (176, 186, 236)      # CoinJoin periwinkle
GREEN  = (46, 214, 122)
GLOW   = (120, 255, 170)
ORANGE = (247, 147, 26)
WHITE  = (236, 239, 246)
GREY   = (110, 120, 134)
DIM    = (46, 40, 34)         # faint sankey ribbon
IN_COLS = [(86,150,240),(232,86,98),(240,158,48),(206,108,196),(74,200,200),(122,138,250),(232,120,150)]
def lerp(a,b,t): return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t)
def clamp8(c): return (max(0,min(255,int(c[0]))),max(0,min(255,int(c[1]))),max(0,min(255,int(c[2]))))
def smooth(u): u=0. if u<0 else 1. if u>1 else u; return u*u*(3-2*u)

# ---- nodes ------------------------------------------------------------------------
IN_Y  = list(range(TOP, BOT+1, 2))                          # 14 input chips
IN_AD = ["bc1qsfun...0n74r","bc1q8huk...n2cfr","bc1qruck...j2n9c",
         "bc1p806c...a04nk","bc1pgev7...2pn7z"]
# outputs: two clean uniform denominations + a little change
OUT = ([(y, GREEN, 3.0) for y in (6,8,10,12)] +           # 6x 200,000 sats
       [(15,GREEN,3.0),(17,GREEN,3.0),(19,ORANGE,2.0),(21,GREEN,3.0)] +  # 6x 131,072 (1 re-linked)
       [(24,(70,200,180),1.0),(26,GREEN,1.0),(28,(70,200,180),1.0),(30,ORANGE,0.8)])  # change
OUT_Y = [o[0] for o in OUT]
OUT_W = [o[2] for o in OUT]

def funnel(t, yi, yo, off):                                # input -> mixing band -> output
    ym = CY + off
    if t < 0.5: return yi + (ym - yi) * smooth(t/0.5)
    return ym + (yo - ym) * smooth((t-0.5)/0.5)

# ---- frame buffers ----------------------------------------------------------------
def blank():
    return [[" "]*W for _ in range(H)], [[BG]*W for _ in range(H)]
def put(ch, col, r, c, s, color):
    for i,k in enumerate(s):
        if 0 <= r < H and 0 <= c+i < W:
            ch[r][c+i] = k; col[r][c+i] = color
def dot(ch, col, r, c, glyph, color):
    r = int(round(r)); c = int(round(c))
    if 0 <= r < H and 0 <= c < W: ch[r][c] = glyph; col[r][c] = color

def main():
    parts = []                                             # [t, speed, yi, yo, off, incol]
    o = sys.stdout.write
    frames = next((int(a) for a in sys.argv[1:] if a.isdigit()), 0)
    o("\x1b[?1049h\x1b[?25l\x1b[2J")
    try:
        f = 0
        while frames == 0 or f < frames:
            ch, col = blank()
            pulse = 0.5 + 0.5*M.sin(f*0.12)

            # -- faint sankey ribbons (static structure) ---------------------------
            for yi in IN_Y:
                for k in range(0, 36):
                    t = k/70.0; x = X_IN + (X_OUT-X_IN)*t
                    dot(ch, col, funnel(t, yi, CY, 0), x, "·", DIM)
            for (yo,_,_) in OUT:
                for k in range(35, 71):
                    t = k/70.0; x = X_IN + (X_OUT-X_IN)*t
                    dot(ch, col, funnel(t, CY, yo, 0), x, "·", DIM)

            # -- spawn + advance the mixed coins -----------------------------------
            for _ in range(5):
                yi = random.choice(IN_Y); ic = IN_COLS[IN_Y.index(yi) % len(IN_COLS)]
                j = random.choices(range(len(OUT)), weights=OUT_W)[0]
                parts.append([0.0, random.uniform(.012,.018), yi, OUT_Y[j], random.uniform(-6,6), ic])
            alive = []
            for p in parts:
                p[0] += p[1]
                if p[0] < 1.02: alive.append(p)
            parts = alive
            for t, sp, yi, yo, off, ic in parts:
                for k in range(4):                          # head + short trail
                    tt = t - k*0.016
                    if tt <= 0 or tt >= 1: continue
                    x = X_IN + (X_OUT-X_IN)*tt
                    y = funnel(tt, yi, yo, off)
                    if tt < 0.44:   c = ic                                   # raw input colour
                    elif tt < 0.5:  c = lerp(ic, GLOW, (tt-0.44)/0.06)       # entering the mix
                    elif tt < 0.57: c = GLOW                                  # mixing
                    else:           c = GREEN                                 # uniform output
                    b = 1.0 - k*0.30
                    dot(ch, col, y, x, "●" if k==0 else "·", clamp8(lerp(BG, c, b)))

            # -- mixing zone bar + vertical label ----------------------------------
            for r in range(TOP, BOT+1):
                cg = clamp8(lerp((22,104,68), GLOW, 0.35+0.4*pulse))
                for cc in (X_MIX-1, X_MIX, X_MIX+1):
                    ch[r][cc] = "█"; col[r][cc] = cg
            for i, k in enumerate("MIXING ZONE"):
                put(ch, col, int(CY)-5+i, X_MIX, k, WHITE)

            # -- input chips + the first few addresses -----------------------------
            for idx, y in enumerate(IN_Y):
                c = IN_COLS[idx % len(IN_COLS)]
                put(ch, col, y, X_IN, "█", c)
                if idx < len(IN_AD):
                    put(ch, col, y, X_IN-2-len(IN_AD[idx]), IN_AD[idx], lerp(c, WHITE, .35))
            # -- output chips (uniform!) -------------------------------------------
            for (y, c, _) in OUT:
                put(ch, col, y, X_OUT, "██", c)
            put(ch, col, 9,  X_OUT+4, "6x 200,000 sats",  GREEN)
            put(ch, col, 17, X_OUT+4, "6x 131,072 sats",  GREEN)
            put(ch, col, 18, X_OUT+4, "1 of 6 re-linked",  ORANGE)
            put(ch, col, 27, X_OUT+4, "change",            GREY)

            # -- header (shield logo + wordmark) / footer ---------------------------
            put(ch, col, 0, 2, "┌──┐", BRAND)
            put(ch, col, 1, 2, "│5╱│", BRAND); put(ch, col, 1, 7, "CoinJoin", lerp(BRAND,WHITE,.3))
            put(ch, col, 2, 2, "└╲─┘", BRAND); put(ch, col, 2, 7, "privacy protocol", GREY)
            put(ch, col, 0, W-13, "coinjoin.nl", BRAND)
            put(ch, col, 1, X_MIX-9, "COINJOIN  STRUCTURE", ORANGE)
            put(ch, col, 3, 2,  "30 INPUTS", GREY)
            put(ch, col, 3, W-12, "26 OUTPUTS", GREY)
            put(ch, col, H-2, 2, "great privacy for cheap mining fees", lerp(BRAND, WHITE, .2))
            put(ch, col, H-2, W-22, "→ join at coinjoin.nl", lerp(GREEN, WHITE, .2))

            # -- emit (RLE on colour; blanks are invisible) ------------------------
            out = ["\x1b[?2026h\x1b[H"]
            for r in range(H):
                last=None; line=[]
                for c in range(W):
                    g = ch[r][c]
                    if g == " ": line.append(" "); continue
                    cc = col[r][c]
                    if cc != last: line.append("\x1b[38;2;%d;%d;%dm"%cc); last=cc
                    line.append(g)
                out.append("".join(line)+"\x1b[0m")
            o("\n".join(out)+"\x1b[?2026l"); sys.stdout.flush()
            time.sleep(0.05); f += 1
    except KeyboardInterrupt:
        pass
    finally:
        o("\x1b[?2026l\x1b[?25h\x1b[?1049l\x1b[0m\n")

if __name__ == "__main__":
    main()
