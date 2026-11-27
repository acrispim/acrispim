#!/usr/bin/env python3
"""Builds the animated SVGs of the profile README into assets/.

Usage: python3 scripts/build_svgs.py

Palette and fonts follow crispim.dev. Animation is CSS only, inside the SVG,
which GitHub runs when the image is shown in an <img>. Rules for every piece:
  - each element's base style is its FINAL, visible state; the animation starts
    from the hidden state with `animation-fill-mode: both`. Wherever animation
    does not run (prefers-reduced-motion, apps that only rasterise the SVG),
    everything still shows;
  - text whose width matters to the animation gets `textLength`, so it does not
    depend on which monospace font the visitor has installed.
"""
import math
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

COLORS = {
    "BG": "#0a0e14", "P1": "#0f141d", "P2": "#141b27", "BD": "#1d2634", "GATE": "#2a3546",
    "TX": "#c9d3df", "HI": "#e6edf3", "DIM": "#7e8b9c",
    "ACC": "#93a3f5", "CYAN": "#22d3ee", "GREEN": "#3fb950", "AMBER": "#e3b341", "RED": "#f85149",
}
MONO = "'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
SERIF = "'Instrument Serif',Georgia,'Times New Roman',serif"
CW = 0.6  # width of one monospace character, in em

BASE_CSS = """
text{font-family:MONO}.serif{font-family:SERIF;font-style:italic}
.rise{animation:rise .8s ease-out both}
.pulse{animation:pulse 2.4s ease-in-out infinite}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes pulse{50%{opacity:.25}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes travel{to{stroke-dashoffset:-100}}
"""
REDUCED = "@media(prefers-reduced-motion:reduce){*{animation:none!important}}"


def fill(s: str) -> str:
    """Replaces palette names (BG, ACC…) and font names with their values."""
    s = s.replace("MONO", MONO).replace("SERIF", SERIF)
    for k in sorted(COLORS, key=len, reverse=True):
        s = s.replace("$" + k, COLORS[k])
    return s


def svg(w, h, title, desc, css, body, panel=True):
    frame = (f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="$BG" stroke="$BD"/>'
             f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="url(#grid)"/>') if panel else ""
    return fill(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-labelledby="t d"><title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
        '<defs><pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">'
        '<path d="M28 0H0V28" fill="none" stroke="$BD" stroke-opacity=".5"/></pattern></defs>'
        f'<style>{BASE_CSS}{css}{REDUCED}</style>{frame}{body}</svg>\n'
    )


def tw(text, size):
    """Nominal width of a monospace string."""
    return round(len(text) * size * CW, 1)


def header(w, prompt, title):
    return (f'<text x="24" y="31" font-size="11" fill="$DIM">{escape(prompt)}</text>'
            f'<text class="serif" x="{w - 24}" y="33" font-size="21" fill="$TX" text-anchor="end">{escape(title)}</text>')


# ─── hero ────────────────────────────────────────────────────────────────────
def hero():
    W, H = 900, 300
    fs, cw = 17, 17 * CW
    who_x = 28 + 9 * cw
    who_w = 6 * cw

    # pipeline: commits go through the gates; threats stop at a gate and vanish
    x0, x1, ty = 40, 800, 260
    span = x1 - x0
    gates = [(260, "SAST"), (420, "SCA"), (580, "DAST"), (740, "POLICY")]
    period = 8.0
    threats = [(0, 1.0), (2, 5.0), (3, 3.0)]  # (gate index, delay in s)

    css = f"""
.cover{{opacity:0;animation:cover .9s steps(6) .5s both}}
@keyframes cover{{from{{transform:translateX(-{who_w}px);opacity:1}}99%{{opacity:1}}to{{transform:none;opacity:0}}}}
.cursor{{animation:cursor .9s steps(6) .5s both,blink 1s step-end infinite}}
@keyframes cursor{{from{{transform:translateX(-{who_w}px)}}to{{transform:none}}}}
@keyframes blink{{50%{{opacity:0}}}}
.flow{{animation:flow {period}s linear infinite}}
@keyframes flow{{0%{{transform:translateX(0);opacity:0}}5%{{opacity:1}}93%{{opacity:1}}100%{{transform:translateX({span}px);opacity:0}}}}
.track{{stroke-dasharray:.4 1.6;animation:travel 12s linear infinite}}
.sweep{{animation:spin 4s linear infinite;transform-origin:0 0}}
.blip{{animation:blip 4s linear infinite}}
@keyframes blip{{0%{{opacity:1;fill:$RED}}28%{{fill:$RED}}36%{{fill:$GREEN;opacity:1}}70%,100%{{opacity:0;fill:$GREEN}}}}
.ticker{{animation:ticker 40s linear infinite}}
"""
    body = []
    # terminal title bar
    body.append('<circle cx="22" cy="18" r="5" fill="$RED" opacity=".8"/>'
                '<circle cx="40" cy="18" r="5" fill="$AMBER" opacity=".8"/>'
                '<circle cx="58" cy="18" r="5" fill="$GREEN" opacity=".8"/>'
                '<text x="80" y="22" font-size="11" fill="$DIM">~/card — bash</text>'
                '<path d="M1 34.5H899" stroke="$BD"/>'
                '<circle class="pulse" cx="746" cy="18" r="4" fill="$GREEN"/>'
                '<text x="758" y="22" font-size="11" fill="$TX">accepting projects</text>')
    # typed $ whoami
    body.append(f'<text x="28" y="72" font-size="{fs}" fill="$ACC">~/card</text>'
                f'<text x="{28 + 7 * cw}" y="72" font-size="{fs}" fill="$GREEN">$</text>'
                f'<text x="{who_x}" y="72" font-size="{fs}" fill="$HI" textLength="{who_w}" lengthAdjust="spacingAndGlyphs">whoami</text>'
                f'<rect class="cover" x="{who_x + who_w}" y="54" width="{who_w + 14}" height="24" fill="$BG"/>'
                f'<rect class="cursor" x="{who_x + who_w + 3}" y="57" width="9" height="19" fill="$ACC" opacity=".9"/>')
    # identity
    body.append('<text class="serif rise" style="animation-delay:1.4s" x="26" y="130" font-size="50" fill="$HI">Alexandre Crispim</text>'
                '<text class="rise" style="animation-delay:1.7s" x="28" y="162" font-size="15" fill="$ACC">DevSecOps · SRE · Platform Engineering</text>'
                '<text class="rise" style="animation-delay:1.9s" x="28" y="188" font-size="12" fill="$DIM">Curitiba · BR · global remote</text>')
    # SOC radar
    blips = [(70, 40), (215, 52), (320, 28)]
    radar = ['<g transform="translate(770 112)">',
             '<circle r="66" fill="$P1" stroke="$BD"/><circle r="44" fill="none" stroke="$BD"/>'
             '<circle r="22" fill="none" stroke="$BD"/><path d="M-66 0H66M0-66V66" stroke="$BD"/>',
             '<g class="sweep"><path d="M0 0L66 0A66 66 0 0 0 50.6-42.4Z" fill="$ACC" fill-opacity=".16"/>'
             '<path d="M0 0H66" stroke="$ACC" stroke-opacity=".85"/></g>']
    for ang, r in blips:
        a = math.radians(ang)
        delay = round(ang / 360 * 4 - 4, 2)
        radar.append(f'<circle class="blip" style="animation-delay:{delay}s" cx="{r * math.cos(a):.1f}" cy="{r * math.sin(a):.1f}" r="3.5" fill="$GREEN"/>')
    radar.append('<circle r="2.5" fill="$ACC"/></g>'
                 '<text x="770" y="198" font-size="10" fill="$DIM" text-anchor="middle">$ tail -f /var/log/soc</text>')
    body.append("".join(radar))
    # ticker
    tick = ("deploy → prod ✓ · trivy: 0 critical · slo 99.99% · argocd: synced · falco: 0 alerts · "
            "sbom: signed · kyverno: enforced · gitops drift: none · ")
    tlen = tw(tick, 11)
    css += f"@keyframes ticker{{to{{transform:translateX(-{tlen}px)}}}}\n"
    body.append('<clipPath id="tickclip"><rect x="20" y="206" width="860" height="18"/></clipPath>'
                '<g clip-path="url(#tickclip)"><g class="ticker">'
                + "".join(f'<text x="{20 + i * tlen}" y="219" font-size="11" fill="$DIM" textLength="{tlen - 6.6}" '
                          f'lengthAdjust="spacingAndGlyphs">{escape(tick.strip())}</text>' for i in range(3))
                + '</g></g>')
    # pipeline
    pipe = [f'<text x="{x0}" y="242" font-size="10" fill="$DIM">commit</text>',
            f'<path d="M{x0} {ty}H{x1}" stroke="$BD" stroke-width="2"/>',
            f'<path class="track" d="M{x0} {ty}H{x1}" stroke="$ACC" stroke-opacity=".45" pathLength="100"/>',
            f'<rect x="{x1}" y="{ty - 11}" width="60" height="22" rx="5" fill="$P2" stroke="$GREEN"/>',
            f'<text x="{x1 + 30}" y="{ty + 4}" font-size="10" fill="$GREEN" text-anchor="middle">prod</text>']
    for gx, label in gates:
        pipe.append(f'<text x="{gx}" y="242" font-size="10" fill="$DIM" text-anchor="middle">{label}</text>')
    for i in range(4):
        pipe.append(f'<g class="flow" style="animation-delay:-{i * period / 4:g}s">'
                    f'<circle cx="{x0}" cy="{ty}" r="8" fill="$GREEN" opacity=".22"/>'
                    f'<circle cx="{x0}" cy="{ty}" r="4.5" fill="$GREEN"/></g>')
    # threats move at the same speed as the commits
    for k, (gi, delay) in enumerate(threats):
        gx = gates[gi][0]
        dist = gx - 6 - x0
        hit = round(dist / span * 93 + 1, 1)
        css += (f"@keyframes t{k}{{0%{{transform:translateX(0);opacity:0}}3%{{opacity:1}}"
                f"{hit}%{{transform:translateX({dist}px);opacity:1}}{hit + 5}%,100%{{transform:translateX({dist}px);opacity:0}}}}\n"
                f"@keyframes g{k}{{0%,{hit - .5}%{{fill:$P2;stroke:$GATE}}{hit}%,{hit + 6}%{{fill:$RED;stroke:$RED}}{hit + 7}%,100%{{fill:$P2;stroke:$GATE}}}}\n"
                f"@keyframes x{k}{{0%,{hit - .5}%{{opacity:0}}{hit}%,{hit + 9}%{{opacity:1}}{hit + 12}%,100%{{opacity:0}}}}\n"
                f".t{k}{{opacity:0;animation:t{k} {period}s linear -{delay}s infinite}}"
                f".g{k}{{animation:g{k} {period}s linear -{delay}s infinite}}"
                f".x{k}{{opacity:0;animation:x{k} {period}s linear -{delay}s infinite}}\n")
        pipe.append(f'<circle class="t{k}" cx="{x0}" cy="{ty}" r="4.5" fill="$RED"/>')
        pipe.append(f'<text class="x{k}" x="{gx + 12}" y="{ty + 4}" font-size="11" fill="$RED">✗</text>')
    gate_cls = {gates[gi][0]: f"g{k}" for k, (gi, _) in enumerate(threats)}
    for gx, _ in gates:
        cls = gate_cls.get(gx, "")
        pipe.append(f'<rect class="{cls}" x="{gx - 3}" y="{ty - 12}" width="6" height="24" rx="2" fill="$P2" stroke="$GATE"/>')
    pipe.append(f'<text x="876" y="290" font-size="10" fill="$DIM" text-anchor="end">threats in prod: <tspan fill="$GREEN">0</tspan></text>')
    body.append("".join(pipe))

    return svg(W, H, "$ whoami — Alexandre Crispim",
               "Alexandre Crispim, DevSecOps, SRE and Platform Engineering, based in Curitiba, Brazil, working remotely worldwide. "
               "An animated pipeline carries commits to production and blocks threats at the security gates.",
               css, "".join(body))


# ─── numbers ─────────────────────────────────────────────────────────────────
METRICS = [
    ("6+", "ACC", "years of critical", "infra in production"),
    ("99.99%", "CYAN", "availability —", "air traffic · DECEA"),
    ("10M+", "GREEN", "requests/day", "via API gateway"),
    ("1TB+", "AMBER", "logs processed", "per month"),
    ("−65%", "ACC", "detection time", "(MTTD)"),
    ("−25%", "CYAN", "monthly cloud", "spend"),
]


def metrics():
    W, H = 900, 150
    css = """
.bar{transform-box:fill-box;transform-origin:0 50%;animation:grow 1.1s cubic-bezier(.2,.7,.2,1) both}
@keyframes grow{from{transform:scaleX(0)}}
.scan{animation:scan 7s ease-in-out 2s infinite}
@keyframes scan{60%,100%{transform:translateX(980px)}}
"""
    body = [header(W, "$ kubectl get results", "Numbers, not adjectives"),
            '<linearGradient id="sg"><stop offset="0" stop-color="$ACC" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="$ACC" stop-opacity=".09"/><stop offset="1" stop-color="$ACC" stop-opacity="0"/></linearGradient>']
    for i, (num, col, l1, l2) in enumerate(METRICS):
        x = 24 + i * 142
        d = round(.2 + i * .12, 2)
        body.append(f'<g class="rise" style="animation-delay:{d}s">'
                    f'<rect x="{x}" y="48" width="132" height="84" rx="10" fill="$P1" stroke="$BD"/>'
                    f'<text x="{x + 14}" y="86" font-size="25" font-weight="700" fill="${col}">{escape(num)}</text>'
                    f'<rect class="bar" style="animation-delay:{d + .35:.2f}s" x="{x + 14}" y="95" width="104" height="2" rx="1" fill="${col}" opacity=".8"/>'
                    f'<text x="{x + 14}" y="112" font-size="10" fill="$DIM">{escape(l1)}</text>'
                    f'<text x="{x + 14}" y="125" font-size="10" fill="$DIM">{escape(l2)}</text></g>')
    body.append('<rect class="scan" x="-80" y="48" width="80" height="84" fill="url(#sg)"/>')
    return svg(W, H, "Numbers, not adjectives",
               "6+ years of critical infrastructure in production; 99.99% availability in air traffic control (DECEA); "
               "10M+ requests per day through the API gateway; 1 TB+ of logs processed per month; "
               "65% faster detection (MTTD); 25% lower monthly cloud spend.",
               css, "".join(body))


# ─── career ─────────────────────────────────────────────────────────────────
CAREER = [
    ("2012", "Brazilian Air Force", "soldier"),
    ("2017", "Exati Tecnologia", "full stack"),
    ("2020", "Delivery Center", "SRE · DevOps"),
    ("2022", "DECEA", "SRE · DevOps"),
    ("2023 → now", "Ink&Code", "founder"),
    ("2024 → now", "Arlequim Technologies", "SRE · platform"),
]


def career():
    W, H = 900, 190
    xa, xb, y = 100, 800, 100
    draw = 2.4
    css = f"""
.line{{stroke-dasharray:{xb - xa};animation:draw {draw}s ease-out .3s both}}
@keyframes draw{{from{{stroke-dashoffset:{xb - xa}}}to{{stroke-dashoffset:0}}}}
.node{{transform-box:fill-box;transform-origin:center;animation:pop .5s cubic-bezier(.3,1.6,.5,1) both}}
@keyframes pop{{from{{transform:scale(0)}}}}
.sig{{stroke-dasharray:.5 2;animation:travel 10s linear infinite}}
.sonar{{transform-box:fill-box;transform-origin:center;animation:sonar 2.6s ease-out {draw + .6}s infinite both}}
@keyframes sonar{{0%{{transform:scale(.5);opacity:0}}20%{{opacity:.8}}100%{{transform:scale(2.4);opacity:0}}}}
"""
    body = [header(W, "$ git log --oneline career/", "From soldier to founder"),
            f'<path d="M{xa} {y}H{xb}" stroke="$BD" stroke-width="2"/>',
            f'<path class="line" d="M{xa} {y}H{xb}" stroke="$ACC" stroke-width="2"/>',
            f'<path class="sig" d="M{xa} {y}H{xb}" stroke="$HI" stroke-opacity=".5" pathLength="100"/>']
    step = (xb - xa) / (len(CAREER) - 1)
    for i, (year, org, role) in enumerate(CAREER):
        x = round(xa + i * step, 1)
        d = round(.3 + draw * i / (len(CAREER) - 1), 2)
        last = i == len(CAREER) - 1
        col = "$GREEN" if last else "$ACC"
        if last:
            body.append(f'<circle class="sonar" cx="{x}" cy="{y}" r="9" fill="none" stroke="$GREEN"/>'
                        f'<g class="rise" style="animation-delay:{d}s"><rect x="{x - 20}" y="50" width="40" height="16" rx="8" fill="none" stroke="$GREEN"/>'
                        f'<text x="{x}" y="61.5" font-size="9" fill="$GREEN" text-anchor="middle">HEAD</text></g>')
        body.append(f'<circle class="node" style="animation-delay:{d}s" cx="{x}" cy="{y}" r="6" fill="$BG" stroke="{col}" stroke-width="2"/>'
                    f'<g class="rise" style="animation-delay:{d}s">'
                    f'<text x="{x}" y="84" font-size="11" fill="$AMBER" text-anchor="middle">{escape(year)}</text>'
                    f'<text x="{x}" y="127" font-size="11.5" fill="$TX" text-anchor="middle">{escape(org)}</text>'
                    f'<text x="{x}" y="144" font-size="10" fill="$DIM" text-anchor="middle">{escape(role)}</text></g>')
    body.append(f'<text class="rise" style="animation-delay:{draw + .5}s" x="24" y="174" font-size="10" fill="$DIM">'
                '<tspan fill="$GREEN">+</tspan> in progress: Cyber Defense degree (FIAP) · network &amp; computer forensics (HackerSec)</text>')
    return svg(W, H, "From soldier to founder",
               "Career: Brazilian Air Force (2012, soldier); Exati Tecnologia (2017, full stack); Delivery Center (2020, SRE and DevOps); "
               "DECEA (2022, SRE and DevOps); Ink&Code (since 2023, founder); Arlequim Technologies (since 2024, SRE and platform). "
               "In progress: Cyber Defense degree (FIAP) and network & computer forensics (HackerSec).",
               css, "".join(body))


# ─── stack ───────────────────────────────────────────────────────────────────
STACK = [
    ("platform", ["Kubernetes", "Helm", "ArgoCD", "Terraform", "Ansible", "Nomad", "Consul", "Proxmox", "Traefik", "AWS · GCP"]),
    ("security", ["Trivy", "Falco", "Kyverno", "SAST/DAST", "SBOM", "Wazuh", "Authentik", "Infisical", "Zero Trust"]),
    ("code", ["Python", "Django", "FastAPI", "TypeScript", "React", "Vue.js", "Spring Boot", "Rust", "Three.js"]),
]


def stack():
    W, H = 900, 176
    css = """
.glow{stroke-dasharray:14 86;animation:glow 7s linear infinite both}
@keyframes glow{0%{stroke-dashoffset:0;opacity:0}2%{opacity:1}12%{stroke-dashoffset:-100;opacity:1}14%,100%{stroke-dashoffset:-100;opacity:0}}
"""
    body = [header(W, "$ cat stack.yml", "Tools of the trade")]
    k = 0
    for r, (label, chips) in enumerate(STACK):
        y = 52 + r * 40
        body.append(f'<text class="rise" style="animation-delay:{.1 + r * .15:.2f}s" x="24" y="{y + 16}" font-size="11" fill="$AMBER">{label}:</text>')
        x = 128
        for chip in chips:
            w = tw(chip, 11) + 20
            d = round(.2 + k * .04, 2)
            body.append(f'<g class="rise" style="animation-delay:{d}s">'
                        f'<rect x="{x}" y="{y}" width="{w}" height="24" rx="12" fill="$P1" stroke="$BD"/>'
                        f'<text x="{x + 10}" y="{y + 16}" font-size="11" fill="$TX">{escape(chip)}</text></g>'
                        f'<rect class="glow" style="animation-delay:{1.5 + k * .12:.2f}s" x="{x}" y="{y}" width="{w}" height="24" rx="12" '
                        f'fill="none" stroke="$ACC" pathLength="100"/>')
            x += w + 8
            k += 1
        assert x <= W - 16, f"row {label} is wider than the panel: {x}"
    return svg(W, H, "Tools of the trade",
               "Platform: " + ", ".join(STACK[0][1]) + ". Security: " + ", ".join(STACK[1][1])
               + ". Code: " + ", ".join(STACK[2][1]) + ".", css, "".join(body))


# ─── badges ──────────────────────────────────────────────────────────────────
ICONS = {
    "web": '<g class="globe"><circle cx="14" cy="14" r="6.5" fill="none" stroke="$ACC"/>'
           '<ellipse class="meridian" cx="14" cy="14" rx="3" ry="6.5" fill="none" stroke="$ACC"/>'
           '<path d="M7.5 14H20.5" stroke="$ACC"/></g>',
    "mail": '<g class="pulse"><rect x="7.5" y="9.5" width="13" height="9" rx="1.5" fill="none" stroke="$ACC"/>'
            '<path d="M8 10.5L14 15L20 10.5" fill="none" stroke="$ACC"/></g>',
    "code": '<text x="14" y="18" font-size="10" font-weight="700" fill="$ACC" text-anchor="middle">&lt;/&gt;</text>',
}


def badge(icon, label):
    w = round(tw(label, 12) + 48)
    css = """
.meridian{transform-box:fill-box;transform-origin:center;animation:turn 3s ease-in-out infinite}
@keyframes turn{50%{transform:scaleX(.15)}}
.accent{stroke-dasharray:18 82;animation:travel 6s linear infinite}
"""
    body = (f'<rect x=".5" y=".5" width="{w - 1}" height="27" rx="6" fill="$P1" stroke="$BD"/>{ICONS[icon]}'
            f'<path d="M28.5 6V22" stroke="$BD"/>'
            f'<text x="38" y="18.5" font-size="12" fill="$HI">{escape(label)}</text>'
            f'<path class="accent" d="M6 27.5H{w - 6}" stroke="$ACC" pathLength="100"/>')
    return svg(w, 28, label, label, css, body, panel=False)


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        "hero.svg": hero(), "metrics.svg": metrics(), "career.svg": career(), "stack.svg": stack(),
        "badge-web.svg": badge("web", "crispim.dev"),
        "badge-mail.svg": badge("mail", "contact@crispim.dev"),
        "badge-inkecode.svg": badge("code", "Ink&Code"),
    }
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"{name:20} {len(content.encode()) / 1024:5.1f} KB")


if __name__ == "__main__":
    main()
