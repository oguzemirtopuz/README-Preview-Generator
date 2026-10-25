<div align="center">

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Resolution](https://img.shields.io/badge/Resolution-1080p_Full_HD-00C8FF?style=for-the-badge&logo=youtube&logoColor=white)](https://github.com/oguzemirtopuz/README-Preview-Generator)
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero_ImageMagick-46e3b7?style=for-the-badge&logo=github&logoColor=white)](https://github.com/oguzemirtopuz/README-Preview-Generator)
[![Video Engine](https://img.shields.io/badge/Video_Engine-MoviePy_2.x-FF6F00?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://github.com/Zulko/moviepy)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<h1>⚡ README Preview Generator</h1>
<h3>Transform static GitHub READMEs into 1080p Full HD animated showcase videos & GIFs — in one click.</h3>

<p><em>Not a PowerPoint slide. Not an ImageMagick dependency nightmare. A native Python & Tkinter showcase engine for production developer repositories.</em></p>

</div>

---

## ⚡ Focus

**Developer attention is won in the first 5 seconds.** Static walls of text don't convert GitHub stars, and manual video editing takes hours of keyframing. 

`README-Preview-Generator` is an automated showcase synthesizer that ingests any public GitHub repo (or local README), parses its architecture and comparison tables, and renders 1080p Full HD videos and 256-color animated GIFs with zero external binaries.

> *If a developer can't understand what you built in 15 seconds, you didn't ship it clearly.*

---

## 🚀 System Architecture

### ⚡ [Showcase Engine Core](https://github.com/oguzemirtopuz/README-Preview-Generator)

**Problem:** Standard automation scripts like MoviePy v1 mandate external ImageMagick binary installations on Windows that break PATH configurations, fail on UTF-8 characters, and produce static, uninspired slides.

**Solution:** A zero-binary engine using native Pillow typography with Segoe UI and Consolas fonts, dynamic macOS window frames, dot-grid high-tech ambient glows, and contextual terminal simulations that adapt their commands based on the slide's topic.

**Impact:** A one-click desktop app and headless CLI that autonomously fetches public repositories, determines complexity depth (4 to 12 scenes), and organizes exports into dedicated folders (`previews/<repo_name>/`).

<details>
<summary><b>Architecture Highlights</b></summary>

- **Zero-Binary Text Engine** — 100% native Pillow text rendering; completely bypasses ImageMagick dependencies and PATH headaches on Windows.
- **Contextual Terminal Synthesis** — Automatically detects feature context (Memory, Security, Reflection, Testing, Routing) and writes dynamic bash commands and logs per slide.
- **Smart Complexity Detection** — Automatically scales showcase length from 4 scenes (micro-utilities) to 10+ scenes (enterprise cognitive OS).
- **GitHub API Integration** — Fetches public repo lists and raw Markdown directly from GitHub without needing local clones.
- **Categorized Folder Management** — Automatically organizes MP4s and GIFs into isolated folders per repository.

</details>

---

## 🏆 What Makes It Different

| Legacy Video Automation | README Preview Generator |
|---|---|
| Requires ImageMagick binary install on Windows | **100% Native Pillow typography (Zero external binaries)** |
| Static, flat slide transitions | **macOS terminal window frame + dot-grid high-tech ambient glows** |
| Repetitive, hardcoded text cards | **Contextual terminal logs & badges dynamic per scene** |
| Fixed 3-scene rigid limits | **Adaptive Scene Count (Smart complexity detection 4-12 scenes)** |
| Headless CLI only | **Modern Dark-Themed GUI + One-Click Desktop Launcher** |
| Cluttered root output directory | **Automatic repository categorization (`previews/<Repo_Name>/`)** |

---

## 🚀 Quickstart & Usage

### 1. Installation

```bash
git clone https://github.com/oguzemirtopuz/README-Preview-Generator.git
cd README-Preview-Generator
pip install -r requirements.txt
```

### 2. Launching the GUI

Double-click **`Baslat.bat`** (or run from terminal):

```bash
python app.py
```

1. Enter your GitHub username and click **"Fetch Repos"**.
2. Select your repository from the dropdown.
3. Choose your desired depth (or leave on **Auto**).
4. Click **"🚀 Generate 1080p Full HD Preview"**.

### 3. Headless CLI

```bash
# Fetch and generate directly from GitHub:
python create_readme_preview.py --github-user oguzemirtopuz --repo JARVIS-Cognitive-OS

# Or generate from a local README file:
python create_readme_preview.py --readme path/to/README.md --title "My Project" --max-scenes 6
```

---

## 🛠️ Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-blue?style=for-the-badge)
![MoviePy](https://img.shields.io/badge/MoviePy-2.x-FF6F00?style=for-the-badge&logo=ffmpeg&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-PIL-green?style=for-the-badge)
![GitHub API](https://img.shields.io/badge/GitHub_API-v3-181717?style=for-the-badge&logo=github&logoColor=white)

</div>

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">
  <sub><i>Discipline in football. Precision in engineering. Autonomy in software.</i></sub>
</div>
