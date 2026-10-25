#!/usr/bin/env python3
"""
Create a polished GitHub README preview as preview_1080p.mp4 and preview_1080p.gif in 1080p Full HD.
Features:
- 1080p Full HD (1920x1080) crystal-clear output
- Fully in English (Global GitHub standard)
- Smart Adaptive Scene Count: Automatically adapts to project complexity (4 to 12 scenes)
- Fully dynamic scenes: Terminal logs & Badges change per scene based on topic!
- Modern macOS window styling, dot-grid high-tech background
- GitHub Integration: Fetch public repos & READMEs directly via GitHub API
- No ImageMagick required!

Dependencies:
    pip install pillow moviepy requests
"""
from __future__ import annotations

import argparse
import json
import re
import sys
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


WIDTH, HEIGHT = 1920, 1080
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


def _base_canvas() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)

    draw.ellipse((WIDTH - 550, -300, WIDTH + 200, 320), fill="#0d2342")
    draw.ellipse((WIDTH - 400, -200, WIDTH + 100, 200), fill="#103663")
    draw.ellipse((-300, HEIGHT - 350, 300, HEIGHT + 200), fill="#0f2038")

    grid_color = "#162338"
    for gx in range(40, WIDTH, 40):
        for gy in range(40, HEIGHT, 40):
            draw.point((gx, gy), fill=grid_color)
            draw.point((gx + 1, gy), fill=grid_color)

    draw.rounded_rectangle((55, 65, 67, HEIGHT - 65), radius=5, fill=BLUE)
    return image


def _header(draw: ImageDraw.ImageDraw, title: str, label: str = "FEATURE SHOWCASE") -> None:
    label_font = _font(20, True)
    pill_w = draw.textbbox((0, 0), label, font=label_font)[2] + 34
    draw.rounded_rectangle((105, 65, 105 + pill_w, 110), radius=22, fill="#1e293b", outline="#334155", width=2)
    draw.text((122, 75), label, font=label_font, fill=BLUE)

    title_font = _font(48, True)
    title_lines = _wrap_text(draw, title, title_font, WIDTH - 280)
    title_y = 125
    for line in title_lines[:1]:
        draw.text((105, title_y), line, font=title_font, fill=WHITE)


def _footer(draw: ImageDraw.ImageDraw, index: int, total: int) -> None:
    draw.text((105, HEIGHT - 68), "OPEN SOURCE  •  LOCAL PRIVACY  •  AUTONOMOUS ARCHITECTURE", font=_font(18, True), fill=MUTED)

    bar_x, bar_y, bar_w = WIDTH - 280, HEIGHT - 60, 150
    draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + 10), radius=5, fill="#1e293b")
    active_w = max(12, int(bar_w * index / max(total, 1)))
    draw.rounded_rectangle((bar_x, bar_y, bar_x + active_w, bar_y + 10), radius=5, fill=BLUE)
    draw.text((WIDTH - 110, HEIGHT - 72), f"{index:02d}/{total:02d}", font=_font(18, True), fill=MUTED)


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

    if any(k in text_content for k in ["memory", "vector", "recall", "chroma", "store", "database"]):
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
    elif any(k in text_content for k in ["router", "semantic", "latency", "fast", "cache", "speed"]):
        terminal_lines = [
            f"$ {clean_proj} route --command \"check status\"",
            "[OK] Semantic router matched intent in 0.4ms (Cache Hit)",
            "[INFO] Bypassed heavy LLM call • Immediate dispatch"
        ]
        badges = [("Sub-Millisecond", BLUE), ("Semantic Router", ACCENT_GREEN), ("Zero Cost", ACCENT_PURPLE)]
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


def make_text_scene(title: str, body: str, project_title: str, index: int, total: int) -> Image.Image:
    image = _base_canvas()
    draw = ImageDraw.Draw(image)
    _header(draw, project_title)

    tab_slug = re.sub(r"[^a-zA-Z0-9_\-]", "", title.lower().replace(" ", "_"))[:16] or f"mod_{index}"
    frame = (105, 215, WIDTH - 95, HEIGHT - 105)
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
        mono_f = _font(20, mono=True)
        draw.text((term_x1 + 25, term_y1 + 22), terminal_lines[0], font=mono_f, fill="#38bdf8")
        draw.text((term_x1 + 25, term_y1 + 58), terminal_lines[1], font=mono_f, fill=ACCENT_GREEN if "[OK]" in terminal_lines[1] or "[PASS]" in terminal_lines[1] else ACCENT_ORANGE)
        if term_y2 - term_y1 >= 140:
            draw.text((term_x1 + 25, term_y1 + 94), terminal_lines[2], font=mono_f, fill=MUTED)

    badge_y = frame[3] - 65
    bx = 160
    for b_text, b_color in badges:
        bw = draw.textbbox((0, 0), b_text, font=_font(18, True))[2] + 32
        draw.rounded_rectangle((bx, badge_y, bx + bw, badge_y + 36), radius=18, fill="#162032", outline=b_color, width=2)
        draw.text((bx + 16, badge_y + 6), b_text, font=_font(18, True), fill=WHITE)
        bx += bw + 18

    _footer(draw, index, total)
    return image


def make_image_scene(
    image_path: Path, project_title: str, index: int, total: int
) -> Image.Image:
    image = _base_canvas()
    draw = ImageDraw.Draw(image)
    _header(draw, project_title, "FEATURED SCREENSHOT")

    frame = (105, 215, WIDTH - 95, HEIGHT - 105)
    inner_top = _draw_window_frame(draw, frame, tab_name=image_path.name)

    inner_x1 = frame[0] + 25
    inner_y1 = inner_top
    inner_x2 = frame[2] - 25
    inner_y2 = frame[3] - 25
    inner_w = inner_x2 - inner_x1
    inner_h = inner_y2 - inner_y1

    try:
        with Image.open(image_path) as source:
            source = ImageOps.exif_transpose(source).convert("RGB")
            source.thumbnail((inner_w, inner_h), Image.Resampling.LANCZOS)
            px = inner_x1 + (inner_w - source.width) // 2
            py = inner_y1 + (inner_h - source.height) // 2
            image.paste(source, (px, py))
    except (OSError, ValueError) as exc:
        draw.text((inner_x1 + 30, inner_y1 + 50), f"Could not load image: {exc}", font=_font(22), fill=MUTED)

    _footer(draw, index, total)
    return image


def fetch_github_repos(username: str) -> list[dict]:
    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=15"
    req = urllib.request.Request(url, headers={"User-Agent": "Jarvis-Preview-Generator"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        print(f"[!] GitHub API error: {exc}", file=sys.stderr)
        return []


def fetch_github_readme(username: str, repo_name: str) -> str:
    for branch in ["main", "master"]:
        url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{branch}/README.md"
        req = urllib.request.Request(url, headers={"User-Agent": "Jarvis-Preview-Generator"})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode("utf-8")
        except Exception:
            continue
    return ""


def parse_readme_content(text: str, max_features: int = 0) -> tuple[str, list[tuple[str, str]]]:
    """Intelligently extract project title and features with adaptive complexity detection."""
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
    
    # 1. Parse comparison tables
    for line in lines:
        if "|" in line and ("**" in line or "Self-heals" in line or "Vector" in line or "Router" in line):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2 and not any(h in parts[0].lower() for h in ["other", "audience", "feature", "---"]):
                title = re.sub(r"[`*_~]", "", parts[0]).strip()
                body = re.sub(r"[`*_~]", "", parts[1]).strip()
                if len(title) >= 4 and len(body) >= 12:
                    features.append((title[:50], body))

    # 2. Parse bullet points across sections
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

    # Fallback default features
    if not features:
        features = [
            ("Self-Healing Core", "Automatic reflection and recovery when runtime errors occur."),
            ("Episodic Vector Memory", "Local vector database that recalls past execution outcomes."),
            ("Local & Privacy First", "Zero external telemetry with offline-first execution guarantees."),
            ("Dynamic Skill Synthesis", "Synthesizes and runs custom sandboxed tools on the fly.")
        ]

    # Adaptive Complexity Determination:
    # If max_features is 0 (Auto), determine based on README depth:
    if max_features <= 0:
        total_found = len(features)
        readme_len = len(text)
        if total_found >= 9 or readme_len > 4000:
            target_limit = 8  # Deep architecture project
        elif total_found >= 6 or readme_len > 2000:
            target_limit = 6  # Standard project
        else:
            target_limit = 4  # Focused utility / micro-tool
    else:
        target_limit = max_features

    return project_title or "Cognitive AI Architecture", features[:target_limit]


def build_video(scene_images: list[Image.Image], output_mp4: Path, fps: int) -> None:
    clips = []
    step = SCENE_SECONDS - TRANSITION_SECONDS
    for index, image in enumerate(scene_images):
        clip = ImageClip(np.asarray(image.convert("RGB")))
        clip = clip.with_duration(SCENE_SECONDS) if hasattr(clip, "with_duration") else clip.set_duration(SCENE_SECONDS)
        clip = clip.with_start(index * step) if hasattr(clip, "with_start") else clip.set_start(index * step)
        if index > 0:
            try:
                from moviepy import vfx
                clip = clip.with_effects([vfx.CrossFadeIn(TRANSITION_SECONDS)])
            except Exception:
                if hasattr(clip, "crossfadein"):
                    clip = clip.crossfadein(TRANSITION_SECONDS)
        clips.append(clip)

    duration = SCENE_SECONDS + max(0, len(clips) - 1) * step
    composite = CompositeVideoClip(clips, size=(WIDTH, HEIGHT), bg_color=(9, 13, 22))
    composite = composite.with_duration(duration) if hasattr(composite, "with_duration") else composite.set_duration(duration)
    try:
        composite.write_videofile(
            str(output_mp4), fps=fps, codec="libx264", audio=False,
            preset="medium", bitrate="5000k", threads=4, logger=None,
        )
    finally:
        composite.close()
        for clip in clips:
            try:
                clip.close()
            except Exception:
                pass


def make_gif(mp4_path: Path, output_gif: Path, fps: int = 10, max_width: int = 960) -> None:
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
    parser = argparse.ArgumentParser(description="1080p Full HD GitHub README Preview Generator.")
    parser.add_argument("--github-user", help="GitHub username to inspect public repos")
    parser.add_argument("--repo", help="Target GitHub repository name")
    parser.add_argument("--readme", default="", help="Local path to README markdown")
    parser.add_argument("--title", default="", help="Custom project title")
    parser.add_argument("--max-scenes", type=int, default=0, help="Max feature scenes (0=Auto adapt)")
    parser.add_argument("--images", nargs="*", default=[], help="Screenshots list")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument("--fps", type=int, default=30, help="MP4 FPS (default: 30)")
    parser.add_argument("--gif-fps", type=int, default=10, help="GIF FPS (default: 10)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    readme_content = ""
    project_title = args.title.strip()

    if args.github_user:
        print(f"[*] Fetching repos for @{args.github_user}...")
        repos = fetch_github_repos(args.github_user)
        if not repos:
            print(f"[!] No repos found for @{args.github_user}.", file=sys.stderr)
            return 1

        selected_repo = None
        if args.repo:
            for r in repos:
                if r["name"].lower() == args.repo.lower():
                    selected_repo = r
                    break

        if not selected_repo:
            selected_repo = repos[0]

        print(f"[✓] Selected Repo: {selected_repo['name']}")
        project_title = project_title or selected_repo["name"]
        print(f"[*] Downloading README.md...")
        readme_content = fetch_github_readme(args.github_user, selected_repo["name"])

    elif args.readme and Path(args.readme).exists():
        readme_content = Path(args.readme).read_text(encoding="utf-8", errors="replace")
    elif Path("README.md").exists():
        readme_content = Path("README.md").read_text(encoding="utf-8", errors="replace")

    parsed_title, features = parse_readme_content(readme_content, max_features=args.max_scenes)
    final_title = project_title or parsed_title

    print(f"\n[✓] Project: {final_title}")
    print(f"[✓] Extracted {len(features)} Features (Adaptive Setting: {'Auto' if args.max_scenes==0 else args.max_scenes}):")
    for t, b in features:
        print(f"    - {t}: {b[:70]}...")

    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    scene_specs: list[tuple[str, str, Path | None]] = [
        ("Autonomous Architecture", "A self-directing cognitive OS that plans, executes, and heals itself.", None)
    ]
    for title, body in features:
        scene_specs.append((title, body, None))

    for img_path_str in args.images[:3]:
        p = Path(img_path_str)
        if p.is_file():
            scene_specs.append((p.stem.title(), f"UI Screenshot: {p.name}", p))

    total = len(scene_specs)
    scene_images: list[Image.Image] = []
    for index, (title, body, image_path) in enumerate(scene_specs, start=1):
        if image_path:
            frame = make_image_scene(image_path, final_title, index, total)
        else:
            frame = make_text_scene(title, body, final_title, index, total)
        scene_images.append(frame)

    output_mp4 = output_dir / "preview_1080p.mp4"
    output_gif = output_dir / "preview_1080p.gif"

    print(f"\n[*] Rendering 1080p Full HD video ({len(scene_images)} scenes, 30 FPS, 5000k Bitrate)...")
    build_video(scene_images, output_mp4, fps=args.fps)
    print(f"[✓] MP4 Ready: {output_mp4.resolve()} ({output_mp4.stat().st_size / (1024*1024):.1f} MB)")

    print(f"[*] Rendering optimized GIF (960px, 256 colors)...")
    make_gif(output_mp4, output_gif, fps=args.gif_fps, max_width=960)
    print(f"[✓] GIF Ready: {output_gif.resolve()} ({output_gif.stat().st_size / (1024*1024):.1f} MB)")

    print("\n🎉 Done! 1080p Full HD Preview successfully created.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        raise SystemExit(130)
