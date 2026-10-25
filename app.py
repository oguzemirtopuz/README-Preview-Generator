#!/usr/bin/env python3
"""
Modern Dark-Themed GUI for GitHub README Preview Generator (1080p).
Fully in English with Smart Adaptive Scene Count selection and Organized Output Folders.
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import urllib.request
import json
import re
from pathlib import Path

current_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))

import create_readme_preview as preview_engine

# Dark Theme Palette
COLOR_BG = "#0b0f19"
COLOR_CARD = "#111827"
COLOR_INPUT = "#1e293b"
COLOR_BORDER = "#334155"
COLOR_TEXT = "#f8fafc"
COLOR_MUTED = "#94a3b8"
COLOR_BLUE = "#38bdf8"
COLOR_BLUE_HOVER = "#0284c7"
COLOR_GREEN = "#10b981"
COLOR_GREEN_HOVER = "#059669"
COLOR_CONSOLE_BG = "#030712"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("README Preview Generator (1080p Full HD)")
        self.geometry("740x760")
        self.minsize(700, 720)
        self.configure(bg=COLOR_BG)

        self.last_output_dir = None
        self.last_mp4_path = None
        self.last_gif_path = None

        self.setup_styles()
        self.build_ui()

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=COLOR_INPUT, background=COLOR_CARD,
                        foreground=COLOR_TEXT, arrowcolor=COLOR_BLUE)
        style.map("TCombobox", fieldbackground=[("readonly", COLOR_INPUT)],
                  foreground=[("readonly", COLOR_TEXT)])

    def build_ui(self):
        # 1. Header
        header_frame = tk.Frame(self, bg=COLOR_BG)
        header_frame.pack(fill="x", padx=30, pady=(20, 15))

        tk.Label(
            header_frame, text="⚡ README Preview Generator",
            font=("Segoe UI", 20, "bold"), fg=COLOR_TEXT, bg=COLOR_BG
        ).pack(anchor="w")

        tk.Label(
            header_frame, text="Generate organized 1080p Full HD showcase videos and GIFs categorized by repository",
            font=("Segoe UI", 11), fg=COLOR_MUTED, bg=COLOR_BG
        ).pack(anchor="w", pady=(2, 0))

        # 2. Source Selection Card
        source_card = tk.Frame(self, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1)
        source_card.pack(fill="x", padx=30, pady=5)

        card_inner = tk.Frame(source_card, bg=COLOR_CARD)
        card_inner.pack(fill="x", padx=20, pady=15)

        self.source_mode = tk.StringVar(value="github")

        mode_frame = tk.Frame(card_inner, bg=COLOR_CARD)
        mode_frame.pack(fill="x", pady=(0, 10))

        tk.Radiobutton(
            mode_frame, text="🌐 Fetch from GitHub Profile", variable=self.source_mode, value="github",
            font=("Segoe UI", 11, "bold"), fg=COLOR_BLUE, bg=COLOR_CARD, selectcolor=COLOR_INPUT,
            activebackground=COLOR_CARD, activeforeground=COLOR_BLUE, command=self.toggle_mode
        ).pack(side="left", padx=(0, 25))

        tk.Radiobutton(
            mode_frame, text="📁 Choose Local README.md", variable=self.source_mode, value="local",
            font=("Segoe UI", 11, "bold"), fg=COLOR_MUTED, bg=COLOR_CARD, selectcolor=COLOR_INPUT,
            activebackground=COLOR_CARD, activeforeground=COLOR_MUTED, command=self.toggle_mode
        ).pack(side="left")

        # GitHub Section
        self.github_frame = tk.Frame(card_inner, bg=COLOR_CARD)
        self.github_frame.pack(fill="x", pady=5)

        user_row = tk.Frame(self.github_frame, bg=COLOR_CARD)
        user_row.pack(fill="x", pady=(0, 8))

        tk.Label(user_row, text="GitHub Username:", font=("Segoe UI", 10), fg=COLOR_TEXT, bg=COLOR_CARD).pack(side="left")
        self.user_entry = tk.Entry(user_row, font=("Segoe UI", 11), bg=COLOR_INPUT, fg=COLOR_TEXT,
                                   insertbackground=COLOR_TEXT, relief="flat", highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.user_entry.insert(0, "oguzemirtopuz")
        self.user_entry.pack(side="left", fill="x", expand=True, padx=10, ipady=4)

        self.fetch_btn = tk.Button(
            user_row, text="Fetch Repos", font=("Segoe UI", 10, "bold"),
            bg=COLOR_INPUT, fg=COLOR_BLUE, activebackground=COLOR_BORDER, activeforeground=COLOR_BLUE,
            relief="flat", cursor="hand2", command=self.fetch_repos
        )
        self.fetch_btn.pack(side="right", padx=2, ipady=2, ipadx=10)

        repo_row = tk.Frame(self.github_frame, bg=COLOR_CARD)
        repo_row.pack(fill="x")

        tk.Label(repo_row, text="Select Repository:", font=("Segoe UI", 10), fg=COLOR_TEXT, bg=COLOR_CARD).pack(side="left")
        self.repo_combo = ttk.Combobox(repo_row, font=("Segoe UI", 10), state="readonly")
        self.repo_combo.pack(side="left", fill="x", expand=True, padx=(22, 0), ipady=3)

        # Local Section
        self.local_frame = tk.Frame(card_inner, bg=COLOR_CARD)

        local_row = tk.Frame(self.local_frame, bg=COLOR_CARD)
        local_row.pack(fill="x")

        tk.Label(local_row, text="README Path:", font=("Segoe UI", 10), fg=COLOR_TEXT, bg=COLOR_CARD).pack(side="left")
        self.local_entry = tk.Entry(local_row, font=("Segoe UI", 10), bg=COLOR_INPUT, fg=COLOR_TEXT,
                                    insertbackground=COLOR_TEXT, relief="flat", highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.local_entry.pack(side="left", fill="x", expand=True, padx=10, ipady=4)

        self.browse_btn = tk.Button(
            local_row, text="Browse...", font=("Segoe UI", 10),
            bg=COLOR_INPUT, fg=COLOR_TEXT, relief="flat", cursor="hand2", command=self.browse_file
        )
        self.browse_btn.pack(side="right", ipady=2, ipadx=10)

        # 3. Settings Card
        settings_card = tk.Frame(self, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1)
        settings_card.pack(fill="x", padx=30, pady=(5, 5))

        settings_inner = tk.Frame(settings_card, bg=COLOR_CARD)
        settings_inner.pack(fill="x", padx=20, pady=10)

        tk.Label(settings_inner, text="⚙️ Showcase Depth (Scene Count):", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT, bg=COLOR_CARD).pack(side="left")

        self.scenes_combo = ttk.Combobox(
            settings_inner,
            values=[
                "⚡ Auto (Smart Complexity Detection)",
                "4 Scenes - Quick Overview (~14s)",
                "6 Scenes - Standard Showcase (~21s)",
                "8 Scenes - Comprehensive Deep Dive (~28s)",
                "10 Scenes - Full Architecture Tour (~35s)",
                "Max Possible (All Extracted Features)"
            ],
            state="readonly", font=("Segoe UI", 9)
        )
        self.scenes_combo.current(0)
        self.scenes_combo.pack(side="right", fill="x", expand=True, padx=(15, 0), ipady=2)

        # 4. Action Button
        action_frame = tk.Frame(self, bg=COLOR_BG)
        action_frame.pack(fill="x", padx=30, pady=(10, 5))

        self.generate_btn = tk.Button(
            action_frame, text="🚀 Generate 1080p Full HD Preview", font=("Segoe UI", 13, "bold"),
            bg=COLOR_BLUE, fg="#041226", activebackground=COLOR_BLUE_HOVER, activeforeground="#ffffff",
            relief="flat", cursor="hand2", command=self.start_generation
        )
        self.generate_btn.pack(fill="x", ipady=8)

        # 5. Progress / Console Log
        console_card = tk.Frame(self, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1)
        console_card.pack(fill="both", expand=True, padx=30, pady=(5, 10))

        tk.Label(console_card, text="Build Status & Logs:", font=("Segoe UI", 10, "bold"),
                 fg=COLOR_MUTED, bg=COLOR_CARD).pack(anchor="w", padx=15, pady=(8, 2))

        self.console = tk.Text(
            console_card, font=("Consolas", 10), bg=COLOR_CONSOLE_BG, fg="#38bdf8",
            insertbackground="#ffffff", relief="flat", wrap="word", height=7
        )
        self.console.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.log("Ready. Previews will be categorized under 'previews/<repo_name>/' automatically.")

        # 6. Result Open Buttons
        self.result_frame = tk.Frame(self, bg=COLOR_BG)
        self.result_frame.pack(fill="x", padx=30, pady=(0, 20))

        self.open_mp4_btn = tk.Button(
            self.result_frame, text="🎬 Open Video (MP4)", font=("Segoe UI", 11, "bold"),
            bg=COLOR_GREEN, fg="#ffffff", activebackground=COLOR_GREEN_HOVER, relief="flat",
            state="disabled", cursor="hand2", command=self.open_mp4
        )
        self.open_mp4_btn.pack(side="left", fill="x", expand=True, padx=(0, 4), ipady=6)

        self.open_gif_btn = tk.Button(
            self.result_frame, text="🖼️ Open GIF", font=("Segoe UI", 11, "bold"),
            bg=COLOR_CARD, fg=COLOR_BLUE, activebackground=COLOR_INPUT, relief="flat",
            highlightbackground=COLOR_BORDER, highlightthickness=1, state="disabled", cursor="hand2", command=self.open_gif
        )
        self.open_gif_btn.pack(side="left", fill="x", expand=True, padx=4, ipady=6)

        self.open_dir_btn = tk.Button(
            self.result_frame, text="📁 Open Repo Folder", font=("Segoe UI", 11, "bold"),
            bg=COLOR_INPUT, fg=COLOR_TEXT, activebackground=COLOR_BORDER, relief="flat",
            state="disabled", cursor="hand2", command=self.open_folder
        )
        self.open_dir_btn.pack(side="right", fill="x", expand=True, padx=(4, 0), ipady=6)

    def log(self, text: str):
        self.console.insert("end", text + "\n")
        self.console.see("end")

    def toggle_mode(self):
        if self.source_mode.get() == "github":
            self.local_frame.pack_forget()
            self.github_frame.pack(fill="x", pady=5)
        else:
            self.github_frame.pack_forget()
            self.local_frame.pack(fill="x", pady=5)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select README.md",
            filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")]
        )
        if filename:
            self.local_entry.delete(0, "end")
            self.local_entry.insert(0, filename)

    def fetch_repos(self):
        username = self.user_entry.get().strip()
        if not username:
            messagebox.showwarning("Warning", "Please enter a valid GitHub username.")
            return

        self.fetch_btn.config(state="disabled", text="Fetching...")
        self.log(f"[*] Fetching public repositories for @{username}...")

        def _fetch():
            repos = preview_engine.fetch_github_repos(username)
            names = [r["name"] for r in repos]
            self.after(0, lambda: self._on_repos_fetched(names))

        threading.Thread(target=_fetch, daemon=True).start()

    def _on_repos_fetched(self, repo_names):
        self.fetch_btn.config(state="normal", text="Fetch Repos")
        if not repo_names:
            self.log("[!] No repositories found or GitHub rate limit reached.")
            messagebox.showerror("Error", "Could not retrieve repositories.")
            return
        self.repo_combo["values"] = repo_names
        self.repo_combo.current(0)
        self.log(f"[✓] {len(repo_names)} repositories found. Select one from the dropdown.")

    def start_generation(self):
        mode = self.source_mode.get()
        github_user = None
        repo_name = None
        local_readme = None

        if mode == "github":
            github_user = self.user_entry.get().strip()
            repo_name = self.repo_combo.get().strip()
            if not github_user or not repo_name:
                messagebox.showwarning("Missing Info", "Please fetch and select a repository first.")
                return
            category_name = repo_name
        else:
            local_readme = self.local_entry.get().strip()
            if not local_readme or not os.path.exists(local_readme):
                messagebox.showwarning("Missing Info", "Please select a valid README.md file.")
                return
            parent_dir = Path(local_readme).parent.name
            category_name = parent_dir if parent_dir and parent_dir != "." else "Local_Project"

        choice = self.scenes_combo.get()
        max_scenes = 0
        if "4 Scenes" in choice:
            max_scenes = 4
        elif "6 Scenes" in choice:
            max_scenes = 6
        elif "8 Scenes" in choice:
            max_scenes = 8
        elif "10 Scenes" in choice:
            max_scenes = 10
        elif "Max Possible" in choice:
            max_scenes = 20

        # Dedicated categorized folder under previews/<category_name>
        safe_folder_name = re.sub(r"[^\w\-.]", "_", category_name)
        target_dir = current_dir / "previews" / safe_folder_name
        target_dir.mkdir(parents=True, exist_ok=True)
        self.last_output_dir = target_dir

        self.generate_btn.config(state="disabled", text="⏳ Rendering 1080p Preview, Please Wait...")
        self.open_mp4_btn.config(state="disabled")
        self.open_gif_btn.config(state="disabled")
        self.open_dir_btn.config(state="disabled")

        def _worker():
            try:
                readme_text = ""
                title = ""

                if mode == "github":
                    self.log(f"[*] Downloading README.md for '{repo_name}'...")
                    readme_text = preview_engine.fetch_github_readme(github_user, repo_name)
                    title = repo_name
                else:
                    self.log(f"[*] Reading local README: {local_readme}")
                    readme_text = Path(local_readme).read_text(encoding="utf-8", errors="replace")

                parsed_title, features = preview_engine.parse_readme_content(readme_text, max_features=max_scenes)
                title = title or parsed_title

                self.log(f"[✓] Target Project: {title}")
                self.log(f"[✓] Output Folder: previews/{safe_folder_name}/")
                self.log(f"[✓] Extracted {len(features)} core showcase features.")
                for t, b in features:
                    self.log(f"    • {t}: {b[:55]}...")

                scene_specs = [
                    ("Autonomous Architecture", "A self-directing cognitive OS that plans, executes, and heals itself.", None)
                ]
                for t, b in features:
                    scene_specs.append((t, b, None))

                self.log(f"[*] Generating {len(scene_specs)} dynamic 1080p scenes with contextual logs & badges...")
                scene_images = []
                total = len(scene_specs)
                for idx, (t, b, img) in enumerate(scene_specs, 1):
                    scene_images.append(preview_engine.make_text_scene(t, b, title, idx, total))

                out_mp4 = target_dir / "preview_1080p.mp4"
                out_gif = target_dir / "preview_1080p.gif"
                self.last_mp4_path = out_mp4
                self.last_gif_path = out_gif

                self.log(f"[*] Encoding MP4 video ({len(scene_specs)} scenes, 30 FPS, 5000k bitrate)...")
                preview_engine.build_video(scene_images, out_mp4, fps=30)
                self.log(f"[✓] MP4 Completed: previews/{safe_folder_name}/{out_mp4.name} ({out_mp4.stat().st_size / (1024*1024):.1f} MB)")

                self.log("[*] Compiling high-definition GIF (960px, 256 colors)...")
                preview_engine.make_gif(out_mp4, out_gif, fps=10, max_width=960)
                self.log(f"[✓] GIF Completed: previews/{safe_folder_name}/{out_gif.name} ({out_gif.stat().st_size / (1024*1024):.1f} MB)")

                self.after(0, self._on_success)
            except Exception as exc:
                self.after(0, lambda: self._on_error(str(exc)))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_success(self):
        self.generate_btn.config(state="normal", text="🚀 Generate 1080p Full HD Preview")
        self.open_mp4_btn.config(state="normal")
        self.open_gif_btn.config(state="normal")
        self.open_dir_btn.config(state="normal")
        self.log(f"\n🎉 Success! Files saved in: previews/{self.last_output_dir.name}/")
        messagebox.showinfo("Success", f"Previews created and organized successfully in:\npreviews/{self.last_output_dir.name}/")

    def _on_error(self, err_msg):
        self.generate_btn.config(state="normal", text="🚀 Generate 1080p Full HD Preview")
        self.log(f"\n[!] Error: {err_msg}")
        messagebox.showerror("Error", f"An error occurred during build:\n{err_msg}")

    def open_mp4(self):
        if self.last_mp4_path and self.last_mp4_path.exists():
            os.startfile(str(self.last_mp4_path))

    def open_gif(self):
        if self.last_gif_path and self.last_gif_path.exists():
            os.startfile(str(self.last_gif_path))

    def open_folder(self):
        if self.last_output_dir and self.last_output_dir.exists():
            os.startfile(str(self.last_output_dir))


if __name__ == "__main__":
    app = App()
    app.mainloop()
