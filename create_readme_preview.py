#!/usr/bin/env python3
"""
Create a polished GitHub README preview as preview_1080p.mp4 and preview_1080p.gif in 1080p Full HD.
Supports both 16:9 Landscape (1920x1080) and 9:16 Vertical (1080x1920) formats for Reels/Shorts/TikTok.

Features:
- Dual Aspect Ratio: 16:9 Landscape (1920x1080) & 9:16 Vertical (1080x1920)
- Dual Mode: Repository Showcase Mode + Personal Developer Portfolio Mode
- Smart Adaptive Scene Count (4 to 12 scenes)
- Fully dynamic scenes: Terminal logs & Badges change per scene based on topic!
- Modern macOS window styling, dot-grid high-tech background
- Audio Sync & Fade-out support
- No ImageMagick required!

Dependencies:
    pip install pillow moviepy requests
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import Iterable

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
from moviepy import __version__ as MOVIEPY_VERSION

try:
    from moviepy import ImageClip, CompositeVideoClip
except ImportError:
    from moviepy.editor import ImageClip, CompositeVideoClip


BACKGROUND = "#090d16"
PANEL = "#0f172a"
BORDER = "#1e293b"
HEADER_BAR = "#162032"
WHITE = "#f8fafc"
MUTED = "#94a3b8"
TEXT_SUB = "#cbd5e1"
BLUE = "#38bdf8"
CYAN = "#0ea5e9"
ACCENT_GREEN = "#10b981"
ACCENT_PURPLE = "#a855f7"
ACCENT_ORANGE = "#fb923c"
SCENE_SECONDS = 3.5
TRANSITION_SECONDS = 0.5
SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

TAG_MAP = {
    "problem": ("THE CHALLENGE", "#f43f5e", "arrow"),
    "what jarvis does": ("AUTONOMOUS INNOVATION", "#0ea5e9", "check"),
    "what it does": ("SMART AI CAPABILITY", "#0ea5e9", "check"),
    "result": ("PROVEN RESULT", "#10b981", "star"),
    "project": ("INDIE GAME PROJECT", "#fb923c", "arrow"),
    "gameplay": ("GAMEPLAY & SIMULATION", "#0ea5e9", "check"),
    "status": ("STEAM RECOGNITION", "#10b981", "star"),
    "idea": ("CORE VISION", "#fb923c", "arrow"),
    "live apps": ("DEPLOYED SUITE", "#0ea5e9", "check"),
    "access": ("PRODUCTION STATUS", "#10b981", "star"),
    "discipline": ("ATHLETIC DISCIPLINE", "#38bdf8", "arrow"),
    "engineering": ("ENGINEERING RIGOR", "#10b981", "check"),
    "let's connect": ("OPEN COLLABORATION", "#a855f7", "star"),
    "builder": ("THE CREATOR", "#38bdf8", "arrow"),
    "focus": ("TECHNICAL FOCUS", "#0ea5e9", "check"),
    "proof": ("PROVEN TRACK RECORD", "#10b981", "star"),
}


def _font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if mono:
        candidates = [
            "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/System/Library/Fonts/Monaco.ttf",
        ]
    elif bold:
        candidates = [
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/SF-Pro-Text-Bold.otf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/SF-Pro-Text-Regular.otf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        proposal = f"{current} {word}".strip()
        if draw.textbbox((0, 0), proposal, font=font)[2] <= max_width or not current:
            current = proposal
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    font,
    fill: str,
    max_width: int,
    line_gap: int = 14,
    max_lines: int = 4,
) -> int:
    x, y = xy
    lines = _wrap_text(draw, text, font, max_width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .") + "…"
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        box = draw.textbbox((x, y), line, font=font)
        y += (box[3] - box[1]) + line_gap
    return y


def _base_canvas(width: int, height: int, is_vertical: bool = False) -> Image.Image:
    image = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)

    if is_vertical:
        # Vertical glows (top-right & bottom-left)
        draw.ellipse((width - 400, -250, width + 250, 400), fill="#0d2342")
        draw.ellipse((-250, height - 450, 350, height + 250), fill="#0f2038")
        draw.ellipse((width - 300, height // 2 - 200, width + 150, height // 2 + 300), fill="#103663")
        grid_step = 36
    else:
        # Landscape glows
        draw.ellipse((width - 550, -300, width + 200, 320), fill="#0d2342")
        draw.ellipse((width - 400, -200, width + 100, 200), fill="#103663")
        draw.ellipse((-300, height - 350, 300, height + 200), fill="#0f2038")
        grid_step = 40

    grid_color = "#162338"
    for gx in range(grid_step, width, grid_step):
        for gy in range(grid_step, height, grid_step):
            draw.point((gx, gy), fill=grid_color)
            draw.point((gx + 1, gy), fill=grid_color)

    if not is_vertical:
        draw.rounded_rectangle((55, 65, 67, height - 65), radius=5, fill=BLUE)
    return image


def _draw_window_frame(draw: ImageDraw.ImageDraw, frame: tuple[int, int, int, int], tab_name: str = "main.py") -> int:
    x1, y1, x2, y2 = frame
    header_h = 58

    draw.rounded_rectangle(frame, radius=20, fill=PANEL, outline=BORDER, width=2)
    draw.rounded_rectangle((x1, y1, x2, y1 + header_h + 15), radius=20, fill=HEADER_BAR)
    draw.rectangle((x1, y1 + header_h, x2, y1 + header_h + 15), fill=PANEL)
    draw.line((x1, y1 + header_h, x2, y1 + header_h), fill=BORDER, width=2)

    lights = [("#ef4444", 0), ("#f59e0b", 1), ("#10b981", 2)]
    for color, i in lights:
        lx = x1 + 28 + i * 28
        ly = y1 + 22
        draw.ellipse((lx, ly, lx + 15, ly + 15), fill=color)

    tab_font = _font(18, bold=False, mono=True)
    tw = draw.textbbox((0, 0), tab_name, font=tab_font)[2]
    draw.text(((x1 + x2 - tw) // 2, y1 + 18), tab_name, font=tab_font, fill=MUTED)

    return y1 + header_h + 35


def get_dynamic_terminal_and_badges(title: str, body: str, index: int, project_title: str) -> tuple[list[str], list[tuple[str, str]]]:
    text_content = f"{title} {body}".lower()
    clean_proj = re.sub(r"[^a-zA-Z0-9_\-]", "", project_title.split()[0]).lower() or "app"
    clean_slug = re.sub(r"[^a-zA-Z0-9_\-]", "", title.lower().replace(" ", "_"))[:18] or "core"

    # Human-first portfolio lines
    if any(k in text_content for k in ["shipped, not", "oguzemirtopuz", "portfolio", "builder"]):
        terminal_lines = [
            "Builder: 15-year-old software creator & AI architect",
            "Focus: Building real-world AI apps and games from scratch",
            "Proof: 16+ production systems live on the web today"
        ]
        badges = [("Autonomous AI", BLUE), ("Live Products", ACCENT_GREEN), ("Young Builder", ACCENT_PURPLE)]
    elif any(k in text_content for k in ["jarvis", "cognitive"]):
        terminal_lines = [
            "Problem: Chatbots break down and ask you for help when errors happen",
            "What JARVIS Does: Detects failures and fixes its own mistakes automatically",
            "Result: 100% autonomous — finishes the entire job with ZERO human help"
        ]
        badges = [("Self-Healing AI", ACCENT_ORANGE), ("Zero Human Help", ACCENT_GREEN), ("Fully Autonomous", BLUE)]
    elif any(k in text_content for k in ["youtube analyse", "yt-analyse", "virality"]):
        terminal_lines = [
            "Problem: Creators don't know if their video will get views before posting",
            "What It Does: AI watches the video and predicts virality score (94/100)",
            "Result: Suggests instant edits to keep viewers watching until the end"
        ]
        badges = [("Virality Predictor", BLUE), ("Viewer Retention", ACCENT_PURPLE), ("Smart Suggestions", ACCENT_GREEN)]
    elif any(k in text_content for k in ["cropocalypse", "steam"]):
        terminal_lines = [
            "Project: 3D farming game fully created from scratch",
            "Gameplay: Build automated farms that harvest crops while you play",
            "Status: Published on the official Steam Store and playable on PC"
        ]
        badges = [("Live on Steam", ACCENT_ORANGE), ("Playable Game", BLUE), ("Made with Unity", ACCENT_GREEN)]
    elif any(k in text_content for k in ["finish & click", "finish and click", "vocalcleaner", "saas"]):
        terminal_lines = [
            "Idea: Turn frustrating everyday tasks into simple 1-click web tools",
            "Live Apps: Project management for teams + AI voice cleaner for creators",
            "Access: Live on the internet right now, used by real people every day"
        ]
        badges = [("Live on Web", ACCENT_GREEN), ("Simple 1-Click", BLUE), ("Real Users", ACCENT_PURPLE)]
    elif any(k in text_content for k in ["precision in engineering", "contact", "discipline"]):
        terminal_lines = [
            "Discipline: Learned from years of competitive football training",
            "Engineering: Clean, reliable software that simply works every time",
            "Let's Connect: Always open to build ambitious projects together"
        ]
        badges = [("Football & Code", BLUE), ("High Precision", ACCENT_GREEN), ("Open to Collab", ACCENT_PURPLE)]

    # General Repository keywords
    elif any(k in text_content for k in ["memory", "vector", "recall", "chroma", "store", "database"]):
        terminal_lines = [
            f"$ {clean_proj} memory --query \"vector_context\" --top-k 5",
            f"[OK] ChromaDB vector store indexed ({clean_slug})",
            "[INFO] Episodic memory retrieved in 1.8ms • 0 bytes sent offline"
        ]
        badges = [("Vector DB", BLUE), ("Persistent Recall", ACCENT_GREEN), ("Low Latency", ACCENT_PURPLE)]
    elif any(k in text_content for k in ["heal", "reflection", "error", "fault", "crash", "recover"]):
        terminal_lines = [
            f"$ {clean_proj} inspect --target {clean_slug}",
            "[WARN] Exception caught: Plan execution interrupted",
            "[HEALED] Reflection engine synthesized alternative plan in 340ms"
        ]
        badges = [("Auto-Healing", ACCENT_ORANGE), ("Fault Tolerant", ACCENT_GREEN), ("AST Sandbox", BLUE)]
    elif any(k in text_content for k in ["install", "setup", "quickstart", "run", "start", "docker"]):
        terminal_lines = [
            f"$ pip install -r requirements.txt && {clean_proj} start",
            f"[OK] Environment verified • Python 3.11+ detected",
            f"[READY] {clean_proj.upper()} cognitive daemon listening on local port"
        ]
        badges = [("Quick Setup", ACCENT_GREEN), ("Zero Config", BLUE), ("Cross-Platform", ACCENT_PURPLE)]
    elif any(k in text_content for k in ["skill", "dynamic", "synthesis", "tool", "plugin", "agent"]):
        terminal_lines = [
            f"$ {clean_proj} synthesize --skill \"browser_automation\"",
            "[OK] Dynamic skill generated on-the-fly and sandboxed",
            "[ACTIVE] Execution confirmed with zero user intervention"
        ]
        badges = [("Dynamic Skills", ACCENT_PURPLE), ("Agentic Core", BLUE), ("Autonomous", ACCENT_GREEN)]
    elif any(k in text_content for k in ["privacy", "local", "security", "offline", "sandbox", "ast"]):
        terminal_lines = [
            f"$ {clean_proj} security --audit --strict",
            "[OK] AST sandbox enforced • Arbitrary execution blocked",
            "[INFO] 100% Local processing • Zero external telemetry"
        ]
        badges = [("100% Local", ACCENT_GREEN), ("Air-Gapped Ready", BLUE), ("Zero Telemetry", ACCENT_ORANGE)]
    else:
        cycle = index % 3
        if cycle == 0:
            terminal_lines = [
                f"$ {clean_proj} execute --mode=autonomous",
                f"[OK] Task plan completed with 0 errors",
                f"[INFO] Verified module: {clean_slug}"
            ]
            badges = [("High Performance", BLUE), ("Async IO Core", ACCENT_GREEN), ("Production Ready", ACCENT_PURPLE)]
        elif cycle == 1:
            terminal_lines = [
                f"$ {clean_proj} benchmark --threads=4",
                f"[OK] Throughput: 1,450 ops/sec",
                f"[INFO] Resource footprint: 48 MB RAM (ultra-light)"
            ]
            badges = [("Ultra Lightweight", ACCENT_GREEN), ("High Throughput", BLUE), ("Optimized", ACCENT_ORANGE)]
        else:
            terminal_lines = [
                f"$ {clean_proj} test --coverage",
                f"[PASS] 100% tests passed across all cognitive sub-systems",
                f"[INFO] Status: Healthy & Self-Sustaining"
            ]
            badges = [("Fully Tested", ACCENT_PURPLE), ("Modular Design", BLUE), ("Enterprise Grade", ACCENT_GREEN)]

    return terminal_lines, badges


def make_landscape_text_scene(
    title: str, body: str, project_title: str, index: int, total: int,
    header_label: str = "FEATURE SHOWCASE", footer_text: str = ""
) -> Image.Image:
    width, height = 1920, 1080
    image = _base_canvas(width, height, is_vertical=False)
    draw = ImageDraw.Draw(image)

    # Pill label
    label_font = _font(20, True)
    pill_w = draw.textbbox((0, 0), header_label, font=label_font)[2] + 34
    draw.rounded_rectangle((105, 65, 105 + pill_w, 110), radius=22, fill="#1e293b", outline="#334155", width=2)
    draw.text((122, 75), header_label, font=label_font, fill=BLUE)

    title_font = _font(48, True)
    title_lines = _wrap_text(draw, project_title, title_font, width - 280)
    for line in title_lines[:1]:
        draw.text((105, 125), line, font=title_font, fill=WHITE)

    tab_slug = re.sub(r"[^a-zA-Z0-9_\-]", "", title.lower().replace(" ", "_"))[:16] or f"mod_{index}"
    frame = (105, 215, width - 95, height - 105)
    content_y = _draw_window_frame(draw, frame, tab_name=f"{tab_slug}.py")

    draw.text((160, content_y), ">", font=_font(42, True, mono=True), fill=BLUE)
    draw.text((205, content_y), title, font=_font(40, True), fill=WHITE)
    content_y += 65

    content_y = _draw_wrapped(
        draw, body, (205, content_y), _font(25), TEXT_SUB, frame[2] - 280, line_gap=16, max_lines=3
    )
    content_y = max(content_y + 25, 450)

    terminal_lines, badges = get_dynamic_terminal_and_badges(title, body, index, project_title)

    term_x1, term_y1 = 160, content_y + 15
    term_x2, term_y2 = frame[2] - 60, frame[3] - 90
    if term_y2 - term_y1 >= 110:
        draw.rounded_rectangle((term_x1, term_y1, term_x2, term_y2), radius=12, fill="#080c17", outline="#1e293b", width=1)
        card_font = _font(21, bold=False)
        draw.text((term_x1 + 25, term_y1 + 20), f">  {terminal_lines[0]}", font=card_font, fill="#38bdf8")
        draw.text((term_x1 + 25, term_y1 + 56), f"[OK] {terminal_lines[1]}", font=card_font, fill=ACCENT_GREEN)
        if term_y2 - term_y1 >= 135:
            draw.text((term_x1 + 25, term_y1 + 92), f"[i]  {terminal_lines[2]}", font=card_font, fill="#e2e8f0")

    badge_y = frame[3] - 65
    bx = 160
    for b_text, b_color in badges:
        bw = draw.textbbox((0, 0), b_text, font=_font(18, True))[2] + 32
        draw.rounded_rectangle((bx, badge_y, bx + bw, badge_y + 36), radius=18, fill="#162032", outline=b_color, width=2)
        draw.text((bx + 16, badge_y + 6), b_text, font=_font(18, True), fill=WHITE)
        bx += bw + 18

    # Footer
    f_text = footer_text or "OPEN SOURCE  •  LOCAL PRIVACY  •  AUTONOMOUS ARCHITECTURE"
    draw.text((105, height - 68), f_text, font=_font(18, True), fill=MUTED)

    bar_x, bar_y, bar_w = width - 280, height - 60, 150
    draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + 10), radius=5, fill="#1e293b")
    active_w = max(12, int(bar_w * index / max(total, 1)))
    draw.rounded_rectangle((bar_x, bar_y, bar_x + active_w, bar_y + 10), radius=5, fill=BLUE)
    draw.text((width - 110, height - 72), f"{index:02d}/{total:02d}", font=_font(18, True), fill=MUTED)

    return image


# Backward compatibility alias for app.py
make_text_scene = make_landscape_text_scene


def _draw_bullet_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, color: str, style: str = "dot") -> None:
    if style == "arrow":
        draw.polygon([(cx - 7, cy - 9), (cx + 7, cy), (cx - 7, cy + 9)], fill=color)
    elif style == "check":
        draw.line([(cx - 8, cy), (cx - 2, cy + 7), (cx + 9, cy - 7)], fill=color, width=3)
    elif style == "star":
        draw.polygon([(cx, cy - 10), (cx + 8, cy), (cx, cy + 10), (cx - 8, cy)], fill=color)
    else:
        draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=color)


def make_vertical_text_scene(
    title: str, body: str, project_title: str, index: int, total: int,
    header_label: str = "DEVELOPER PORTFOLIO", footer_text: str = ""
) -> Image.Image:
    """Renders a pixel-perfect 9:16 Vertical (1080x1920) mobile-first showcase slide."""
    width, height = 1080, 1920
    image = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)

    # Ambient subtle grid
    for gx in range(40, width, 55):
        for gy in range(40, height, 55):
            draw.point((gx, gy), fill="#141c2c")

    # 1. Top Header Area
    top_y = 85
    pill_font = _font(19, True)
    tag = header_label or "OĞUZ EMİR TOPUZ  •  MASTERPIECE SHOWCASE"
    pill_w = draw.textbbox((0, 0), tag, font=pill_font)[2] + 36
    draw.rounded_rectangle((65, top_y, 65 + pill_w, top_y + 46), radius=23, fill="#131d31", outline="#1e293b", width=2)
    draw.text((83, top_y + 10), tag, font=pill_font, fill=BLUE)

    title_font = _font(56, True)
    draw.text((65, top_y + 68), project_title, font=title_font, fill=WHITE)

    sub_font = _font(25, False)
    draw.text((65, top_y + 144), "Autonomous AI  •  Deployed SaaS  •  Developer Tooling", font=sub_font, fill=MUTED)

    # 2. Window Content layout calculations
    fx1 = 65
    fy1 = top_y + 205
    fx2 = width - 65

    cur_y = fy1 + 82
    head_font = _font(40, True)
    head_lines = _wrap_text(draw, title, head_font, (fx2 - fx1) - 100)
    cur_y += len(head_lines[:2]) * 52 + 12

    desc_font = _font(25, False)
    desc_lines = _wrap_text(draw, body, desc_font, (fx2 - fx1) - 80)
    cur_y += len(desc_lines[:3]) * 38 + 36

    card_h = 235
    card_gap = 24
    cards_bottom = cur_y + 3 * card_h + 2 * card_gap

    badge_box_h = 135
    fy2 = cards_bottom + badge_box_h + 55
    frame = (fx1, fy1, fx2, fy2)

    # Draw Window Frame
    draw.rounded_rectangle(frame, radius=24, fill=PANEL, outline="#1e293b", width=2)
    draw.rounded_rectangle((fx1, fy1, fx2, fy1 + 58), radius=24, fill=HEADER_BAR)
    draw.rectangle((fx1, fy1 + 32, fx2, fy1 + 58), fill=HEADER_BAR)
    draw.line([(fx1, fy1 + 58), (fx2, fy1 + 58)], fill="#1e293b", width=2)

    # Window dots
    draw.ellipse((fx1 + 24, fy1 + 23, fx1 + 38, fy1 + 37), fill="#f43f5e")
    draw.ellipse((fx1 + 46, fy1 + 23, fx1 + 60, fy1 + 37), fill="#eab308")
    draw.ellipse((fx1 + 68, fy1 + 23, fx1 + 82, fy1 + 37), fill="#22c55e")

    # Tab title
    slug = f"showcase_{index:02d}.tsx"
    draw.text((fx1 + 105, fy1 + 19), slug, font=_font(18, True), fill=MUTED)

    # Draw Title & Desc
    draw_y = fy1 + 82
    _draw_bullet_icon(draw, fx1 + 45, draw_y + 24, BLUE, "arrow")
    for hl in head_lines[:2]:
        draw.text((fx1 + 65, draw_y), hl, font=head_font, fill=WHITE)
        draw_y += 52

    draw_y += 12
    for dl in desc_lines[:3]:
        draw.text((fx1 + 45, draw_y), dl, font=desc_font, fill=TEXT_SUB)
        draw_y += 38

    # 3. Dynamic Terminal Lines & Structured Cards
    terminal_lines, badges = get_dynamic_terminal_and_badges(title, body, index, project_title)

    card_x1 = fx1 + 35
    card_x2 = fx2 - 35
    card_w = card_x2 - card_x1

    for c_idx, raw_text in enumerate(terminal_lines[:3]):
        c_y1 = cur_y + c_idx * (card_h + card_gap)
        c_y2 = c_y1 + card_h

        # Parse prefix
        if ":" in raw_text:
            pfx, _, clean_text = raw_text.partition(":")
            pfx = pfx.strip().lower()
            clean_text = clean_text.strip()
        else:
            pfx = ""
            clean_text = raw_text.strip()

        c_label, c_color, c_icon = TAG_MAP.get(pfx, ("CORE HIGHLIGHT", BLUE, "check"))

        # Card container
        draw.rounded_rectangle((card_x1, c_y1, card_x2, c_y2), radius=18, fill="#080c16", outline="#1e293b", width=2)

        # Header tag pill inside card
        tag_f = _font(16, True)
        tw = draw.textbbox((0, 0), c_label, font=tag_f)[2] + 26
        draw.rounded_rectangle((card_x1 + 25, c_y1 + 20, card_x1 + 25 + tw, c_y1 + 48), radius=14, fill="#131d31", outline=c_color, width=2)
        draw.text((card_x1 + 38, c_y1 + 24), c_label, font=tag_f, fill=c_color)

        text_f = _font(28, False)
        wrapped = _wrap_text(draw, clean_text, text_f, card_w - 70)
        ty = c_y1 + 72
        for wline in wrapped[:3]:
            draw.text((card_x1 + 35, ty), wline, font=text_f, fill=WHITE)
            ty += 40

    # 4. Badges Container
    badge_box_y1 = cards_bottom + 25
    badge_box_y2 = badge_box_y1 + badge_box_h
    draw.rounded_rectangle((card_x1, badge_box_y1, card_x2, badge_box_y2), radius=18, fill="#080c16", outline="#1e293b", width=2)

    # Badges header
    tag_b = "SYSTEM ATTRIBUTES & PRODUCTION PROOF"
    draw.text((card_x1 + 25, badge_box_y1 + 18), tag_b, font=_font(15, True), fill=MUTED)

    # Badges row
    bx = card_x1 + 25
    by = badge_box_y1 + 52
    for b_text, b_color in badges:
        bw = draw.textbbox((0, 0), b_text, font=_font(20, True))[2] + 32
        draw.rounded_rectangle((bx, by, bx + bw, by + 48), radius=24, fill="#131d31", outline=b_color, width=2)
        draw.text((bx + 16, by + 12), b_text, font=_font(20, True), fill=WHITE)
        bx += bw + 16

    # 5. Bottom Mobile Footer
    foot_y = height - 80
    foot_text = footer_text or "SHIPPED, NOT SHOWCASED  •  15 Y/O BUILDER"
    draw.text((65, foot_y), foot_text, font=_font(18, True), fill=MUTED)

    bar_x, bar_y, bar_w = width - 260, foot_y + 6, 120
    draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + 8), radius=4, fill="#1e293b")
    active_w = max(16, int(bar_w * index / max(total, 1)))
    draw.rounded_rectangle((bar_x, bar_y, bar_x + active_w, bar_y + 8), radius=4, fill=BLUE)
    draw.text((width - 120, foot_y), f"{index:02d} / {total:02d}", font=_font(18, True), fill=MUTED)

    return image


def get_portfolio_scenes() -> list[tuple[str, str]]:
    """Curated, high-impact portfolio scenes for Oğuz Emir Topuz focusing on the 3 Masterpieces."""
    return [
        ("Shipped, Not Showcased.", "Autonomous AI systems, deployed SaaS platforms, and developer tooling — built from scratch."),
        ("JARVIS — Cognitive AI Operating System", "39-module autonomous cognitive agent with episodic vector memory, reflection self-healing, and dynamic skill synthesis."),
        ("YouTube Analyse Pro — SaaS Edition", "Multi-modal virality platform: OpenCV frame analysis, Librosa audio intelligence, and multi-agent debate synthesis."),
        ("Cropocalypse — Listed on Steam", "3D cell-shaded Unity/C# farming simulator with automated agricultural pipelines, publicly listed on Steam."),
        ("Finish & Click · VocalCleaner · Idea to SaaS", "Enterprise Kanban with Supabase RLS + Dual-engine AI mastering live on Render + Autonomous SaaS prototyping."),
        ("Precision in Engineering. Autonomy in Software.", "Discipline in football. Precision in engineering. Open for high-signal collaboration & ambitious builds.")
    ]


def fetch_github_repos(username: str) -> list[dict]:
    """Fetch public repositories for the given GitHub username."""
    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
    req = urllib.request.Request(url, headers={"User-Agent": "README-Preview-Generator"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        print(f"[!] GitHub API error: {exc}", file=sys.stderr)
        return []


def fetch_github_readme(username: str, repo_name: str) -> str:
    """Download the raw README.md for a given user and repository."""
    for branch in ["main", "master", "develop"]:
        url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{branch}/README.md"
        req = urllib.request.Request(url, headers={"User-Agent": "README-Preview-Generator"})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode("utf-8")
        except Exception:
            continue
    return ""



def parse_readme_content(text: str, max_features: int = 0) -> tuple[str, list[tuple[str, str]]]:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    lines = text.splitlines()

    project_title = ""
    for line in lines:
        match = re.search(r"^\s*#\s+(.+?)\s*#*\s*$", line) or re.search(r"<h1[^>]*>(.+?)</h1>", line, re.I)
        if match:
            project_title = re.sub(r"[`*_]|<[^>]+>", "", match.group(1)).strip()
            project_title = re.sub(r"[^\w\s\.\-]", "", project_title).strip()
            break

    features: list[tuple[str, str]] = []
    
    for line in lines:
        if "|" in line and ("**" in line or "Self-heals" in line or "Vector" in line or "Router" in line):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2 and not any(h in parts[0].lower() for h in ["other", "audience", "feature", "---"]):
                title = re.sub(r"[`*_~]", "", parts[0]).strip()
                body = re.sub(r"[`*_~]", "", parts[1]).strip()
                if len(title) >= 4 and len(body) >= 12:
                    features.append((title[:50], body))

    for line in lines:
        bullet = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+(.+?)\s*$", line)
        if bullet:
            item = bullet.group(1)
            item = re.sub(r"!\[[^\]]*\]\([^)]*\)|\[([^\]]+)\]\([^)]*\)|[`*_~]", "", item).strip()
            if len(item) >= 20 and not item.startswith("http"):
                if ":" in item:
                    t, _, b = item.partition(":")
                    if len(t.strip()) <= 45 and not any(t.strip().lower() == f[0].lower() for f in features):
                        features.append((t.strip(), b.strip() or item))
                        continue
                if not any(item[:30].lower() in f[1].lower() for f in features):
                    features.append((f"Feature {len(features)+1}", item))

    if not features:
        features = [
            ("Self-Healing Core", "Automatic reflection and recovery when runtime errors occur."),
            ("Episodic Vector Memory", "Local vector database that recalls past execution outcomes."),
            ("Local & Privacy First", "Zero external telemetry with offline-first execution guarantees."),
            ("Dynamic Skill Synthesis", "Synthesizes and runs custom sandboxed tools on the fly.")
        ]

    if max_features <= 0:
        total_found = len(features)
        readme_len = len(text)
        if total_found >= 9 or readme_len > 4000:
            target_limit = 8
        elif total_found >= 6 or readme_len > 2000:
            target_limit = 6
        else:
            target_limit = 4
    else:
        target_limit = max_features

    return project_title or "Cognitive AI Architecture", features[:target_limit]


def build_video(scene_images: list[Image.Image], output_mp4: Path, fps: int, audio_path: Path | None = None, is_vertical: bool = False) -> None:
    width, height = (1080, 1920) if is_vertical else (1920, 1080)
    clips = []
    step = SCENE_SECONDS - TRANSITION_SECONDS
    for index, image in enumerate(scene_images):
        clip = ImageClip(np.asarray(image.convert("RGB")))
        clip = clip.with_duration(SCENE_SECONDS) if hasattr(clip, "with_duration") else clip.set_duration(SCENE_SECONDS)
        clip = clip.with_start(index * step) if hasattr(clip, "with_start") else clip.set_start(index * step)
        if index > 0 and TRANSITION_SECONDS > 0:
            try:
                from moviepy import vfx
                clip = clip.with_effects([vfx.CrossFadeIn(TRANSITION_SECONDS)])
            except Exception:
                if hasattr(clip, "crossfadein"):
                    clip = clip.crossfadein(TRANSITION_SECONDS)
        clips.append(clip)

    duration = SCENE_SECONDS + max(0, len(clips) - 1) * step
    composite = CompositeVideoClip(clips, size=(width, height), bg_color=(9, 13, 22))
    composite = composite.with_duration(duration) if hasattr(composite, "with_duration") else composite.set_duration(duration)

    audio_clip = None
    if audio_path and Path(audio_path).is_file():
        try:
            try:
                from moviepy import AudioFileClip, afx
            except ImportError:
                from moviepy.editor import AudioFileClip
                from moviepy.audio import fx as afx
            audio_clip = AudioFileClip(str(audio_path))
            audio_clip = audio_clip.subclipped(0, duration) if hasattr(audio_clip, "subclipped") else audio_clip.subclip(0, duration)
            try:
                audio_clip = audio_clip.with_effects([afx.AudioFadeOut(1.5)])
            except Exception:
                if hasattr(audio_clip, "audio_fadeout"):
                    audio_clip = audio_clip.audio_fadeout(1.5)
            composite = composite.with_audio(audio_clip) if hasattr(composite, "with_audio") else composite.set_audio(audio_clip)
        except Exception as e:
            print(f"[!] Warning: Audio could not be loaded: {e}", file=sys.stderr)

    try:
        composite.write_videofile(
            str(output_mp4), fps=fps, codec="libx264", audio=bool(audio_clip), audio_codec="aac",
            preset="medium", bitrate="5000k", threads=4, logger=None,
        )
    finally:
        composite.close()
        if audio_clip:
            try:
                audio_clip.close()
            except Exception:
                pass
        for clip in clips:
            try:
                clip.close()
            except Exception:
                pass


def make_gif(mp4_path: Path, output_gif: Path, fps: int = 12, max_width: int = 960) -> None:
    # 1. En yüksek kalite: FFmpeg iki aşamalı (palettegen + paletteuse) render
    # Bu yöntem yazı kenarlarındaki titreşimi, bulanıklığı ve greni (dithering) tamamen yok eder.
    if shutil.which("ffmpeg"):
        cmd = [
            "ffmpeg", "-y", "-i", str(mp4_path),
            "-vf", f"fps={fps},scale={max_width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256:reserve_transparent=0:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3",
            str(output_gif)
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and output_gif.exists():
            return

    # 2. Yedek: Pillow tabanlı render (FFmpeg bulunamazsa)
    try:
        from moviepy import VideoFileClip
    except ImportError:
        from moviepy.editor import VideoFileClip

    video = VideoFileClip(str(mp4_path))
    frames: list[Image.Image] = []
    try:
        for frame in video.iter_frames(fps=fps, dtype="uint8"):
            image = Image.fromarray(frame).convert("RGB")
            if image.width > max_width:
                height = round(image.height * max_width / image.width)
                image = image.resize((max_width, height), Image.Resampling.LANCZOS)
            frames.append(image.quantize(colors=256, method=Image.Quantize.MEDIANCUT))
    finally:
        video.close()

    if not frames:
        raise RuntimeError("Could not generate GIF frames.")
    duration_ms = max(1, round(1000 / fps))
    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
        disposal=2,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="1080p Full HD GitHub Showcase & Portfolio Preview Generator.")
    parser.add_argument("--github-user", help="GitHub username")
    parser.add_argument("--repo", help="Target GitHub repository name")
    parser.add_argument("--readme", default="", help="Local path to README markdown")
    parser.add_argument("--title", default="", help="Custom project title")
    parser.add_argument("--portfolio", action="store_true", help="Enable Developer Portfolio Showcase mode")
    parser.add_argument("--vertical", action="store_true", help="Render in 9:16 Vertical format (1080x1920)")
    parser.add_argument("--max-scenes", type=int, default=0, help="Max feature scenes (0=Auto adapt)")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument("--fps", type=int, default=30, help="MP4 FPS (default: 30)")
    parser.add_argument("--gif-fps", type=int, default=10, help="GIF FPS (default: 10)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    is_portfolio = args.portfolio or (args.repo and args.repo.lower() in ["oguzemirtopuz", "portfolio"]) or (args.title and "portfolio" in args.title.lower())
    is_vertical = args.vertical

    if is_portfolio:
        project_title = "Oğuz Emir Topuz"
        header_label = "DEVELOPER PORTFOLIO"
        footer_text = "OĞUZ EMİR TOPUZ  •  AUTONOMOUS AI & SAAS ARCHITECT"
        scenes = get_portfolio_scenes()
        print(f"\n[★] Developer Portfolio Mode Active: {project_title}")
        print(f"[✓] Compiling {len(scenes)} curated portfolio showcase scenes (Orientation: {'9:16 Vertical' if is_vertical else '16:9 Landscape'})...")
    else:
        readme_content = ""
        project_title = args.title.strip()
        header_label = "FEATURE SHOWCASE"
        footer_text = "OPEN SOURCE  •  LOCAL PRIVACY  •  AUTONOMOUS ARCHITECTURE"

        if args.readme and Path(args.readme).exists():
            readme_content = Path(args.readme).read_text(encoding="utf-8", errors="replace")
        elif Path("README.md").exists():
            readme_content = Path("README.md").read_text(encoding="utf-8", errors="replace")

        parsed_title, features = parse_readme_content(readme_content, max_features=args.max_scenes)
        project_title = project_title or parsed_title
        scenes = [("Autonomous Architecture", "A self-directing cognitive OS that plans, executes, and heals itself.")] + features

    scene_images: list[Image.Image] = []
    total = len(scenes)
    for idx, (title, body) in enumerate(scenes, start=1):
        if is_vertical:
            frame = make_vertical_text_scene(
                title, body, project_title, idx, total,
                header_label=header_label, footer_text=footer_text
            )
        else:
            frame = make_landscape_text_scene(
                title, body, project_title, idx, total,
                header_label=header_label, footer_text=footer_text
            )
        scene_images.append(frame)

    prefix = "preview_9x16" if is_vertical else "preview_1080p"
    out_mp4 = output_dir / f"{prefix}.mp4"
    out_gif = output_dir / f"{prefix}.gif"

    default_audio = Path(__file__).parent / "assets" / "ambient_tech.mp3"
    audio_to_use = default_audio if default_audio.is_file() else None

    print(f"\n[*] Rendering Full HD video ({len(scene_images)} scenes, 30 FPS, Bitrate 5000k, Audio: {'Enabled' if audio_to_use else 'Muted'})...")
    build_video(scene_images, out_mp4, fps=args.fps, audio_path=audio_to_use, is_vertical=is_vertical)
    print(f"[✓] MP4 Ready: {out_mp4.resolve()} ({out_mp4.stat().st_size / (1024*1024):.1f} MB)")

    gif_max_w = 640 if is_vertical else 960
    print(f"[*] Rendering optimized GIF ({gif_max_w}px, 256 colors)...")
    make_gif(out_mp4, out_gif, fps=args.gif_fps, max_width=gif_max_w)
    print(f"[✓] GIF Ready: {out_gif.resolve()} ({out_gif.stat().st_size / (1024*1024):.1f} MB)")

    print(f"\n🎉 Done! {'9:16 Vertical' if is_vertical else '16:9 Landscape'} Showcase successfully created.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        raise SystemExit(130)
