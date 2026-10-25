<div align="center">

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Resolution](https://img.shields.io/badge/Resolution-1080p_Full_HD-00C8FF?style=for-the-badge&logo=youtube&logoColor=white)](https://github.com/oguzemirtopuz)
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero_ImageMagick-46e3b7?style=for-the-badge&logo=github&logoColor=white)](https://github.com/oguzemirtopuz)
[![Engine](https://img.shields.io/badge/Video_Engine-MoviePy_2.x-FF6F00?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://github.com/Zulko/moviepy)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<h1>⚡ README Preview Generator</h1>
<h3>Transform static GitHub READMEs into 1080p Full HD animated showcase videos & GIFs — in one click.</h3>

<p><em>Not a PowerPoint slide. Not an ImageMagick dependency nightmare. A native Python & Tkinter showcase engine for modern developer repositories.</em></p>

---

</div>

## 🎯 What Problem Does This Solve?

90% of developers lose visitors within the first 5 seconds of opening a GitHub repository. 

Wall-of-text READMEs don't convert stars, and video editors take hours of manual cutting, keyframing, and subtitle alignment. Harici command-line tools like MoviePy v1 require painful ImageMagick installations on Windows that constantly break PATH configurations.

**README Preview Generator automates repository showcases end-to-end:**
- Fetches any public GitHub repo directly via GitHub API (or parses local Markdown)
- Extracts key architectural highlights, comparison tables, and setup steps
- Synthesizes dynamic, contextual terminal simulations (`$ jarvis test`, `$ memory recall`) and tech badges
- Renders 1080p Full HD 30 FPS MP4 videos and lightweight 256-color animated GIFs
- Organizes all outputs automatically into dedicated folders (`previews/<repo_name>/`)

**Zero manual editing. Zero external binaries. Pure developer-first automation.**

---

## 🔥 What Makes This Different

| Traditional Preview Tools | README Preview Generator |
|---|---|
| Requires ImageMagick binary install on Windows | **100% Native Pillow font rendering (Zero external binaries)** |
| Static, boring slide transitions | **macOS terminal window frame + dot-grid high-tech ambient glows** |
| Hardcoded, repetitive text cards | **Contextual terminal logs & badges dynamic per scene** |
| Fixed 3-scene rigid limits | **Smart Complexity Detection (Adapts 4 to 12 scenes based on README depth)** |
| Terminal-only CLI commands | **Modern Dark-Themed GUI + One-Click Desktop Launcher** |
| Cluttered output directory | **Automatic repository categorization (`previews/<Repo_Name>/`)** |

---

## ⚡ Key Features

* **🌐 GitHub API Integration:** Simply enter your GitHub username (e.g. `oguzemirtopuz`). The tool fetches all public repositories into a dropdown menu and downloads the raw README automatically.
* **📺 1080p Full HD Standard:** Generates crystal-clear 1920×1080 video at 30 FPS (5000k bitrate) for YouTube/Twitter/LinkedIn, and optimized 960px GIFs for GitHub README headers.
* **🧠 Contextual Terminal Simulation:** Every slide adapts its simulated bash commands and tags based on the topic (Memory, Security, Reflection, Testing, Benchmarks).
* **⚙️ Adaptive Scene Depth:** Choose between `Auto` (smart complexity detection) or select `4 Scenes (Quick)`, `6 Scenes (Standard)`, `8-10 Scenes (Deep Dive)`, or `Max Possible`.
* **📁 Auto-Categorized Storage:** Every generation is safely organized inside `previews/<repo_name>/` with direct quick-open buttons for video, GIF, and explorer folder.

---

## 🚀 Quickstart & Usage

### 1. Installation

Clone the repository and install the lightweight requirements:

```bash
git clone https://github.com/oguzemirtopuz/README-Preview-Generator.git
cd README-Preview-Generator
pip install -r requirements.txt
```

### 2. Launching the GUI (Recommended)

Simply double-click **`Baslat.bat`** (or launch from terminal):

```bash
python app.py
```

1. Enter your GitHub username and click **"Fetch Repos"**.
2. Select your repository from the dropdown.
3. Click **"🚀 Generate 1080p Full HD Preview"**.
4. Open the finished video or GIF with one click!

### 3. CLI Automation (Headless / Scripts)

You can also run it completely headless from terminal or CI/CD pipelines:

```bash
# Fetch directly from GitHub by username and repo
python create_readme_preview.py --github-user oguzemirtopuz --repo JARVIS-Cognitive-OS

# Or generate from a local README file
python create_readme_preview.py --readme path/to/README.md --title "My Project" --max-scenes 6
```

---

## 🛠️ Architecture & Tech Stack

```text
README-Preview-Generator/
│
├── app.py                     # Modern Tkinter Dark-Themed GUI
├── create_readme_preview.py   # High-resolution Pillow + MoviePy 2.x core engine
├── Baslat.bat                 # One-click Windows launcher
├── requirements.txt           # Minimal dependencies (pillow, moviepy, requests)
│
└── previews/                  # Auto-categorized output directory
    ├── JARVIS-Cognitive-OS/
    │   ├── preview_1080p.mp4
    │   └── preview_1080p.gif
    └── Autocutter/
        ├── preview_1080p.mp4
        └── preview_1080p.gif
```

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">
  <b>Built from scratch by <a href="https://github.com/oguzemirtopuz">Oğuz Emir Topuz</a></b>
</div>
