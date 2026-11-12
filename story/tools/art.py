"""Shared cartoon art for the Bridgeville film. Every function returns an SVG string.

Objects are drawn with their origin at the bottom centre (where they touch the ground),
wrapped as  <g transform="translate(x,y) scale(s)"><g id="...">...</g></g>
so GSAP animates the inner group and never fights the placement transform.
"""

INK = "#23202E"
SKY_TOP, SKY_BOT = "#9AD4F0", "#FBE6C2"
MEADOW, HILL, HILL2 = "#9BCB6E", "#7DB46C", "#8CC084"
RW1, RW2 = "#2E5B3B", "#3F7A4C"
BARK = "#8E3B2A"
ROAD, DASH = "#5A5566", "#F6D35B"
RED, GOLD, PAPER = "#D7263D", "#F2B134", "#FFFDF7"
HOUSE_COLS = ["#F2B134", "#E4572E", "#4E8FD1", "#F49AC2", "#7BC67E", "#F6F1E3", "#E4572E", "#4E8FD1", "#F2B134", "#7BC67E"]
ROOFS = ["#6B2E2E", "#3C3A4D", "#6B2E2E", "#3C3A4D", "#6B2E2E", "#3C3A4D", "#3C3A4D", "#6B2E2E", "#3C3A4D", "#6B2E2E"]

S = f'stroke="{INK}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"'
S4 = f'stroke="{INK}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"'


def place(x, y, s, inner_id, body, extra=""):
    gid = f' id="{inner_id}"' if inner_id else ""
    return f'<g transform="translate({x},{y}) scale({s})"{extra}><g{gid}>{body}</g></g>'


def sky(pid, top=SKY_TOP, bot=SKY_BOT):
    return (
        f'<defs><linearGradient id="{pid}-sky" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient></defs>'
        f'<rect x="-2000" y="-2000" width="5920" height="5080" fill="url(#{pid}-sky)"/>'
    )


def shadow(w=120, y=0, op=0.18):
    return f'<ellipse cx="0" cy="{y}" rx="{w}" ry="{w * 0.12:.1f}" fill="{INK}" opacity="{op}"/>'


def redwood(x, y, s, col=RW1, iid=None):
    body = (
        f'<rect x="-10" y="-56" width="20" height="58" fill="{BARK}" {S4}/>'
        f'<polygon points="-54,-44 0,-170 54,-44" fill="{col}" {S4}/>'
        f'<polygon points="-44,-118 0,-236 44,-118" fill="{col}" {S4}/>'
        f'<polygon points="-30,-190 0,-280 30,-190" fill="{col}" {S4}/>'
    )
    return place(x, y, s, iid, body)


def house(x, y, s, col, roof="#6B2E2E", iid=None):
    body = (
        shadow(80, 2)
        + f'<rect x="-62" y="-92" width="124" height="92" fill="{col}" {S}/>'
        f'<polygon points="-80,-88 0,-156 80,-88" fill="{roof}" {S}/>'
        f'<rect x="-14" y="-52" width="30" height="52" fill="#6B4A3A" {S}/>'
        f'<rect x="-50" y="-74" width="26" height="24" fill="#FFF2B0" {S}/>'
        f'<rect x="26" y="-74" width="26" height="24" fill="#FFF2B0" {S}/>'
    )
    return place(x, y, s, iid, body)


def cabin(x, y, s, iid=None):
    logs = "".join(f'<line x1="-56" y1="{-12 * i}" x2="56" y2="{-12 * i}" stroke="{INK}" stroke-width="3" opacity="0.5"/>' for i in range(1, 5))
    body = (
        shadow(70, 2)
        + f'<rect x="-58" y="-62" width="116" height="62" fill="#A0522D" {S}/>'
        + logs
        + f'<polygon points="-72,-58 0,-110 72,-58" fill="#4A3B33" {S}/>'
        f'<rect x="-14" y="-40" width="28" height="40" fill="#5A3A2A" {S}/>'
    )
    return place(x, y, s, iid, body)


def mailbox(x, y, s, zipcode="95526", iid=None):
    body = (
        shadow(60, 2)
        + f'<rect x="-9" y="-120" width="18" height="120" fill="#8E5B3A" {S}/>'
        f'<path d="M-70 -120 V-175 A40 40 0 0 1 -30 -215 H70 A40 40 0 0 1 70 -215 V-120 Z" fill="#4E8FD1" {S}/>'
        f'<path d="M-70 -120 V-175 A40 40 0 0 1 10 -175 V-120 Z" fill="#3E77B5" {S}/>'
        f'<rect x="64" y="-250" width="10" height="70" fill="{RED}" {S4}/><rect x="74" y="-250" width="34" height="24" fill="{RED}" {S4}/>'
        f'<rect x="-40" y="-168" width="104" height="36" rx="6" fill="{PAPER}" {S4}/>'
        f'<text x="12" y="-140" text-anchor="middle" font-family="Archivo Black" font-size="27" fill="{INK}">{zipcode}</text>'
    )
    return place(x, y, s, iid, body)


def town(p, with_mailbox=True, edges=True):
    """The whole town in a 1920x1080 world. Ids: {p}-land, {p}-h0..h9, {p}-c0..c3, {p}-mail, {p}-road."""
    out = [
        f'<path d="M-200 640 Q 400 470 820 600 T 1640 560 T 2120 600 V1300 H-200 Z" fill="{HILL2}" {S4}/>',
    ]
    for i, xx in enumerate(range(-40, 2000, 86)):
        out.append(redwood(xx, 655 + (i % 3) * 8, 0.78 + (i % 4) * 0.08, RW1 if i % 2 else RW2))
    out.append(f'<path id="{p}-land" d="M-200 700 Q 960 630 2120 700 V1300 H-200 Z" fill="{MEADOW}" {S4}/>')
    out.append(
        f'<g id="{p}-road"><path d="M-80 1000 C 480 870, 900 930, 1300 830 S 1800 770 2000 780" fill="none" stroke="{INK}" stroke-width="82"/>'
        f'<path d="M-80 1000 C 480 870, 900 930, 1300 830 S 1800 770 2000 780" fill="none" stroke="{ROAD}" stroke-width="72"/>'
        f'<path d="M-80 1000 C 480 870, 900 930, 1300 830 S 1800 770 2000 780" fill="none" stroke="{DASH}" stroke-width="6" stroke-dasharray="30 30"/></g>'
    )
    cabins = [(170, 735, 0.62), (820, 700, 0.55), (1490, 700, 0.55), (1850, 712, 0.6)]
    for i, (x, y, s) in enumerate(cabins):
        out.append(cabin(x, y, s, f"{p}-c{i}"))
    houses = [(560, 735, 0.62), (1250, 715, 0.58), (1740, 770, 0.7), (1380, 790, 0.78), (930, 812, 0.82),
              (470, 820, 0.85), (260, 870, 0.92), (1560, 862, 0.9), (1120, 885, 0.95), (700, 900, 1.0)]
    for i, (x, y, s) in enumerate(houses):
        out.append(house(x, y, s, HOUSE_COLS[i], ROOFS[i], f"{p}-h{i}"))
    if with_mailbox:
        out.append(mailbox(330, 1010, 1.0, iid=f"{p}-mail"))
    if edges:
        out.append(redwood(30, 1110, 2.3, RW1))
        out.append(redwood(1900, 1110, 2.1, RW2))
    return "".join(out)


def person(p, x, y, s, shirt, cap=None, hair=None, bag=False, skin="#F1C27D", pants="#3B4A6B", bun=False, beard=False):
    """Rig ids: {p} (whole), {p}-armL, {p}-armR, {p}-eyes, {p}-m-happy, {p}-m-sad, {p}-m-open, {p}-bag"""
    hair_svg = ""
    if hair:
        hair_svg = f'<path d="M-52 -268 A52 52 0 0 1 52 -268 Q30 -290 0 -292 Q-30 -290 -52 -268 Z" fill="{hair}" {S}/>'
        if bun:
            hair_svg += f'<circle cx="0" cy="-322" r="20" fill="{hair}" {S}/>'
    cap_svg = ""
    if cap:
        cap_svg = (f'<path d="M-50 -272 A50 50 0 0 1 50 -272 Z" fill="{cap}" {S}/>'
                   f'<path d="M30 -274 H84 Q86 -262 74 -262 H30 Z" fill="{cap}" {S}/>')
    beard_svg = f'<path d="M-40 -250 Q0 -190 40 -250 Q20 -222 0 -222 Q-20 -222 -40 -250 Z" fill="#6B4A3A" {S4}/>' if beard else ""
    bag_svg = ""
    if bag:
        bag_svg = (f'<g id="{p}-bag"><path d="M58 -150 Q85 -190 112 -150" fill="none" {S}/>'
                   f'<rect x="48" y="-152" width="76" height="84" rx="6" fill="#E9C98B" {S}/>'
                   f'<rect x="64" y="-128" width="44" height="26" rx="4" fill="{RED}" {S4}/></g>')
    body = (
        shadow(70, 2)
        + f'<rect x="-30" y="-92" width="24" height="92" rx="8" fill="{pants}" {S}/>'
        f'<rect x="6" y="-92" width="24" height="92" rx="8" fill="{pants}" {S}/>'
        f'<ellipse cx="-20" cy="-2" rx="22" ry="10" fill="{INK}"/><ellipse cx="20" cy="-2" rx="22" ry="10" fill="{INK}"/>'
        f'<g id="{p}-armL"><rect x="-66" y="-204" width="22" height="104" rx="11" fill="{shirt}" {S}/><circle cx="-55" cy="-98" r="12" fill="{skin}" {S4}/></g>'
        f'<g id="{p}-armR"><rect x="44" y="-204" width="22" height="104" rx="11" fill="{shirt}" {S}/><circle cx="55" cy="-98" r="12" fill="{skin}" {S4}/></g>'
        f'<rect x="-48" y="-214" width="96" height="134" rx="34" fill="{shirt}" {S}/>'
        + bag_svg
        + f'<g id="{p}-head"><circle cx="0" cy="-262" r="52" fill="{skin}" {S}/>'
        + hair_svg + cap_svg + beard_svg
        + f'<g id="{p}-eyes"><ellipse cx="-18" cy="-266" rx="6" ry="8" fill="{INK}"/><ellipse cx="18" cy="-266" rx="6" ry="8" fill="{INK}"/></g>'
        f'<path id="{p}-m-happy" d="M-18 -240 Q0 -222 18 -240" fill="none" {S}/>'
        f'<path id="{p}-m-sad" d="M-16 -228 Q0 -244 16 -228" fill="none" {S} opacity="0"/>'
        f'<ellipse id="{p}-m-open" cx="0" cy="-234" rx="14" ry="13" fill="#7A2230" {S4} opacity="0"/></g>'
    )
    return place(x, y, s, p, body)


def buyer(p, x, y, s):
    return person(p, x, y, s, shirt="#2BA39A", cap=RED, bag=True)


def owners(p, x, y, s):
    return person(f"{p}-a", x - 75, y, s, shirt="#E4572E", hair="#6B4A3A", beard=True) + person(
        f"{p}-b", x + 75, y, s * 0.94, shirt="#4E8FD1", hair="#C77D3A", bun=True, skin="#E0A878"
    )


def phone(x, y, w, h, screen="#FFFDF7", iid=None, inner=""):
    body = (
        f'<rect x="{-w / 2 + 6}" y="{-h + 16}" width="{w}" height="{h}" rx="56" fill="{INK}" opacity="0.18"/>'
        f'<rect x="{-w / 2}" y="{-h}" width="{w}" height="{h}" rx="56" fill="{INK}"/>'
        f'<rect x="{-w / 2 + 26}" y="{-h + 26}" width="{w - 52}" height="{h - 52}" rx="34" fill="{screen}"/>'
        + inner
    )
    return place(x, y, 1, iid, body)


def stamp(iid, text, x, y, s=1.0, col=RED, w=420, h=150, rot=-12, small=None):
    sub = ""
    if small:
        sub = f'<text x="0" y="{h / 2 - 18}" text-anchor="middle" font-family="Archivo Black" font-size="30" fill="{col}">{small}</text>'
    body = (
        f'<g transform="rotate({rot})"><rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="18" fill="{PAPER}" fill-opacity="0.35" stroke="{col}" stroke-width="12"/>'
        f'<rect x="{-w / 2 + 14}" y="{-h / 2 + 14}" width="{w - 28}" height="{h - 28}" rx="10" fill="none" stroke="{col}" stroke-width="4"/>'
        f'<text x="0" y="{(28 if not small else 8)}" text-anchor="middle" font-family="Archivo Black" font-size="{h * 0.56 if not small else h * 0.42:.0f}" letter-spacing="6" fill="{col}">{text}</text>{sub}</g>'
    )
    return place(x, y, s, iid, body)


def cursor(iid, x, y, s=1.0, rot=0):
    body = f'<path transform="rotate({rot})" d="M0 0 L0 74 L18 58 L32 90 L46 84 L32 52 L56 52 Z" fill="#FFFFFF" {S}/>'
    return place(x, y, s, iid, body)


def bid_button(iid, x, y, s=1.0, label="BID"):
    body = (
        f'<rect x="-150" y="-50" width="300" height="100" rx="26" fill="{INK}" transform="translate(0,10)"/>'
        f'<g id="{iid}-top"><rect x="-150" y="-50" width="300" height="100" rx="26" fill="{RED}" {S}/>'
        f'<text x="0" y="22" text-anchor="middle" font-family="Archivo Black" font-size="60" fill="#FFFFFF">{label}</text></g>'
    )
    return place(x, y, s, iid, body)


def van(iid, x, y, s, col, label):
    body = (
        shadow(170, 4)
        + f'<rect x="-170" y="-150" width="250" height="120" rx="18" fill="{col}" {S}/>'
        f'<path d="M80 -120 H140 L176 -80 V-30 H80 Z" fill="{col}" {S}/>'
        f'<path d="M92 -110 H136 L160 -82 H92 Z" fill="#BFE6F5" {S4}/>'
        f'<rect x="-170" y="-40" width="346" height="14" fill="{INK}"/>'
        f'<text x="-45" y="-74" text-anchor="middle" font-family="Archivo Black" font-size="40" fill="#FFFFFF">{label}</text>'
        f'<line x1="-60" y1="-150" x2="-60" y2="-190" {S}/><path d="M-110 -200 A50 30 0 0 0 -10 -200 Z" fill="#E8E8EE" {S}/>'
        f'<circle cx="-110" cy="-22" r="28" fill="{INK}"/><circle cx="-110" cy="-22" r="11" fill="#BBB"/>'
        f'<circle cx="120" cy="-22" r="28" fill="{INK}"/><circle cx="120" cy="-22" r="11" fill="#BBB"/>'
    )
    return place(x, y, s, iid, body)


def listing_card(iid, x, y, s, title="ENTIRE TOWN", sub="Bridgeville, CA", price="", photo="", w=520, h=600):
    body = (
        f'<rect x="{-w / 2 + 8}" y="{-h + 16}" width="{w}" height="{h}" rx="28" fill="{INK}" opacity="0.2"/>'
        f'<rect x="{-w / 2}" y="{-h}" width="{w}" height="{h}" rx="28" fill="{PAPER}" {S}/>'
        f'<clipPath id="{iid}-clip"><rect x="{-w / 2 + 24}" y="{-h + 24}" width="{w - 48}" height="{h * 0.52:.0f}" rx="16"/></clipPath>'
        f'<g clip-path="url(#{iid}-clip)"><rect x="{-w / 2 + 24}" y="{-h + 24}" width="{w - 48}" height="{h * 0.52:.0f}" fill="{SKY_TOP}"/>{photo}</g>'
        f'<rect x="{-w / 2 + 24}" y="{-h + 24}" width="{w - 48}" height="{h * 0.52:.0f}" rx="16" fill="none" {S4}/>'
        f'<text x="{-w / 2 + 34}" y="{-h + h * 0.52 + 84:.0f}" font-family="Archivo Black" font-size="{w * 0.085:.0f}" fill="{INK}">{title}</text>'
        f'<text x="{-w / 2 + 34}" y="{-h + h * 0.52 + 132:.0f}" font-family="Inter" font-weight="700" font-size="{w * 0.06:.0f}" fill="#5A5566">{sub}</text>'
        + (f'<text x="{-w / 2 + 34}" y="{-34}" font-family="Archivo Black" font-size="{w * 0.1:.0f}" fill="{INK}">{price}</text>' if price else "")
    )
    return place(x, y, s, iid, body)


def mini_town(p, scale, x, y):
    """The town scaled into a box; its world is 1920x1080 with the horizon around y=640."""
    return f'<g transform="translate({x},{y}) scale({scale})">{town(p, with_mailbox=False, edges=False)}</g>'


def lawnmower(x, y, s):
    body = (
        f'<rect x="-70" y="-60" width="140" height="50" rx="12" fill="{RED}" {S}/>'
        f'<circle cx="-46" cy="-8" r="22" fill="{INK}"/><circle cx="46" cy="-8" r="22" fill="{INK}"/>'
        f'<path d="M50 -60 L120 -150 H150" fill="none" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>'
    )
    return place(x, y, s, None, body)


def baseball_card(x, y, s):
    body = (
        f'<rect x="-60" y="-170" width="120" height="170" rx="10" fill="#F6F1E3" {S}/>'
        f'<rect x="-46" y="-156" width="92" height="104" fill="#9AD4F0" {S4}/>'
        f'<circle cx="0" cy="-120" r="16" fill="#F1C27D" {S4}/><rect x="-18" y="-104" width="36" height="46" rx="10" fill="#4E8FD1" {S4}/>'
        f'<rect x="-46" y="-40" width="92" height="22" fill="{RED}" {S4}/>'
    )
    return place(x, y, s, None, body)


def newspaper(iid, x, y, s, headline, rot=0):
    lines = "".join(f'<rect x="-190" y="{-120 + 26 * i}" width="{150 if i % 2 else 170}" height="10" fill="#C9C3B5"/>' for i in range(5))
    lines += "".join(f'<rect x="20" y="{-120 + 26 * i}" width="170" height="10" fill="#C9C3B5"/>' for i in range(5))
    body = (
        f'<g transform="rotate({rot})"><rect x="-220" y="-300" width="440" height="320" fill="#F3EFE4" {S}/>'
        f'<text x="0" y="-262" text-anchor="middle" font-family="EB Garamond" font-weight="700" font-size="30" fill="{INK}">THE DAILY BUGLE-HORN</text>'
        f'<line x1="-200" y1="-250" x2="200" y2="-250" {S4}/>'
        f'<text x="0" y="-196" text-anchor="middle" font-family="Archivo Black" font-size="{min(44, int(560 / max(len(headline), 1)))}" fill="{INK}">{headline}</text>'
        f'<g transform="translate(0,90)">{lines}</g></g>'
    )
    return place(x, y, s, iid, body)


def calendar(iid, x, y, s, top_text, big_text, col=RED):
    body = (
        f'<rect x="-150" y="-300" width="300" height="300" rx="20" fill="{PAPER}" {S}/>'
        f'<path d="M-150 -280 A20 20 0 0 1 -130 -300 H130 A20 20 0 0 1 150 -280 V-220 H-150 Z" fill="{col}" {S}/>'
        f'<circle cx="-80" cy="-300" r="12" fill="{INK}"/><circle cx="80" cy="-300" r="12" fill="{INK}"/>'
        f'<text x="0" y="-238" text-anchor="middle" font-family="Archivo Black" font-size="{min(42, int(420 / max(len(top_text), 1)))}" fill="#FFFFFF">{top_text}</text>'
        f'<text x="0" y="-70" text-anchor="middle" font-family="Archivo Black" font-size="{110 if len(big_text) < 4 else 92}" fill="{INK}">{big_text}</text>'
    )
    return place(x, y, s, iid, body)


def for_sale_sign(iid, x, y, s, text="FOR SALE"):
    body = (
        shadow(110, 2)
        + f'<rect x="-12" y="-300" width="24" height="300" fill="#8E5B3A" {S}/>'
        f'<rect x="-190" y="-290" width="380" height="16" fill="#8E5B3A" {S4}/>'
        f'<line x1="-150" y1="-274" x2="-150" y2="-250" {S4}/><line x1="150" y1="-274" x2="150" y2="-250" {S4}/>'
        f'<rect x="-180" y="-250" width="360" height="150" rx="12" fill="{PAPER}" {S}/>'
        f'<rect x="-166" y="-236" width="332" height="122" rx="8" fill="none" stroke="{RED}" stroke-width="6"/>'
        f'<text x="0" y="-152" text-anchor="middle" font-family="Archivo Black" font-size="50" fill="{RED}">{text}</text>'
    )
    return place(x, y, s, iid, body)


def bill(iid, x, y, s, rot, amount):
    body = (
        f'<g transform="rotate({rot})"><rect x="-90" y="-120" width="180" height="230" fill="{PAPER}" {S4}/>'
        f'<rect x="-90" y="-120" width="180" height="40" fill="{RED}" {S4}/>'
        f'<text x="0" y="-90" text-anchor="middle" font-family="Archivo Black" font-size="26" fill="#FFFFFF">REPAIR</text>'
        + "".join(f'<rect x="-70" y="{-60 + 22 * i}" width="{120 - 20 * (i % 2)}" height="8" fill="#C9C3B5"/>' for i in range(4))
        + f'<text x="0" y="90" text-anchor="middle" font-family="Archivo Black" font-size="34" fill="{INK}">{amount}</text></g>'
    )
    return place(x, y, s, iid, body)


def poof(iid, x, y, s=1.0):
    puffs = [(-60, -20, 46), (0, -50, 58), (60, -18, 44), (-30, 20, 40), (40, 26, 38), (0, 0, 50)]
    body = "".join(f'<circle class="{iid}-p" cx="{a}" cy="{b}" r="{r}" fill="#EFE6D6" {S4}/>' for a, b, r in puffs)
    return place(x, y, s, iid, body)


def mist(iid, y, op=0.55):
    return (f'<g id="{iid}">'
            + "".join(f'<ellipse cx="{x}" cy="{y + (i % 2) * 24}" rx="{300 + (i % 3) * 60}" ry="46" fill="#FFFFFF" opacity="{op}"/>' for i, x in enumerate(range(-200, 2300, 420)))
            + "</g>")
