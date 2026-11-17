"""Generate light/dark SVG assets for the GitHub profile README.

Run:  python scripts/build_assets.py
All text lives in this file; edit CONTENT below and re-run.
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

SANS = "'Segoe UI','PingFang SC','Microsoft YaHei','Noto Sans SC','Noto Sans CJK SC',Arial,sans-serif"
MONO = "'Cascadia Code','JetBrains Mono','SF Mono',Consolas,'Microsoft YaHei',monospace"

THEMES = {
    "light": dict(card="#f7faf8", border="#d3dfd9", text="#10241f", muted="#5b6f68",
                  accent="#1f7a5c", accent_soft="#e2f1e9", amber="#f3c54a", amber_text="#3a2a00",
                  chip="#ffffff", chip_border="#cddbd4", dot="#dbe6e0", wire="#9fb3ab"),
    "dark": dict(card="#0f1714", border="#24372f", text="#e8f0ec", muted="#8fa59c",
                 accent="#3ecf8e", accent_soft="#123022", amber="#f2c14e", amber_text="#1f1600",
                 chip="#14201c", chip_border="#2b4038", dot="#1b2924", wire="#4a5f57"),
}


def tw(s: str, size: float, mono: bool = False) -> float:
    """Rough text width estimate (CJK = 1em, latin ~0.6em mono / ~0.56em sans)."""
    w = 0.0
    for ch in s:
        if ord(ch) > 0x2E80:
            w += size
        elif ch == " ":
            w += size * (0.6 if mono else 0.3)
        else:
            w += size * (0.6 if mono else 0.56)
    return w


def text(x, y, s, size, fill, weight=400, family=SANS, anchor="start", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'font-family="{family}" text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def chips(x, y, items, t, size=12, h=24, gap=8, max_x=None):
    """Return (svg, end_x, end_y). Wraps to next line when max_x reached."""
    out, cx, cy = [], x, y
    for it in items:
        w = tw(it, size, mono=True) + 20
        if max_x and cx + w > max_x and cx > x:
            cx, cy = x, cy + h + gap
        out.append(f'<rect x="{cx:.1f}" y="{cy}" width="{w:.1f}" height="{h}" rx="6" fill="{t["chip"]}" stroke="{t["chip_border"]}"/>')
        out.append(text(cx + 10, cy + h / 2 + size * 0.36, it, size, t["text"], family=MONO))
        cx += w + gap
    return "".join(out), cx, cy + h


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>{body}</svg>\n')


def frame(w, h, t, accent_bar=False):
    s = (f'<defs><pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse">'
         f'<circle cx="2" cy="2" r="1.1" fill="{t["dot"]}"/></pattern></defs>'
         f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1.5"/>')
    if accent_bar:
        s += f'<rect x="1" y="18" width="5" height="{h-36}" rx="2.5" fill="{t["accent"]}"/>'
    return s


# ---------------------------------------------------------------- banner
def ladder(t, x0=632, x_end=860):
    """TIA Portal style ladder: Network 1 seal-in (%I0.0/%M0.0/%I0.1->%M0.0) + Network 2 (%M0.0->%Q0.0)."""
    a, ln, m = t["accent"], t["text"], t["muted"]

    def rail(y0, y1):
        return f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{ln}" stroke-width="2.4" stroke-linecap="butt"/>'

    def contact(cx, cy, nc=False):
        g = (f'<line x1="{cx-6}" y1="{cy-10}" x2="{cx-6}" y2="{cy+10}" stroke="{ln}" stroke-width="2" stroke-linecap="round"/>'
             f'<line x1="{cx+6}" y1="{cy-10}" x2="{cx+6}" y2="{cy+10}" stroke="{ln}" stroke-width="2" stroke-linecap="round"/>')
        if nc:
            g += f'<line x1="{cx-5}" y1="{cy+8}" x2="{cx+5}" y2="{cy-8}" stroke="{ln}" stroke-width="1.8" stroke-linecap="round"/>'
        return g

    def coil(cx, cy):
        return (f'<path d="M{cx-4},{cy-11} A12,12 0 0,0 {cx-4},{cy+11}" fill="none" stroke="{ln}" stroke-width="2" stroke-linecap="round"/>'
                f'<path d="M{cx+4},{cy-11} A12,12 0 0,1 {cx+4},{cy+11}" fill="none" stroke="{ln}" stroke-width="2" stroke-linecap="round"/>'
                f'<line x1="{cx+11.2}" y1="{cy}" x2="{x_end}" y2="{cy}" stroke="{ln}" stroke-width="2" stroke-linecap="butt"/>'
                f'<line x1="{x_end}" y1="{cy-3}" x2="{x_end}" y2="{cy+3}" stroke="{ln}" stroke-width="2" stroke-linecap="butt"/>')

    def wire(xa, ya, xb, yb):
        return f'<line x1="{xa}" y1="{ya}" x2="{xb}" y2="{yb}" stroke="{ln}" stroke-width="2" stroke-linecap="round"/>'

    def lab(cx, cy, addr, sym):
        return (text(cx, cy - 27, addr, 10.5, a, 700, MONO, anchor="middle")
                + text(cx, cy - 15, sym, 10, m, 400, MONO, anchor="middle"))

    c1, xb, c2, c3 = 678, 714, 750, 836

    # Network 1: %I0.0 || %M0.0 -> %I0.1 (NC) -> %M0.0 coil
    r1, br = 76, 152
    out = [
        rail(36, 174),
        wire(x0, r1, c1 - 6, r1), contact(c1, r1), wire(c1 + 6, r1, c2 - 6, r1),
        wire(x0, br, c1 - 6, br), contact(c1, br), wire(c1 + 6, br, xb, br), wire(xb, br, xb, r1),
        contact(c2, r1, nc=True), wire(c2 + 6, r1, c3 - 11.2, r1), coil(c3, r1),
        lab(c1, r1, "%I0.0", '"I0.0"'), lab(c2, r1, "%I0.1", '"I0.1"'), lab(c3, r1, "%M0.0", '"M0.0"'),
        lab(c1, br, "%M0.0", '"M0.0"'),
    ]

    # Network 2: %M0.0 -> %Q0.0 coil
    r2 = 238
    out += [
        rail(198, 262),
        wire(x0, r2, c1 - 6, r2), contact(c1, r2), wire(c1 + 6, r2, c3 - 11.2, r2), coil(c3, r2),
        lab(c1, r2, "%M0.0", '"M0.0"'), lab(c3, r2, "%Q0.0", '"Q0.0"'),
    ]
    return "".join(out)


def banner(t):
    W, H = 900, 300
    b = [frame(W, H, t), f'<rect x="600" y="16" width="284" height="{H-32}" rx="10" fill="url(#dots)"/>']
    b.append(text(40, 54, "ELECTRICAL ENGINEERING · CLASS OF 2027", 12.5, t["accent"], 600, MONO, extra='letter-spacing="1.5"'))
    b.append(text(38, 112, "YiBiao Li", 50, t["text"], 800))
    b.append(text(38 + tw("YiBiao Li", 50) + 6, 110, "李一标", 26, t["muted"], 500))
    b.append(text(40, 150, "PLC 编程 · 电气控制 · 让 AI 操作真实的工程软件", 20, t["text"], 600))
    b.append(text(40, 180, "洛阳师范学院 · 电气工程及其自动化 · 可配合项目出差", 15, t["muted"]))
    c, _, _ = chips(40, 200, ["TIA Portal V21", "S7-1200/1500", "TwinCAT 3", "CODESYS", "EPLAN P8"], t)
    b.append(c)
    pill = "求职中 · 电气工程师（PLC 方向）· 2027 届"
    pw = tw(pill, 13) + 40
    b.append(f'<rect x="40" y="242" width="{pw:.1f}" height="30" rx="15" fill="{t["accent_soft"]}" stroke="{t["accent"]}" stroke-opacity=".5"/>')
    b.append(f'<circle cx="57" cy="257" r="4.5" fill="{t["accent"]}"><animate attributeName="opacity" values="1;.35;1" dur="2s" repeatCount="indefinite"/></circle>')
    b.append(text(70, 261.5, pill, 13, t["text"], 600))
    b.append(ladder(t))
    return svg(W, H, "".join(b), "YiBiao Li 李一标 — PLC / 电气控制 / 工程软件自动化")


# ---------------------------------------------------------------- buttons
def button(t, label, sub, primary):
    size, h = 15, 44
    w = int(tw(label, size) + (tw(sub, 12, True) + 14 if sub else 0) + 62)
    fill = t["amber"] if primary else t["card"]
    fg = t["amber_text"] if primary else t["text"]
    stroke = t["amber"] if primary else t["border"]
    b = [f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>',
         text(20, 27.5, label, size, fg, 700)]
    if sub:
        b.append(text(20 + tw(label, size) + 12, 27, sub, 12, fg if primary else t["muted"], 400, MONO, extra='opacity=".8"'))
    b.append(text(w - 18, 28, "↗", 15, fg, 700, anchor="end"))
    return svg(w, h, "".join(b), f"{label} {sub}")


# ---------------------------------------------------------------- project card
def project(t, name, status, desc, tags):
    W, H = 900, 142
    b = [frame(W, H, t, accent_bar=True)]
    b.append(text(32, 50, name, 25, t["text"], 800))
    b.append(text(32 + tw(name, 25) + 10, 50, "↗", 20, t["accent"], 700))
    sw = tw(status, 12, True) + 22
    b.append(f'<rect x="{W-28-sw:.1f}" y="28" width="{sw:.1f}" height="24" rx="12" fill="{t["accent_soft"]}"/>')
    b.append(text(W - 28 - sw / 2, 44.5, status, 12, t["accent"], 700, MONO, anchor="middle"))
    b.append(text(32, 85, desc, 16, t["muted"]))
    c, _, _ = chips(32, 102, tags, t, size=12.5)
    b.append(c)
    return svg(W, H, "".join(b), f"{name} — {desc}")


# ---------------------------------------------------------------- skills panel
def skills(t, groups):
    W, H = 900, 176
    b = [frame(W, H, t)]
    col_w = (W - 64) / len(groups)
    for i, (head, items) in enumerate(groups):
        x = 32 + i * col_w
        b.append(text(x, 46, head, 12.5, t["accent"], 700, MONO, extra='letter-spacing="1"'))
        b.append(f'<line x1="{x}" y1="58" x2="{x+col_w-28:.1f}" y2="58" stroke="{t["border"]}"/>')
        c, _, _ = chips(x, 72, items, t, max_x=x + col_w - 20)
        b.append(c)
    return svg(W, H, "".join(b), "工具与平台")


# ---------------------------------------------------------------- content
CONTENT = {
    "banner": lambda t: banner(t),
    "btn-website": lambda t: button(t, "个人网站", "biaobiao.space", True),
    "btn-prs": lambda t: button(t, "全部上游 PR", "", False),
    "card-tia-guard": lambda t: project(
        t, "TIA-Guard", "ALPHA · 开源",
        "让 AI Agent 读取、创建并编译 TIA Portal / TwinCAT 3 工程，按真实诊断继续修复",
        ["TIA Portal V21", "S7-1200/1500", "TwinCAT 3", "Openness", "MCP", "C# / .NET"]),
    "card-servo": lambda t: project(
        t, "Servo Motion Lab", "进行中",
        "伺服运动控制作品集：TwinCAT 3 NC/PTP 单轴仿真、PLCopen 功能块与可复现测试",
        ["TwinCAT 3", "NC / PTP", "PLCopen MC", "ST", "EtherCAT"]),
    "skills": lambda t: skills(t, [
        ("PLC / 电气", ["TIA Portal V21", "PLCSIM Adv", "TwinCAT 3", "CODESYS", "EPLAN P8", "Factory I/O"]),
        ("工业通信", ["PROFINET", "EtherCAT", "Modbus", "ADS", "OPC UA"]),
        ("软件 / 工具", ["C# / .NET", "Python", "Git", "STM32 / Keil", "MATLAB"]),
    ]),
}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, fn in CONTENT.items():
        for theme, t in THEMES.items():
            (OUT / f"{name}-{theme}.svg").write_text(fn(t), encoding="utf-8")
    print("generated", len(CONTENT) * len(THEMES), "files in", OUT)
