import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import math

# ─────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CPP      = os.path.join(BASE_DIR, "backend")

# ─────────────────────────────────────────
# COLORS
# ─────────────────────────────────────────
BG       = "#0b0f1a"
SIDEBAR  = "#0d1120"
CARD     = "#111827"
CARD2    = "#151e2e"
INPUT    = "#1a2236"
BORDER   = "#1f2d45"
ACCENT   = "#3b82f6"
ACCENT2  = "#60a5fa"
GREEN    = "#22c55e"
RED      = "#ef4444"
YELLOW   = "#f59e0b"
PURPLE   = "#a855f7"
CYAN     = "#06b6d4"
PINK     = "#ec4899"
TEXT1    = "#f1f5f9"
TEXT2    = "#94a3b8"
TEXT3    = "#475569"
WHITE    = "#ffffff"
SEM_LIMITS = {
    "SEM1": 22, "SEM2": 22, "SEM3": 22, "SEM4": 22,
    "SEM5": 22, "SEM6": 22, "SEM7": 22, "SEM8": 22,
}

GRADE_COLORS = {
    "A+": "#22c55e", "A": "#4ade80",
    "B+": "#3b82f6", "B": "#60a5fa",
    "C+": "#f59e0b", "C": "#fbbf24",
    "D+": "#a855f7", "D": "#c084fc",
    "F":  "#ef4444"
}

# ─────────────────────────────────────────
# C++ BRIDGE
# ─────────────────────────────────────────
def cpp(cmd, *args):
    try:
        result = subprocess.run(
            [CPP, cmd] + list(str(a) for a in args),
            capture_output=True, text=True, cwd=BASE_DIR
        )
        return result.stdout.strip()
    except Exception as e:
        return ""

def parse_lines(output):
    lines = [l for l in output.split("\n") if l.strip()]
    return lines

# ─────────────────────────────────────────
# STYLE SETUP
# ─────────────────────────────────────────
def setup_styles():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.Treeview",
        background=CARD, foreground=TEXT1,
        rowheight=34, fieldbackground=CARD,
        borderwidth=0, font=("Segoe UI", 10))
    style.configure("Dark.Treeview.Heading",
        background=CARD2, foreground=TEXT3,
        font=("Segoe UI", 9, "bold"), borderwidth=0,
        relief="flat")
    style.map("Dark.Treeview",
        background=[("selected", INPUT)],
        foreground=[("selected", ACCENT2)])
    style.configure("TCombobox",
        fieldbackground=WHITE, background=WHITE,
        foreground="#000000", arrowcolor=TEXT3,
        selectbackground=WHITE, selectforeground="#000000")
    style.map("TCombobox",
        fieldbackground=[("readonly", WHITE), ("!readonly", WHITE)],
        foreground=[("readonly", "#000000"), ("!readonly", "#000000")])
    style.configure("TScrollbar",
        background=BORDER, troughcolor=CARD,
        arrowcolor=TEXT3)

# ─────────────────────────────────────────
# CANVAS GRAPH WIDGET — HIGH QUALITY
# ─────────────────────────────────────────
class BarGraph(tk.Canvas):
    def __init__(self, parent, data, colors=None, **kwargs):
        super().__init__(parent, bg=CARD, highlightthickness=0, **kwargs)
        self.data   = data    # {label: value}
        self.colors = colors or [ACCENT, GREEN, YELLOW, PURPLE, CYAN, PINK]
        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        self.delete("all")
        if not self.data: return
        try:
            self.update_idletasks()
            w = self.winfo_width()
            h = self.winfo_height()
            if w < 10 or h < 10: return

            pad_l, pad_r, pad_t, pad_b = 45, 20, 24, 50
            items = list(self.data.items())
            n     = len(items)
            max_v = max(v for _, v in items) if items else 1
            if max_v == 0: max_v = 1

            graph_w = w - pad_l - pad_r
            graph_h = h - pad_t - pad_b
            slot_w  = graph_w // n
            bar_w   = max(14, slot_w - 14)

            # Background subtle grid
            for i in range(6):
                y   = pad_t + int(graph_h * i / 5)
                val = max_v * (5 - i) / 5
                self.create_line(pad_l, y, w - pad_r, y,
                                 fill=BORDER, width=1)
                self.create_text(pad_l - 6, y, text=f"{val:.0f}",
                                 anchor="e", fill=TEXT3,
                                 font=("Segoe UI", 8))

            for i, (label_text, value) in enumerate(items):
                x_center = pad_l + i * slot_w + slot_w // 2
                bar_h    = int((value / max_v) * graph_h) if max_v else 0
                x1 = x_center - bar_w // 2
                x2 = x_center + bar_w // 2
                y1 = pad_t + graph_h - bar_h
                y2 = pad_t + graph_h

                color = self.colors[i % len(self.colors)]

                # Glow / shadow effect
                for glow in [4, 2]:
                    self.create_rectangle(x1 - glow, y1 - glow,
                                          x2 + glow, y2,
                                          fill="", outline=_lighten(color),
                                          width=1)
                self.create_rectangle(x1, y1, x2, y2,
                                      fill=color, outline="", width=0)
                self.create_rectangle(x1, y1, x2, y1 + 3,
                                      fill=_lighten(color), outline="", width=0)

                self.create_text(x_center, y1 - 8, text=f"{value:.1f}",
                                 fill=WHITE,
                                 font=("Segoe UI", 9, "bold"),
                                 anchor="s")
                short = label_text[:6] if len(label_text) > 6 else label_text
                self.create_text(x_center, pad_t + graph_h + 8,
                                 text=short, fill=TEXT2,
                                 font=("Segoe UI", 9), anchor="n")
        except Exception as err:
            w = self.winfo_width() or 100
            h = self.winfo_height() or 50
            self.create_text(w // 2, h // 2,
                             text="Graph error",
                             fill=RED,
                             font=("Segoe UI", 10, "bold"))
            print("BarGraph draw error:", err)


class PieChart(tk.Canvas):
    def __init__(self, parent, data, **kwargs):
        super().__init__(parent, bg=CARD, highlightthickness=0, **kwargs)
        self.data = data  # {label: (value, color)}
        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        self.delete("all")
        if not self.data: return
        try:
            self.update_idletasks()
            w = self.winfo_width()
            h = self.winfo_height()
            if w < 10 or h < 10: return

            total = sum(v for v, _ in self.data.values())
            if total == 0: return

            pie_w = int(w * 0.45)
            cx, cy = pie_w // 2 + 10, h // 2
            r = min(cx - 10, cy - 10)

            start = 0
            for label_text, (val, color) in self.data.items():
                if val == 0: continue
                extent = (val / total) * 360
                self.create_arc(cx - r, cy - r, cx + r, cy + r,
                                start=start, extent=extent,
                                fill=color, outline=BG, width=2,
                                style="pieslice")
                start += extent

            lx = pie_w + 20
            ly = max(10, h // 2 - len(self.data) * 14)
            for label_text, (val, color) in self.data.items():
                pct = (val / total * 100) if total else 0
                self.create_rectangle(lx, ly, lx + 14, ly + 14,
                                      fill=color, outline="")
                self.create_text(lx + 20, ly + 7,
                                 text=f"{label_text}: {val} ({pct:.0f}%)",
                                 anchor="w", fill=TEXT1,
                                 font=("Segoe UI", 10))
                ly += 26
        except Exception as err:
            w = self.winfo_width() or 100
            h = self.winfo_height() or 50
            self.create_text(w // 2, h // 2,
                             text="Pie graph error",
                             fill=RED,
                             font=("Segoe UI", 10, "bold"))
            print("PieChart draw error:", err)


# ─────────────────────────────────────────
# PROGRESS BAR WIDGET for subject averages
# ─────────────────────────────────────────
class SubjectProgressBars(tk.Frame):
    def __init__(self, parent, data, colors=None, **kwargs):
        super().__init__(parent, bg=CARD, **kwargs)
        self.data   = data
        self.colors = colors or [ACCENT, GREEN, YELLOW, PURPLE, CYAN, PINK]
        self._draw()

    def _draw(self):
        for w in self.winfo_children():
            w.destroy()
        if not self.data:
            tk.Label(self, text="No data", bg=CARD, fg=TEXT3,
                     font=("Segoe UI", 9)).pack(pady=10)
            return

        max_v = max(self.data.values()) if self.data else 1
        if max_v == 0: max_v = 1

        for i, (subj, val) in enumerate(self.data.items()):
            color = self.colors[i % len(self.colors)]
            row = tk.Frame(self, bg=CARD)
            row.pack(fill="x", pady=3, padx=4)

            # Label
            tk.Label(row, text=subj, bg=CARD, fg=TEXT2,
                     font=("Segoe UI", 9, "bold"), width=8,
                     anchor="w").pack(side="left")

            # Bar container
            bar_outer = tk.Frame(row, bg=BORDER, height=18)
            bar_outer.pack(side="left", fill="x", expand=True, padx=(4, 8))
            bar_outer.pack_propagate(False)

            pct = val / 100  # subject avg is out of 100
            bar_inner = tk.Frame(bar_outer, bg=color, height=18)
            bar_inner.place(relx=0, rely=0, relwidth=pct, relheight=1)

            # Value label
            tk.Label(row, text=f"{val:.1f}", bg=CARD, fg=color,
                     font=("Courier New", 9, "bold"), width=5,
                     anchor="e").pack(side="left")

    def update_data(self, data):
        self.data = data
        self._draw()


# ─────────────────────────────────────────
# HELPER WIDGETS
# ─────────────────────────────────────────
def make_card(parent, accent_color=ACCENT, **kwargs):
    frame = tk.Frame(parent, bg=CARD, **kwargs)
    tk.Frame(frame, bg=accent_color, height=2).pack(fill="x")
    inner = tk.Frame(frame, bg=CARD)
    inner.pack(fill="both", expand=True, padx=14, pady=12)
    return frame, inner

def label(parent, text, size=10, color=TEXT2, bold=False, **kwargs):
    font = ("Segoe UI", size, "bold" if bold else "normal")
    return tk.Label(parent, text=text, bg=parent.cget("bg"),
                   fg=color, font=font, **kwargs)

def heading(parent, text, size=11, color=TEXT3):
    lbl = tk.Label(parent, text=text.upper(),
                  bg=parent.cget("bg"), fg=color,
                  font=("Segoe UI", 8, "bold"))
    lbl.pack(anchor="w", pady=(0, 10))
    return lbl

def make_entry(parent, width=25, placeholder=""):
    e = tk.Entry(parent, bg=INPUT, fg=TEXT1,
                insertbackground=TEXT1,
                font=("Segoe UI", 10), bd=0, width=width,
                relief="flat")
    e.pack(anchor="w", ipady=7, ipadx=10, fill="x")
    if placeholder:
        e.insert(0, placeholder)
        e.config(fg=TEXT3)
        e.bind("<FocusIn>",  lambda ev: (e.delete(0,"end"), e.config(fg=TEXT1)) if e.get()==placeholder else None)
        e.bind("<FocusOut>", lambda ev: (e.insert(0,placeholder), e.config(fg=TEXT3)) if e.get()=="" else None)
    return e

def field_row(parent, label_text, width=20, placeholder=""):
    tk.Label(parent, text=label_text, bg=parent.cget("bg"),
            fg=TEXT3, font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(8,3))
    return make_entry(parent, width, placeholder)

def btn(parent, text, color=ACCENT, cmd=None, side="left", **kw):
    b = tk.Button(parent, text=text, bg=color, fg=WHITE,
                 font=("Segoe UI", 10, "bold"),
                 bd=0, padx=16, pady=8, cursor="hand2",
                 activebackground=color, activeforeground=WHITE,
                 relief="flat", command=cmd, **kw)
    b.pack(side=side, padx=(0,8), pady=4)
    def on_enter(e): b.config(bg=_lighten(color))
    def on_leave(e): b.config(bg=color)
    b.bind("<Enter>", on_enter)
    b.bind("<Leave>", on_leave)
    return b

def _lighten(hex_color):
    try:
        r = min(255, int(hex_color[1:3],16)+30)
        g = min(255, int(hex_color[3:5],16)+30)
        b = min(255, int(hex_color[5:7],16)+30)
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return hex_color

def toast(root, msg, ok=True):
    t = tk.Toplevel(root)
    t.overrideredirect(True)
    t.attributes("-topmost", True)
    x = root.winfo_x() + root.winfo_width()  - 320
    y = root.winfo_y() + root.winfo_height() - 70
    t.geometry(f"300x46+{x}+{y}")
    t.configure(bg=CARD)
    color = GREEN if ok else RED
    tk.Frame(t, bg=color, width=4).pack(side="left", fill="y")
    tk.Label(t, text=msg, bg=CARD, fg=TEXT1,
            font=("Segoe UI", 10), padx=14).pack(side="left")
    t.after(2800, t.destroy)

def make_tree(parent, cols, widths, height=12):
    frame = tk.Frame(parent, bg=CARD)
    frame.pack(fill="both", expand=True)
    vsb = ttk.Scrollbar(frame, orient="vertical", style="TScrollbar")
    vsb.pack(side="right", fill="y")
    hsb = ttk.Scrollbar(frame, orient="horizontal", style="TScrollbar")
    hsb.pack(side="bottom", fill="x")
    tree = ttk.Treeview(frame, columns=cols, show="headings",
                       style="Dark.Treeview", height=height,
                       yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)
    for col, w in zip(cols, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, minwidth=w//2)
    tree.pack(fill="both", expand=True)
    tree.tag_configure("odd",  background=CARD)
    tree.tag_configure("even", background=CARD2)
    tree.tag_configure("top",  background="#1a3a1a", foreground=GREEN)
    return tree

def fill_tree(tree, rows, tag_top_roll=None):
    tree.delete(*tree.get_children())
    for i, row in enumerate(rows):
        tag = "top" if (tag_top_roll and str(row[0])==tag_top_roll) else ("even" if i%2==0 else "odd")
        tree.insert("", "end", values=row, tags=(tag,))

# ─────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("BSc Computer Engineering 2025 — Student Management System")
        self.root.geometry("1280x780")
        self.root.configure(bg=BG)
        self.root.minsize(960, 640)
        setup_styles()

        self.pages = {}
        self._build_layout()
        self.show("dashboard")

    # ── LAYOUT ──
    def _build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        right = tk.Frame(self.root, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        self.topbar = tk.Frame(right, bg=SIDEBAR, height=56)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)
        tk.Frame(self.topbar, bg=BORDER, height=1).pack(side="bottom", fill="x")
        self.page_title = tk.Label(self.topbar, text="",
                                  bg=SIDEBAR, fg=TEXT1,
                                  font=("Segoe UI", 15, "bold"))
        self.page_title.pack(side="left", padx=22, pady=14)
        self.subtitle = tk.Label(self.topbar, text="BSc CPE 2025 • Spring 2026",
                                bg=SIDEBAR, fg=TEXT3,
                                font=("Segoe UI", 9))
        self.subtitle.pack(side="left")

        tk.Button(self.topbar, text="⟳  Refresh",
                 bg=CARD, fg=TEXT2, bd=0, padx=12, pady=5,
                 font=("Segoe UI", 9), cursor="hand2",
                 activebackground=BORDER,
                 command=self._refresh).pack(side="right", padx=18, pady=14)

        self.content_wrap = tk.Frame(right, bg=BG)
        self.content_wrap.pack(fill="both", expand=True)

        self.content = tk.Frame(self.content_wrap, bg=BG)
        self.content.pack(fill="both", expand=True, padx=22, pady=18)

        self._build_dashboard()
        self._build_students()
        self._build_marks()
        self._build_result_card()
        self._build_analytics()
        self._build_add_student()
        self._build_courses()

    def _build_sidebar(self):
        logo = tk.Frame(self.sidebar, bg=SIDEBAR)
        logo.pack(fill="x", padx=14, pady=16)
        icon = tk.Label(logo, text="CPE", bg=ACCENT, fg=WHITE,
                       font=("Segoe UI", 11, "bold"),
                       width=4, padx=4, pady=6)
        icon.pack(side="left")
        tk.Label(logo, text="  Student\n  Management",
                bg=SIDEBAR, fg=TEXT1,
                font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x")

        self.nav_btns = {}
        nav = [
            ("dashboard",    "📊", "Dashboard"),
            ("students",     "👥", "All Students"),
            ("marks",        "📝", "Enter Marks"),
            ("result_card",  "🎓", "Result Card"),
            ("analytics",    "📈", "Analytics"),
            ("add_student",  "➕", "Add Student"),
            ("courses",      "📚", "Courses"),
        ]

        nav_frame = tk.Frame(self.sidebar, bg=SIDEBAR)
        nav_frame.pack(fill="x", padx=8, pady=10)

        for page_id, icon_str, label_text in nav:
            b = tk.Button(nav_frame,
                         text=f"  {icon_str}  {label_text}",
                         bg=SIDEBAR, fg=TEXT2,
                         font=("Segoe UI", 10),
                         anchor="w", bd=0, padx=8, pady=9,
                         cursor="hand2",
                         activebackground=CARD,
                         activeforeground=TEXT1,
                         relief="flat",
                         command=lambda p=page_id: self.show(p))
            b.pack(fill="x", pady=2)
            self.nav_btns[page_id] = b

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(side="bottom", fill="x")
        tk.Label(self.sidebar, text="Spring 2026\nBSc CPE Session 2025",
                bg=SIDEBAR, fg=TEXT3,
                font=("Segoe UI", 8)).pack(side="bottom", pady=10)

    def show(self, page_id):
        for p in self.pages.values():
            p.pack_forget()
        self.pages[page_id].pack(fill="both", expand=True)

        titles = {
            "dashboard":   "📊  Dashboard",
            "students":    "👥  All Students",
            "marks":       "📝  Enter / Edit Marks",
            "result_card": "🎓  Result Card",
            "analytics":   "📈  Analytics & Graphs",
            "add_student": "➕  Add New Student",
            "courses":     "📚  Course Management",
        }
        self.page_title.config(text=titles.get(page_id, ""))

        for pid, b in self.nav_btns.items():
            if pid == page_id:
                b.config(bg=CARD, fg=ACCENT2, font=("Segoe UI", 10, "bold"))
            else:
                b.config(bg=SIDEBAR, fg=TEXT2, font=("Segoe UI", 10))

        loaders = {
            "dashboard":   self._load_dashboard,
            "students":    self._load_students,
            "analytics":   self._load_analytics,
        }
        if page_id in loaders:
            loaders[page_id]()

    def _refresh(self):
        page = [k for k,v in self.pages.items() if v.winfo_ismapped()]
        if page: self.show(page[0])
        toast(self.root, "Data refreshed! ✅")

    # ══════════════════════════════════════
    # PAGE 1: DASHBOARD  (IMPROVED)
    # ══════════════════════════════════════
    def _build_dashboard(self):
        page = tk.Frame(self.content, bg=BG)
        self.pages["dashboard"] = page

        canvas = tk.Canvas(page, bg=BG, highlightthickness=0)
        vscroll = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        scroll_frame = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(win_id, width=e.width))

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Top stats row
        self.stat_frame = tk.Frame(scroll_frame, bg=BG)
        self.stat_frame.pack(fill="x", pady=(0,12))

        self.stat_widgets = {}
        stat_defs = [
            ("total",    "TOTAL STUDENTS", "—", WHITE,  ACCENT),
            ("avg_cgpa", "AVG CGPA",       "—", GREEN,  GREEN),
            ("top_cgpa", "TOP CGPA",       "—", YELLOW, YELLOW),
            ("passing",  "PASSING",        "—", CYAN,   CYAN),
            ("top_name", "TOP STUDENT",    "—", PINK,   PINK),
        ]
        for key, title, val, num_color, line_color in stat_defs:
            card, inner = make_card(self.stat_frame, accent_color=line_color)
            card.pack(side="left", fill="both", expand=True, padx=(0,10))
            tk.Label(inner, text=title, bg=CARD, fg=TEXT3,
                    font=("Segoe UI", 7, "bold")).pack(anchor="w")
            v_lbl = tk.Label(inner, text=val, bg=CARD,
                            fg=num_color, font=("Courier New", 22, "bold"))
            v_lbl.pack(anchor="w", pady=(6,2))
            s_lbl = tk.Label(inner, text="", bg=CARD, fg=TEXT3,
                            font=("Segoe UI", 8))
            s_lbl.pack(anchor="w")
            self.stat_widgets[key] = (v_lbl, s_lbl)

        # Middle row: subject progress bars (left) + grade pie (right)
        mid = tk.Frame(scroll_frame, bg=BG)
        mid.pack(fill="both", expand=True, pady=(0,12))

        # Subject averages as progress bars — left 55%
        bar_card, bar_inner = make_card(mid, ACCENT)
        bar_card.pack(side="left", fill="both", expand=True, padx=(0,12))
        tk.Label(bar_inner, text="SUBJECT AVERAGES (SEM 2)",
                bg=CARD, fg=TEXT3,
                font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,8))
        self.subj_progress = SubjectProgressBars(bar_inner, {})
        self.subj_progress.pack(fill="both", expand=True)

        # Grade pie — right
        pie_card, pie_inner = make_card(mid, PURPLE)
        pie_card.pack(side="left", fill="both", expand=True)
        tk.Label(pie_inner, text="GRADE DISTRIBUTION",
                bg=CARD, fg=TEXT3,
                font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,8))
        self.pie_chart = PieChart(pie_inner, {})
        self.pie_chart.pack(fill="both", expand=True)

        # Bottom: Top 10 — full width, full height scrollable
        bot_card, bot_inner = make_card(scroll_frame, GREEN)
        bot_card.pack(fill="both", expand=True)
        tk.Label(bot_inner, text="TOP 10 STUDENTS BY CGPA",
                bg=CARD, fg=TEXT3,
                font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,8))
        cols   = ["#","Roll No","Name","SEM1 GPA","SEM2 GPA","CGPA","Status"]
        widths = [35, 140, 180, 95, 95, 85, 90]
        # Full expand tree — no fixed height so it fills the panel
        self.dash_tree = make_tree(bot_inner, cols, widths, height=8)

    def _load_dashboard(self):
        out   = cpp("GET_STATS")
        lines = parse_lines(out)

        stats    = {}
        sub_data = {}
        for line in lines:
            if ":" in line:
                k, _, v = line.partition(":")
                if k == "SUB":
                    parts = v.split(":")
                    sub_data[parts[0]] = float(parts[1])
                else:
                    stats[k] = v

        total    = stats.get("TOTAL", "0")
        avg_cgpa = stats.get("AVG_CGPA", "0")
        top_cgpa = stats.get("TOP_CGPA", "0")
        top_name = stats.get("TOP_NAME", "—")
        passing  = stats.get("PASSING", "0")

        self.stat_widgets["total"][0].config(text=total)
        self.stat_widgets["total"][1].config(text="All students")
        self.stat_widgets["avg_cgpa"][0].config(text=avg_cgpa)
        self.stat_widgets["avg_cgpa"][1].config(text="Class average")
        self.stat_widgets["top_cgpa"][0].config(text=top_cgpa)
        self.stat_widgets["top_cgpa"][1].config(text="Highest CGPA")
        self.stat_widgets["passing"][0].config(text=passing)
        n = int(total) if total.isdigit() else 1
        p = int(passing) if passing.isdigit() else 0
        self.stat_widgets["passing"][1].config(
            text=f"{p/n*100:.1f}% pass rate" if n else "—")
        name_short = top_name.split()[0] if top_name != "—" else "—"
        self.stat_widgets["top_name"][0].config(
            text=name_short, font=("Segoe UI", 14, "bold"))
        self.stat_widgets["top_name"][1].config(text="Top performer 🏆")

        # Subject progress bars
        self.subj_progress.update_data(sub_data)

        # Top students table + pie data
        all_out = cpp("GET_STUDENTS")
        rows = []
        grade_counts = {"A+/A":0, "B+/B":0, "C+/C":0, "D":0, "F":0}

        for line in parse_lines(all_out):
            parts = line.split("|")
            if len(parts) < 6: continue
            roll  = parts[0]
            name  = parts[1]
            cgpa  = float(parts[5]) if parts[5] else 0

            gpa_out = cpp("GET_GPA", roll)
            gpas    = gpa_out.split("|") if gpa_out else ["0","0","0"]
            gpa1 = gpas[0] if len(gpas)>0 else "0"
            gpa2 = gpas[1] if len(gpas)>1 else "0"

            status = "✅ Pass" if cgpa >= 2.0 else "❌ Fail"
            rows.append((len(rows)+1, roll, name, gpa1, gpa2,
                        f"{cgpa:.2f}", status))

            if cgpa >= 3.5:   grade_counts["A+/A"] += 1
            elif cgpa >= 3.0: grade_counts["B+/B"] += 1
            elif cgpa >= 2.5: grade_counts["C+/C"] += 1
            elif cgpa >= 2.0: grade_counts["D"]    += 1
            else:             grade_counts["F"]    += 1

        rows.sort(key=lambda r: float(r[5]), reverse=True)
        for i, r in enumerate(rows):
            rows[i] = (i+1,) + r[1:]

        fill_tree(self.dash_tree, rows[:10])

        pie_colors = [GREEN, ACCENT, YELLOW, PURPLE, RED]
        pie_data = {k: (v, pie_colors[i])
                   for i,(k,v) in enumerate(grade_counts.items()) if v>0}
        self.pie_chart.data = pie_data
        self.pie_chart._draw()

    # ══════════════════════════════════════
    # PAGE 2: ALL STUDENTS
    # ══════════════════════════════════════
    def _build_students(self):
        page = tk.Frame(self.content, bg=BG)
        self.pages["students"] = page

        top = tk.Frame(page, bg=BG)
        top.pack(fill="x", pady=(0,12))

        tk.Label(top, text="🔍", bg=BG, fg=TEXT2,
                font=("Segoe UI", 12)).pack(side="left")
        self.stu_search = tk.Entry(top, bg=INPUT, fg=TEXT1,
                                  insertbackground=TEXT1,
                                  font=("Segoe UI", 10), bd=0, width=30)
        self.stu_search.pack(side="left", ipady=7, ipadx=10, padx=6)
        self.stu_search.bind("<KeyRelease>", lambda e: self._load_students())

        btn(top, "🗑  Delete", RED, self._delete_student, "right")
        btn(top, "✏️  Edit",   YELLOW, self._edit_student_popup, "right")
        btn(top, "📄  Result Card", PURPLE, self._quick_result, "right")

        self.stu_count = tk.Label(top, text="", bg=BG, fg=TEXT2,
                                 font=("Segoe UI", 9))
        self.stu_count.pack(side="right", padx=10)

        card, inner = make_card(page, ACCENT)
        card.pack(fill="both", expand=True)
        cols   = ["#","Roll No","Name","Gender","Contact","Father","SEM1 GPA","SEM2 GPA","CGPA","Status"]
        widths = [30, 130, 160, 70, 120, 160, 85, 85, 80, 90]
        self.stu_tree = make_tree(inner, cols, widths)

    def _load_students(self):
        query  = self.stu_search.get().lower() if hasattr(self, "stu_search") else ""
        out    = cpp("GET_STUDENTS")
        students = []

        for line in parse_lines(out):
            parts = line.split("|")
            if len(parts) < 6: continue
            roll, name, gender = parts[0], parts[1], parts[2]
            contact, father    = parts[3], parts[4]
            cgpa = float(parts[5]) if parts[5] else 0.0

            if query and query not in name.lower() and query not in roll.lower():
                continue

            gpa_out = cpp("GET_GPA", roll)
            gpas    = gpa_out.split("|") if gpa_out else ["—","—","—"]
            gpa1 = gpas[0] if len(gpas)>0 else "—"
            gpa2 = gpas[1] if len(gpas)>1 else "—"

            students.append({
                "roll": roll,
                "name": name,
                "gender": gender,
                "contact": contact,
                "father": father,
                "gpa1": gpa1,
                "gpa2": gpa2,
                "cgpa": cgpa,
            })

        students.sort(key=lambda s: s["cgpa"], reverse=True)
        top3_rolls = [s["roll"] for s in students[:3]]

        rows = []
        for idx, student in enumerate(students, start=1):
            if idx == 1:
                status = "1st"
            elif idx == 2:
                status = "2nd"
            elif idx == 3:
                status = "3rd"
            else:
                status = "Pass" if student["cgpa"] >= 2.0 else "Fail"

            rows.append((idx, student["roll"], student["name"], student["gender"],
                         student["contact"], student["father"],
                         student["gpa1"], student["gpa2"],
                         f"{student['cgpa']:.2f}", status))

        fill_tree(self.stu_tree, rows)
        if hasattr(self, "stu_count"):
            self.stu_count.config(text=f"Showing {len(rows)} students")

    def _get_selected_roll(self, tree):
        sel = tree.selection()
        if not sel:
            toast(self.root, "Please select a student first!", False)
            return None
        return tree.item(sel[0])["values"][1]

    def _delete_student(self):
        roll = self._get_selected_roll(self.stu_tree)
        if not roll: return
        if not messagebox.askyesno("Confirm",
            f"Delete '{roll}'?\nThis action cannot be undone!"):
            return
        out = cpp("DELETE_STUDENT", roll)
        if "OK" in out:
            self._load_students()
            toast(self.root, "Student deleted successfully! ✅")
        else:
            toast(self.root, "Error! Try again.", False)

    def _edit_student_popup(self):
        roll = self._get_selected_roll(self.stu_tree)
        if not roll: return

        out  = cpp("GET_STUDENTS")
        data = {}
        for line in parse_lines(out):
            parts = line.split("|")
            if parts[0] == roll:
                data = {"name": parts[1], "gender": parts[2],
                       "cnic": "—", "contact": parts[3],
                       "father": parts[4]}
                break

        popup = tk.Toplevel(self.root)
        popup.title("Edit Student")
        popup.configure(bg=BG)
        popup.geometry("420x380")
        popup.grab_set()

        card, inner = make_card(popup, YELLOW)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(inner, text=f"Edit: {roll}",
                bg=CARD, fg=YELLOW,
                font=("Segoe UI", 11, "bold")).pack(anchor="w")

        e_name    = field_row(inner, "Full Name")
        e_gender  = field_row(inner, "Gender (Male/Female)")
        e_contact = field_row(inner, "Contact")
        e_father  = field_row(inner, "Father Name")

        e_name.delete(0,"end");    e_name.insert(0, data.get("name",""))
        e_gender.delete(0,"end");  e_gender.insert(0, data.get("gender",""))
        e_contact.delete(0,"end"); e_contact.insert(0, data.get("contact",""))
        e_father.delete(0,"end");  e_father.insert(0, data.get("father",""))

        def save():
            out = cpp("UPDATE_STUDENT", roll,
                     e_name.get(), e_gender.get(),
                     "—", e_contact.get(), e_father.get())
            if "OK" in out:
                popup.destroy()
                self._load_students()
                toast(self.root, "Student updated! ✅")

        row = tk.Frame(inner, bg=CARD)
        row.pack(fill="x", pady=(16,0))
        btn(row, "💾  Save", GREEN, save)
        btn(row, "Cancel", TEXT3, popup.destroy)

    def _quick_result(self):
        roll = self._get_selected_roll(self.stu_tree)
        if not roll: return
        self.result_roll_var.set(roll)
        self.show("result_card")
        self._load_result_card()

    # ══════════════════════════════════════
    # PAGE 3: ENTER MARKS
    # ══════════════════════════════════════
    def _build_marks(self):
        page = tk.Frame(self.content, bg=BG)
        self.pages["marks"] = page

        left = tk.Frame(page, bg=BG, width=260)
        left.pack(side="left", fill="y", padx=(0,16))
        left.pack_propagate(False)

        sel_card, sel_inner = make_card(left, ACCENT)
        sel_card.pack(fill="x", pady=(0,12))

        tk.Label(sel_inner, text="SELECT STUDENT & COURSE",
                bg=CARD, fg=TEXT3,
                font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,10))

        tk.Label(sel_inner, text="Roll Number", bg=CARD,
                fg=TEXT3, font=("Segoe UI", 8)).pack(anchor="w")
        self.marks_roll = tk.Entry(sel_inner, bg=INPUT, fg=TEXT1,
                                  insertbackground=TEXT1,
                                  font=("Segoe UI", 10), bd=0, width=22)
        self.marks_roll.pack(anchor="w", ipady=6, ipadx=8, fill="x")

        tk.Label(sel_inner, text="Semester", bg=CARD,
                fg=TEXT3, font=("Segoe UI", 8)).pack(anchor="w", pady=(8,3))
        self.marks_sem = tk.StringVar(value="SEM2")
        sem_combo = ttk.Combobox(sel_inner, textvariable=self.marks_sem,
                                values=["SEM1","SEM2"],
                                state="readonly", width=20,
                                font=("Segoe UI", 10))
        sem_combo.pack(anchor="w", ipady=4)

        tk.Label(sel_inner, text="Course", bg=CARD,
                fg=TEXT3, font=("Segoe UI", 8)).pack(anchor="w", pady=(8,3))
        self.marks_course = tk.StringVar(value="OOPS")
        self.course_combo = ttk.Combobox(sel_inner,
                                        textvariable=self.marks_course,
                                        state="readonly", width=20,
                                        font=("Segoe UI", 10))
        self.course_combo.pack(anchor="w", ipady=4)

        sem_combo.bind("<<ComboboxSelected>>", lambda e: self._update_course_list())
        self._update_course_list()

        btn_row = tk.Frame(sel_inner, bg=CARD)
        btn_row.pack(fill="x", pady=(12,0))
        btn(btn_row, "Load Marks", ACCENT, self._load_marks_form)

        cur_card, cur_inner = make_card(left, GREEN)
        cur_card.pack(fill="both", expand=True)
        tk.Label(cur_inner, text="CURRENT MARKS",
                bg=CARD, fg=TEXT3,
                font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,8))
        self.cur_marks_lbl = tk.Label(cur_inner, text="Select student\nto view marks",
                                     bg=CARD, fg=TEXT3,
                                     font=("Segoe UI", 9), justify="left")
        self.cur_marks_lbl.pack(anchor="w")

        right_f = tk.Frame(page, bg=BG)
        right_f.pack(side="left", fill="both", expand=True)

        form_card, self.marks_form = make_card(right_f, YELLOW)
        form_card.pack(fill="both", expand=True)

        tk.Label(self.marks_form, text="ENTER / EDIT MARKS",
                bg=CARD, fg=TEXT3,
                font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,12))

        self.mark_entries = {}
        mark_fields = [
            ("q1",    "Quiz 1",     "10", GREEN),
            ("q2",    "Quiz 2",     "10", GREEN),
            ("assign","Assignment", "10", CYAN),
            ("mid",   "Midterm",    "30", YELLOW),
            ("final", "Final Exam", "40", ACCENT),
        ]

        grid = tk.Frame(self.marks_form, bg=CARD)
        grid.pack(fill="x")

        for i, (key, lbl_text, max_v, color) in enumerate(mark_fields):
            col = i % 3
            row_num = i // 3
            cell = tk.Frame(grid, bg=CARD)
            cell.grid(row=row_num, column=col, padx=(0,12), pady=6, sticky="w")
            tk.Label(cell, text=f"{lbl_text} (/{max_v})",
                    bg=CARD, fg=color,
                    font=("Segoe UI", 8, "bold")).pack(anchor="w")
            e = tk.Entry(cell, bg=INPUT, fg=TEXT1,
                        insertbackground=TEXT1,
                        font=("Courier New", 13, "bold"),
                        bd=0, width=8)
            e.pack(ipady=8, ipadx=6)
            self.mark_entries[key] = e

        total_frame = tk.Frame(self.marks_form, bg=CARD2)
        total_frame.pack(fill="x", pady=(14,0))
        tk.Frame(total_frame, bg=BORDER, height=1).pack(fill="x")
        tf_inner = tk.Frame(total_frame, bg=CARD2)
        tf_inner.pack(fill="x", padx=12, pady=10)

        self.total_lbl = tk.Label(tf_inner, text="Total: —/100",
                                 bg=CARD2, fg=WHITE,
                                 font=("Courier New", 14, "bold"))
        self.total_lbl.pack(side="left")
        self.grade_lbl = tk.Label(tf_inner, text="Grade: —",
                                 bg=CARD2, fg=GREEN,
                                 font=("Segoe UI", 13, "bold"))
        self.grade_lbl.pack(side="left", padx=20)
        self.pct_lbl = tk.Label(tf_inner, text="",
                                bg=CARD2, fg=TEXT2,
                                font=("Segoe UI", 10))
        self.pct_lbl.pack(side="left")

        for e in self.mark_entries.values():
            e.bind("<KeyRelease>", lambda ev: self._calc_total())

        save_row = tk.Frame(self.marks_form, bg=CARD)
        save_row.pack(fill="x", pady=(14,0))
        btn(save_row, "💾  Save Marks", GREEN, self._save_marks)
        btn(save_row, "🗑  Clear",      RED,   self._clear_marks)

    def _update_course_list(self):
        sem = self.marks_sem.get()
        try:
            courses_out = open(os.path.join(BASE_DIR,"data","courses.txt")).read()
            codes = [l.split("|")[1] for l in courses_out.split("\n")
                    if l.startswith(sem)]
            self.course_combo["values"] = codes
            if codes: self.marks_course.set(codes[0])
        except:
            pass

    def _load_marks_form(self):
        roll   = self.marks_roll.get().strip()
        sem    = self.marks_sem.get()
        course = self.marks_course.get()
        if not roll:
            toast(self.root, "Please enter a roll number!", False); return

        out = cpp("GET_MARKS", roll, sem)
        found = False
        cur_text = f"Student: {roll}\nSemester: {sem}\n\n"

        for line in parse_lines(out):
            parts = line.split("|")
            if len(parts) < 9: continue
            ccode = parts[0]
            cur_text += f"{ccode}: {parts[6]}/100 ({parts[7]})\n"

            if ccode == course:
                for key, idx in [("q1",1),("q2",2),("mid",3),
                                 ("final",4),("assign",5)]:
                    self.mark_entries[key].delete(0,"end")
                    self.mark_entries[key].insert(0, parts[idx])
                found = True

        if not found:
            for e in self.mark_entries.values():
                e.delete(0,"end")

        self.cur_marks_lbl.config(text=cur_text if cur_text.strip() else "No marks found")
        self._calc_total()

    def _calc_total(self):
        try:
            vals  = {k: int(e.get() or 0) for k, e in self.mark_entries.items()}
            total = sum(vals.values())
            grade = self._get_grade(total)
            color = GRADE_COLORS.get(grade, TEXT2)
            self.total_lbl.config(text=f"Total: {total}/100")
            self.grade_lbl.config(text=f"Grade: {grade}", fg=color)
            self.pct_lbl.config(text=f"({total:.0f}%)")
        except:
            pass

    def _get_grade(self, pct):
        if pct >= 85: return "A+"
        if pct >= 80: return "A"
        if pct >= 75: return "B+"
        if pct >= 70: return "B"
        if pct >= 65: return "C+"
        if pct >= 60: return "C"
        if pct >= 55: return "D+"
        if pct >= 50: return "D"
        return "F"

    def _save_marks(self):
        roll   = self.marks_roll.get().strip()
        sem    = self.marks_sem.get()
        course = self.marks_course.get()
        if not roll:
            toast(self.root, "Please enter a roll number!", False); return
        try:
            vals = {k: int(e.get() or 0) for k, e in self.mark_entries.items()}
            out  = cpp("UPDATE_MARKS", roll, sem, course,
                      vals["q1"], vals["q2"], vals["mid"],
                      vals["final"], vals["assign"])
            if "OK" in out:
                toast(self.root, f"Marks saved for {roll}! ✅")
                self._load_marks_form()
            else:
                toast(self.root, "Error saving marks!", False)
        except ValueError:
            toast(self.root, "Please enter numbers only!", False)

    def _clear_marks(self):
        for e in self.mark_entries.values():
            e.delete(0,"end")
        self.total_lbl.config(text="Total: —/100")
        self.grade_lbl.config(text="Grade: —")

    # ══════════════════════════════════════
    # PAGE 4: RESULT CARD  (FULLY IMPROVED)
    # ══════════════════════════════════════
    def _build_result_card(self):
        page = tk.Frame(self.content, bg=BG)
        self.pages["result_card"] = page

        top = tk.Frame(page, bg=BG)
        top.pack(fill="x", pady=(0,14))

        tk.Label(top, text="Roll Number:",
                bg=BG, fg=TEXT2,
                font=("Segoe UI", 10)).pack(side="left")
        self.result_roll_var = tk.StringVar(value="2025-BSCPE-19")
        e = tk.Entry(top, textvariable=self.result_roll_var,
                    bg=INPUT, fg=TEXT1, insertbackground=TEXT1,
                    font=("Segoe UI", 10), bd=0, width=20)
        e.pack(side="left", ipady=7, ipadx=10, padx=8)
        btn(top, "🎓  Generate Card", PURPLE, self._load_result_card)

        self.rc_canvas = tk.Canvas(page, bg=BG, highlightthickness=0)
        rc_scroll = ttk.Scrollbar(page, orient="vertical",
                                 command=self.rc_canvas.yview)
        self.rc_canvas.configure(yscrollcommand=rc_scroll.set)
        rc_scroll.pack(side="right", fill="y")
        self.rc_canvas.pack(fill="both", expand=True)

        self.rc_frame = tk.Frame(self.rc_canvas, bg=BG)
        self._rc_win = self.rc_canvas.create_window((0,0), window=self.rc_frame, anchor="nw")
        self.rc_frame.bind("<Configure>",
            lambda e: self.rc_canvas.configure(
                scrollregion=self.rc_canvas.bbox("all")))
        self.rc_canvas.bind("<Configure>",
            lambda e: self.rc_canvas.itemconfig(self._rc_win, width=e.width))

        # Mousewheel scrolling
        def _on_mousewheel(event):
            self.rc_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.rc_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _load_result_card(self):
        for w in self.rc_frame.winfo_children():
            w.destroy()

        roll = self.result_roll_var.get().strip()
        out  = cpp("GET_RESULT", roll)

        if "NOT_FOUND" in out or not out:
            tk.Label(self.rc_frame, text="❌ Student not found! (backend data unavailable)",
                    bg=BG, fg=RED,
                    font=("Segoe UI", 14)).pack(pady=20)
            tk.Label(self.rc_frame, text=f"Backend output: '{out[:200] if out else 'EMPTY'}'",
                    bg=BG, fg=YELLOW,
                    font=("Segoe UI", 9), wraplength=800).pack(pady=10)
            tk.Label(self.rc_frame, text=f"CPP path: {CPP}",
                    bg=BG, fg=TEXT3,
                    font=("Segoe UI", 9)).pack()
            return

        info      = {}
        sem_marks = {"SEM1": [], "SEM2": []}
        sem_gpa   = {}

        for line in parse_lines(out):
            if line.startswith("NAME:"):    info["name"]   = line[5:]
            elif line.startswith("ROLL:"):  info["roll"]   = line[5:]
            elif line.startswith("FATHER:"):info["father"] = line[7:]
            elif line.startswith("CGPA:"):  info["cgpa"]   = line[5:]
            elif line.startswith("SEM:"):
                parts = line.split(":")
                sem_gpa[parts[1]] = parts[3]
            elif line.startswith("MARKS:"):
                rest  = line[6:]
                parts = rest.split("|")
                sem   = parts[0]
                if len(parts) >= 12:
                    sem_marks[sem].append(parts[1:])

        def _ordinal(n):
            if n is None:
                return "—"
            if 10 <= n % 100 <= 20:
                suffix = "th"
            else:
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
            return f"{n}{suffix}"

        rank_text = "—"
        rank_color = TEXT2
        if info.get("roll"):
            all_students = []
            for line in parse_lines(cpp("GET_STUDENTS")):
                parts = line.split("|")
                if len(parts) >= 6:
                    try:
                        all_students.append((parts[0], float(parts[5] or 0)))
                    except:
                        all_students.append((parts[0], 0.0))
            all_students.sort(key=lambda x: x[1], reverse=True)
            for idx, (student_roll, _) in enumerate(all_students, start=1):
                if student_roll == info["roll"]:
                    rank_text = _ordinal(idx)
                    rank_color = GREEN if idx == 1 else YELLOW if idx <= 3 else TEXT2
                    break

        # ── Header ──
        header = tk.Frame(self.rc_frame, bg=CARD2)
        header.pack(fill="x", pady=(0,12), padx=2)
        tk.Frame(header, bg=ACCENT, height=3).pack(fill="x")
        h_inner = tk.Frame(header, bg=CARD2)
        h_inner.pack(fill="x", padx=20, pady=16)

        tk.Label(h_inner, text="RESULT CARD",
                bg=CARD2, fg=ACCENT2,
                font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(h_inner, text=info.get("name","—"),
                bg=CARD2, fg=WHITE,
                font=("Segoe UI", 18, "bold")).pack(anchor="w")

        info_row = tk.Frame(h_inner, bg=CARD2)
        info_row.pack(fill="x", pady=(8,0))
        for lbl_t, val in [
            ("Roll No", info.get("roll","—")),
            ("Father",  info.get("father","—")),
            ("Program", "BSc Computer Engineering"),
            ("Session", "2025"),
        ]:
            cell = tk.Frame(info_row, bg=CARD2)
            cell.pack(side="left", padx=(0,30))
            tk.Label(cell, text=lbl_t, bg=CARD2, fg=TEXT3,
                    font=("Segoe UI", 8)).pack(anchor="w")
            tk.Label(cell, text=val, bg=CARD2, fg=TEXT1,
                    font=("Segoe UI", 10, "bold")).pack(anchor="w")

        def _gpa_to_grade(gpa_str):
            try:
                gpa_v = float(gpa_str)
            except:
                return "—"
            if gpa_v >= 3.5: return "A+"
            if gpa_v >= 3.0: return "A"
            if gpa_v >= 2.5: return "B+"
            if gpa_v >= 2.0: return "B"
            if gpa_v >= 1.5: return "C+"
            if gpa_v >= 1.0: return "C"
            if gpa_v >= 0.5: return "D+"
            if gpa_v >= 0.0: return "D"
            return "F"

        summary = tk.Frame(h_inner, bg=CARD2)
        summary.pack(fill="x", pady=(12,0))
        for label_text, value_text, color in [
            ("SEM 1 GPA", sem_gpa.get("SEM1", "—"), ACCENT),
            ("SEM 2 GPA", sem_gpa.get("SEM2", "—"), GREEN),
            ("FINAL CGPA", info.get("cgpa", "—"), YELLOW),
        ]:
            card = tk.Frame(summary, bg=_lighten(color), padx=14, pady=10)
            card.pack(side="left", fill="both", expand=True, padx=(0,12))
            tk.Label(card, text=label_text, bg=_lighten(color), fg=TEXT3,
                    font=("Segoe UI", 8)).pack(anchor="w")
            tk.Label(card, text=value_text, bg=_lighten(color), fg=TEXT1,
                    font=("Segoe UI", 14, "bold")).pack(anchor="w")
            tk.Label(card, text=_gpa_to_grade(value_text), bg=_lighten(color),
                    fg=TEXT1, font=("Segoe UI", 9)).pack(anchor="w", pady=(4,0))

        try:
            gpa1_val = float(sem_gpa.get("SEM1", "0"))
            gpa2_val = float(sem_gpa.get("SEM2", "0"))
            diff_val = gpa2_val - gpa1_val
            if abs(diff_val) < 0.01:
                improvement_text = "No change from SEM1 to SEM2"
                improvement_color = TEXT3
            elif diff_val > 0:
                improvement_text = f"Improved by {diff_val:.2f} points from SEM1"
                improvement_color = GREEN
            else:
                improvement_text = f"Dropped by {abs(diff_val):.2f} points from SEM1"
                improvement_color = RED
        except:
            improvement_text = "Improvement data unavailable"
            improvement_color = TEXT2

        improvement_card = tk.Frame(h_inner, bg=CARD, padx=14, pady=10)
        improvement_card.pack(fill="x", pady=(12,0))
        tk.Label(improvement_card, text="IMPROVEMENT SUMMARY", bg=CARD,
                fg=TEXT3, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(improvement_card, text=improvement_text, bg=CARD,
                fg=improvement_color, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(6,0))

        # CGPA + status badge
        cgpa_val   = float(info.get("cgpa","0")) if info.get("cgpa","0").replace(".","").isdigit() else 0
        cgpa_color = GREEN if cgpa_val>=3.0 else YELLOW if cgpa_val>=2.0 else RED
        badge = tk.Frame(h_inner, bg=_lighten(cgpa_color), padx=16, pady=8)
        badge.pack(anchor="w", pady=(12,0))
        tk.Label(badge, text=f"CGPA: {info.get('cgpa','—')}",
                bg=_lighten(cgpa_color), fg=WHITE,
                font=("Courier New", 16, "bold")).pack(side="left")
        status_txt = "  PASS ✅" if cgpa_val >= 2.0 else "  FAIL ❌"
        tk.Label(badge, text=status_txt,
                bg=_lighten(cgpa_color), fg=WHITE,
                font=("Segoe UI", 11, "bold")).pack(side="left", padx=10)

        rank_frame = tk.Frame(h_inner, bg=CARD2)
        rank_frame.pack(anchor="w", pady=(8,0))
        tk.Label(rank_frame, text="Rank:", bg=CARD2, fg=TEXT3,
                font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Label(rank_frame, text=rank_text, bg=CARD2, fg=rank_color,
                font=("Segoe UI", 10, "bold")).pack(side="left", padx=(6,0))

        # ── GPA Comparison Visual (SEM1 vs SEM2) ──
        gpa1_str = sem_gpa.get("SEM1", "0")
        gpa2_str = sem_gpa.get("SEM2", "0")
        try:    gpa1_f = float(gpa1_str)
        except: gpa1_f = 0.0
        try:    gpa2_f = float(gpa2_str)
        except: gpa2_f = 0.0

        cmp_card, cmp_inner = make_card(self.rc_frame, CYAN)
        cmp_card.pack(fill="x", pady=(0,12), padx=2)

        tk.Label(cmp_inner, text="GPA COMPARISON — SEM 1  vs  SEM 2",
                bg=CARD, fg=TEXT3,
                font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,10))

        bars_row = tk.Frame(cmp_inner, bg=CARD)
        bars_row.pack(fill="x")

        max_gpa = 4.0
        for sem_lbl, gpa_f, color in [("SEM 1", gpa1_f, ACCENT), ("SEM 2", gpa2_f, GREEN)]:
            col = tk.Frame(bars_row, bg=CARD)
            col.pack(side="left", fill="both", expand=True, padx=(0,16))

            gpa_c = GREEN if gpa_f >= 3.0 else YELLOW if gpa_f >= 2.0 else RED
            tk.Label(col, text=sem_lbl, bg=CARD, fg=TEXT3,
                    font=("Segoe UI", 8, "bold")).pack(anchor="w")

            bar_outer = tk.Frame(col, bg=BORDER, height=22)
            bar_outer.pack(fill="x", pady=(4,4))
            bar_outer.pack_propagate(False)
            pct = min(gpa_f / max_gpa, 1.0)
            bar_inner_w = tk.Frame(bar_outer, bg=color, height=22)
            bar_inner_w.place(relx=0, rely=0, relwidth=pct, relheight=1)

            tk.Label(col, text=f"{gpa_f:.2f} / 4.00",
                    bg=CARD, fg=gpa_c,
                    font=("Courier New", 11, "bold")).pack(anchor="w")

        # GPA diff badge
        if gpa1_f > 0 or gpa2_f > 0:
            diff = gpa2_f - gpa1_f
            if abs(diff) >= 0.01:
                arrow   = "▲" if diff > 0 else "▼"
                d_clr   = GREEN if diff > 0 else RED
                d_bg    = _lighten(GREEN) if diff > 0 else _lighten(RED)
                msg     = f"Improved" if diff > 0 else "Dropped"
                d_text  = f"{arrow}  {msg} by {abs(diff):.2f} points (SEM1 → SEM2)"
            else:
                d_clr  = TEXT3
                d_bg   = BORDER
                d_text = "→  GPA same raha SEM1 aur SEM2 mein"

            diff_badge = tk.Frame(cmp_inner, bg=d_bg, padx=14, pady=7)
            diff_badge.pack(anchor="w", pady=(8,0))
            tk.Label(diff_badge, text=d_text,
                    bg=d_bg, fg=d_clr,
                    font=("Segoe UI", 10, "bold")).pack()

        # ── Per-semester sections ──
        sem_labels = {
            "SEM1": "Semester 1 — Fall 2025",
            "SEM2": "Semester 2 — Spring 2026"
        }
        sem_colors = {"SEM1": ACCENT, "SEM2": GREEN}
        prev_gpa   = None

        # Grade → GPA points map
        GRADE_POINTS = {
            "A+": 4.0, "A": 4.0, "B+": 3.5, "B": 3.0,
            "C+": 2.5, "C": 2.0, "D+": 1.5, "D": 1.0, "F": 0.0
        }

        for sem in ["SEM1", "SEM2"]:
            sem_card, sem_inner = make_card(self.rc_frame, sem_colors[sem])
            sem_card.pack(fill="x", pady=(0,12), padx=2)

            # Header row
            hdr = tk.Frame(sem_inner, bg=CARD)
            hdr.pack(fill="x", pady=(0,10))
            tk.Label(hdr, text=sem_labels[sem],
                    bg=CARD, fg=TEXT1,
                    font=("Segoe UI", 11, "bold")).pack(side="left")

            gpa_val_str = sem_gpa.get(sem, "—")
            try:
                gpa_val_f = float(gpa_val_str)
                gpa_c = GREEN if gpa_val_f>=3.0 else YELLOW if gpa_val_f>=2.0 else RED
            except:
                gpa_val_f = None
                gpa_c = TEXT3

            # GPA badge on right
            gpa_badge_bg = (_lighten(GREEN) if gpa_val_f and gpa_val_f>=3.0
                           else _lighten(YELLOW) if gpa_val_f and gpa_val_f>=2.0
                           else _lighten(RED)) if gpa_val_f is not None else BORDER
            gpa_badge = tk.Frame(hdr, bg=gpa_badge_bg, padx=10, pady=3)
            gpa_badge.pack(side="right")
            tk.Label(gpa_badge, text=f"GPA: {gpa_val_str}",
                    bg=gpa_badge_bg, fg=gpa_c,
                    font=("Courier New", 12, "bold")).pack()

            # Improvement indicator (SEM2 only)
            if sem == "SEM2" and prev_gpa is not None and gpa_val_f is not None:
                diff = gpa_val_f - prev_gpa
                if abs(diff) >= 0.01:
                    arrow  = "▲" if diff > 0 else "▼"
                    d_clr  = GREEN if diff > 0 else RED
                    d_text = f"{arrow} {abs(diff):.2f} from Sem 1"
                    tk.Label(hdr, text=d_text,
                            bg=CARD, fg=d_clr,
                            font=("Segoe UI", 9, "bold")).pack(side="right", padx=10)
                else:
                    tk.Label(hdr, text="→ Same as Sem 1",
                            bg=CARD, fg=TEXT3,
                            font=("Segoe UI", 9)).pack(side="right", padx=10)

            if gpa_val_f is not None:
                prev_gpa = gpa_val_f

            # Subject marks table — with Grade Points column
            cols   = ["Code","Course Name","Cr","Q1","Q2","Mid","Final","Asgn","Total","Grade","%","GP"]
            widths = [65, 195, 32, 38, 38, 50, 55, 50, 55, 58, 46, 46]
            tree   = make_tree(sem_inner, cols, widths, height=max(len(sem_marks[sem]), 3))

            total_credits = 0
            for m in sem_marks[sem]:
                if len(m) < 11: continue
                grade = m[9]
                color = GRADE_COLORS.get(grade, TEXT2)
                gp    = GRADE_POINTS.get(grade, 0.0)
                tree.insert("", "end", values=(
                    m[0], m[1], m[2],
                    m[3], m[4], m[5], m[6], m[7],
                    m[8], grade, m[10]+"%", f"{gp:.1f}"
                ), tags=(grade,))
                tree.tag_configure(grade, foreground=color)
                try: total_credits += int(m[2])
                except: pass

            # Per-subject GPA mini-bars
            if sem_marks[sem]:
                subj_gpa_frame = tk.Frame(sem_inner, bg=CARD)
                subj_gpa_frame.pack(fill="x", pady=(8,4))
                tk.Label(subj_gpa_frame, text="SUBJECT-WISE GRADE POINTS",
                        bg=CARD, fg=TEXT3,
                        font=("Segoe UI", 7, "bold")).pack(anchor="w", pady=(0,5))

                bars_f = tk.Frame(subj_gpa_frame, bg=CARD)
                bars_f.pack(fill="x")

                for m in sem_marks[sem]:
                    if len(m) < 11: continue
                    grade = m[9]
                    gp    = GRADE_POINTS.get(grade, 0.0)
                    color = GRADE_COLORS.get(grade, TEXT2)
                    code  = m[0][:7]  # short code

                    row_f = tk.Frame(bars_f, bg=CARD)
                    row_f.pack(fill="x", pady=2)

                    tk.Label(row_f, text=code, bg=CARD, fg=TEXT2,
                            font=("Segoe UI", 8, "bold"), width=9,
                            anchor="w").pack(side="left")

                    bar_o = tk.Frame(row_f, bg=BORDER, height=14)
                    bar_o.pack(side="left", fill="x", expand=True, padx=(4,8))
                    bar_o.pack_propagate(False)
                    bar_i = tk.Frame(bar_o, bg=color, height=14)
                    bar_i.place(relx=0, rely=0, relwidth=gp/4.0, relheight=1)

                    tk.Label(row_f, text=f"{gp:.1f}  {grade}",
                            bg=CARD, fg=color,
                            font=("Courier New", 8, "bold"), width=9,
                            anchor="e").pack(side="left")

            # Credits + pass/fail summary
            bot_row = tk.Frame(sem_inner, bg=CARD)
            bot_row.pack(fill="x", pady=(6,0))
            passed_sub = sum(1 for m in sem_marks[sem] if len(m)>=11 and m[9]!="F")
            total_sub  = len(sem_marks[sem])
            tk.Label(bot_row,
                    text=f"Passed: {passed_sub}/{total_sub} subjects  |  Total Credits: {total_credits}",
                    bg=CARD, fg=TEXT2,
                    font=("Segoe UI", 9)).pack(anchor="e")

    # ══════════════════════════════════════
    # PAGE 5: ANALYTICS  (IMPROVED QUALITY)
    # ══════════════════════════════════════
    def _build_analytics(self):
        page = tk.Frame(self.content, bg=BG)
        self.pages["analytics"] = page

        canvas = tk.Canvas(page, bg=BG, highlightthickness=0)
        vscroll = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        scroll_frame = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(win_id, width=e.width))

        def _mw(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _mw)

        top = tk.Frame(scroll_frame, bg=BG)
        top.pack(fill="x", pady=(0,14))

        tk.Label(top, text="Semester:",
                bg=BG, fg=TEXT2,
                font=("Segoe UI", 10)).pack(side="left")
        self.an_sem = tk.StringVar(value="SEM2")
        ttk.Combobox(top, textvariable=self.an_sem,
                     values=["SEM1","SEM2","Both"],
                     state="readonly", width=10,
                     font=("Segoe UI",10)).pack(side="left", padx=8, ipady=4)
        btn(top, "📊  Generate", ACCENT, self._load_analytics)

        self.an_frame = tk.Frame(scroll_frame, bg=BG)
        self.an_frame.pack(fill="both", expand=True)

    def _load_analytics(self):
        for w in self.an_frame.winfo_children():
            w.destroy()

        selected_sem = self.an_sem.get()
        out      = cpp("GET_STUDENTS")
        students = []
        for line in parse_lines(out):
            parts = line.split("|")
            if len(parts) >= 6:
                roll = parts[0]
                name = parts[1]
                gpa_out = cpp("GET_GPA", roll)
                gpas    = gpa_out.split("|") if gpa_out else ["0","0","0"]
                try:
                    sem1_gpa = float(gpas[0]) if len(gpas) > 0 and gpas[0] else 0.0
                except:
                    sem1_gpa = 0.0
                try:
                    sem2_gpa = float(gpas[1]) if len(gpas) > 1 and gpas[1] else 0.0
                except:
                    sem2_gpa = 0.0
                try:
                    cgpa_val = float(gpas[2]) if len(gpas) > 2 and gpas[2] else 0.0
                except:
                    cgpa_val = 0.0
                if selected_sem == "SEM1":
                    value = sem1_gpa
                elif selected_sem == "SEM2":
                    value = sem2_gpa
                else:
                    value = cgpa_val
                students.append({
                    "roll": roll,
                    "name": name,
                    "sem1": sem1_gpa,
                    "sem2": sem2_gpa,
                    "cgpa": cgpa_val,
                    "value": value
                })

        # ── Row 1: Distribution + Top 10 bar ──
        row1 = tk.Frame(self.an_frame, bg=BG)
        row1.pack(fill="both", expand=True, pady=(0,10))

        title1 = "CGPA DISTRIBUTION" if selected_sem == "Both" else f"{selected_sem} GPA DISTRIBUTION"
        c1, i1 = make_card(row1, ACCENT)
        c1.pack(side="left", fill="both", expand=True, padx=(0,10))
        tk.Label(i1, text=title1,
                bg=CARD, fg=TEXT3,
                font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,8))
        ranges = {"4.0":0,"3.5-3.9":0,"3.0-3.4":0,"2.5-2.9":0,"2.0-2.4":0,"<2.0":0}
        for s in students:
            c = s["value"]
            if c >= 4.0:   ranges["4.0"]     += 1
            elif c >= 3.5: ranges["3.5-3.9"] += 1
            elif c >= 3.0: ranges["3.0-3.4"] += 1
            elif c >= 2.5: ranges["2.5-2.9"] += 1
            elif c >= 2.0: ranges["2.0-2.4"] += 1
            else:          ranges["<2.0"]    += 1
        g1 = BarGraph(i1, ranges,
                     [ACCENT, GREEN, CYAN, YELLOW, PURPLE, RED], height=260)
        g1.pack(fill="both", expand=True)
        g1.after(50, g1._draw)
        g1._draw()

        c2, i2 = make_card(row1, GREEN)
        c2.pack(side="left", fill="both", expand=True)
        title2 = "TOP 10 STUDENTS (CGPA)" if selected_sem == "Both" else f"TOP 10 STUDENTS ({selected_sem})"
        tk.Label(i2, text=title2,
                bg=CARD, fg=TEXT3,
                font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,8))
        top10 = sorted([s for s in students if s["value"] > 0], key=lambda x: x["value"], reverse=True)[:10]
        top_data = {f"{i+1}. {s['name'].split()[0]}": s["value"] for i, s in enumerate(top10)}
        top_clrs = [GREEN if s["roll"] == "2025-BSCPE-19" else ACCENT for s in top10]
        if top_data:
            g2 = BarGraph(i2, top_data, top_clrs, height=260)
            g2.pack(fill="both", expand=True)
            g2.after(50, g2._draw)
            g2._draw()
        else:
            tk.Label(i2, text="No data available for this semester.",
                    bg=CARD, fg=TEXT3,
                    font=("Segoe UI", 10)).pack(pady=20)

        # ── Row 2: Subject averages + Pass/Fail pie ──
        row2 = tk.Frame(self.an_frame, bg=BG)
        row2.pack(fill="both", expand=True)

        stats_out = cpp("GET_STATS")
        sub_data  = {}
        for line in parse_lines(stats_out):
            if line.startswith("SUB:"):
                parts = line.split(":")
                if len(parts) >= 3:
                    try:
                        sub_data[parts[1]] = float(parts[2])
                    except:
                        sub_data[parts[1]] = 0.0

        c3, i3 = make_card(row2, YELLOW)
        c3.pack(side="left", fill="both", expand=True, padx=(0,10))
        tk.Label(i3, text="SUBJECT AVERAGES",
                bg=CARD, fg=TEXT3,
                font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,8))
        if sub_data:
            g3 = BarGraph(i3, sub_data,
                         [ACCENT, GREEN, YELLOW, PURPLE, CYAN, PINK], height=260)
            g3.pack(fill="both", expand=True)
            g3.after(50, g3._draw)
            g3._draw()
        else:
            tk.Label(i3, text="Subject average data unavailable.",
                    bg=CARD, fg=TEXT3,
                    font=("Segoe UI", 10)).pack(pady=20)

        c4, i4 = make_card(row2, RED)
        c4.pack(side="left", fill="both", expand=True)
        tk.Label(i4, text="PASS / FAIL RATIO",
                bg=CARD, fg=TEXT3,
                font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,8))
        passing = sum(1 for s in students if s["value"] >= 2.0)
        failing = len([s for s in students if s["value"] > 0]) - passing
        pie_data = {
            "Pass": (passing, GREEN),
            "Fail": (failing, RED)
        }
        g4 = PieChart(i4, pie_data)
        g4.pack(fill="both", expand=True)
        g4.after(50, g4._draw)
        g4._draw()

        # ── Data summary table ──
        summary_card, summary_inner = make_card(self.an_frame, ACCENT2)
        summary_card.pack(fill="both", expand=True, pady=(10,0))
        tk.Label(summary_inner, text="ANALYTICS DATA SUMMARY",
                bg=CARD, fg=TEXT3,
                font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,8))
        summary_cols = ["Metric","Value"]
        summary_widths = [260, 220]
        summary_table = make_tree(summary_inner, summary_cols, summary_widths, height=7)
        summary_rows = [
            ("Semester", selected_sem),
            ("Students analyzed", str(len([s for s in students if s["value"] > 0]))),
            ("Top GPA value", f"{top10[0]['value']:.2f}" if top10 else "—"),
            ("Pass count", str(passing)),
            ("Fail count", str(failing)),
        ]
        fill_tree(summary_table, summary_rows)

    # ══════════════════════════════════════
    # PAGE 6: ADD STUDENT
    # ══════════════════════════════════════
    def _build_add_student(self):
        page = tk.Frame(self.content, bg=BG)
        self.pages["add_student"] = page

        card, inner = make_card(page, ACCENT)
        card.pack(anchor="nw", padx=0, pady=0, ipadx=10)

        tk.Label(inner, text="ADD NEW STUDENT",
                bg=CARD, fg=TEXT3,
                font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,14))

        grid = tk.Frame(inner, bg=CARD)
        grid.pack(fill="x")

        def cell(parent, row, col):
            f = tk.Frame(parent, bg=CARD)
            f.grid(row=row, column=col, padx=(0,20), pady=4, sticky="w")
            return f

        def lbl(f, text):
            tk.Label(f, text=text, bg=CARD, fg=TEXT3,
                    font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,4))

        def ent(f, w=22):
            e = tk.Entry(f, bg=INPUT, fg=TEXT1,
                        insertbackground=TEXT1,
                        font=("Segoe UI", 10), bd=0, width=w)
            e.pack(ipady=7, ipadx=8)
            return e

        c1 = cell(grid,0,0); lbl(c1,"Roll Number")
        self.add_roll = ent(c1)
        self.add_roll.insert(0, "2025-BSCPE-41")

        c2 = cell(grid,0,1); lbl(c2,"Full Name")
        self.add_name = ent(c2, 28)

        c3 = cell(grid,0,2); lbl(c3,"Gender")
        self.add_gender = tk.StringVar(value="Male")
        ttk.Combobox(c3, textvariable=self.add_gender,
                    values=["Male","Female"],
                    state="readonly", width=12,
                    font=("Segoe UI",10)).pack(ipady=4)

        c4 = cell(grid,1,0); lbl(c4,"CNIC")
        self.add_cnic = ent(c4)

        c5 = cell(grid,1,1); lbl(c5,"Contact")
        self.add_contact = ent(c5)

        c6 = cell(grid,1,2); lbl(c6,"Father's Name")
        self.add_father = ent(c6, 28)

        row_btns = tk.Frame(inner, bg=CARD)
        row_btns.pack(fill="x", pady=(20,0))
        btn(row_btns, "➕  Add Student", GREEN, self._submit_add)
        btn(row_btns, "Clear", RED,
           lambda: [e.delete(0,"end") for e in
                   [self.add_roll, self.add_name,
                    self.add_cnic, self.add_contact,
                    self.add_father]])

    def _submit_add(self):
        roll    = self.add_roll.get().strip()
        name    = self.add_name.get().strip()
        gender  = self.add_gender.get()
        cnic    = self.add_cnic.get().strip()
        contact = self.add_contact.get().strip()
        father  = self.add_father.get().strip()

        if not roll or not name:
            toast(self.root, "Roll number and name are required!", False)
            return

        out = cpp("ADD_STUDENT", roll, name, gender,
                 cnic or "—", contact or "—", father or "—")
        if "OK" in out:
            toast(self.root, f"Student '{name}' added successfully! ✅")
        else:
            toast(self.root, "Error! Check roll number.", False)

    # ══════════════════════════════════════
    # PAGE 7: COURSES  (IMPROVED + SEM3)
    # ══════════════════════════════════════
    def _build_courses(self):
        page = tk.Frame(self.content, bg=BG)
        self.pages["courses"] = page

        # Scrollable canvas for all semesters
        canvas = tk.Canvas(page, bg=BG, highlightthickness=0)
        vscroll = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        scroll_frame = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(win_id, width=e.width))

        def _mw(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _mw)

        self._sem_trees = {}
        self._sem_fields = {}
        self._sem_credit_labels = {}

        sem_defs = [
            ("SEM1", "📚 Semester 1 — Fall 2025",   ACCENT),
            ("SEM2", "📚 Semester 2 — Spring 2026",  GREEN),
            ("SEM3", "📚 Semester 3 — Fall 2026",    YELLOW),
            ("SEM4", "📚 Semester 4 — Future",       PURPLE),
            ("SEM5", "📚 Semester 5 — Future",       CYAN),
            ("SEM6", "📚 Semester 6 — Future",       PINK),
            ("SEM7", "📚 Semester 7 — Future",       ACCENT2),
            ("SEM8", "📚 Semester 8 — Future",       BORDER),
        ]

        editable_semesters = {"SEM3", "SEM4", "SEM5", "SEM6", "SEM7", "SEM8"}

        def make_add_field(parent, lbl_text, w=12):
            f = tk.Frame(parent, bg=CARD2)
            f.pack(side="left", padx=(0,10))
            tk.Label(f, text=lbl_text, bg=CARD2, fg=TEXT3,
                    font=("Segoe UI", 7, "bold")).pack(anchor="w")
            e = tk.Entry(f, bg=INPUT, fg=TEXT1,
                        insertbackground=TEXT1,
                        font=("Segoe UI", 9), bd=0, width=w)
            e.pack(ipady=5, ipadx=4)
            return e

        for sem, label_text, color in sem_defs:
            card, inner = make_card(scroll_frame, color)
            card.pack(fill="x", pady=(0,14), padx=2)

            hdr_row = tk.Frame(inner, bg=CARD)
            hdr_row.pack(fill="x", pady=(0,10))
            tk.Label(hdr_row, text=label_text,
                    bg=CARD, fg=TEXT1,
                    font=("Segoe UI", 11, "bold")).pack(side="left")

            cols   = ["Code","Course Name","Theory Cr","Lab Cr","Total Cr","Teacher"]
            widths = [80, 240, 90, 70, 80, 200]
            tree   = make_tree(inner, cols, widths, height=6)

            if sem in editable_semesters:
                tree.config(height=8)
                self._sem_trees[sem] = tree
                self._load_sem_courses(sem, tree)

                add_frame = tk.Frame(inner, bg=CARD2)
                add_frame.pack(fill="x", pady=(10,4))
                tk.Frame(add_frame, bg=BORDER, height=1).pack(fill="x")
                ctl = tk.Frame(add_frame, bg=CARD2)
                ctl.pack(fill="x", padx=6, pady=8)

                tk.Label(ctl, text=f"ADD COURSE TO {sem}",
                        bg=CARD2, fg=TEXT1,
                        font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,6))

                fields_row = tk.Frame(ctl, bg=CARD2)
                fields_row.pack(fill="x")

                self._sem_fields[sem] = {
                    "code":    make_add_field(fields_row, "Code",        8),
                    "name":    make_add_field(fields_row, "Course Name", 20),
                    "th":      make_add_field(fields_row, "Theory Cr",   5),
                    "lab":     make_add_field(fields_row, "Lab Cr",      5),
                    "teacher": make_add_field(fields_row, "Teacher",     18),
                }

                self._sem_credit_labels[sem] = tk.Label(ctl, text="",
                                                      bg=CARD2, fg=CYAN,
                                                      font=("Segoe UI", 9, "bold"))
                self._sem_credit_labels[sem].pack(anchor="w", pady=(6,0))
                self._update_sem_credits(sem)

                btns_row = tk.Frame(ctl, bg=CARD2)
                btns_row.pack(fill="x", pady=(8,0))
                btn(btns_row, "➕ Add Course",   GREEN,
                    lambda sem=sem: self._add_sem_course(sem))
                btn(btns_row, "🗑 Remove Selected", RED,
                    lambda sem=sem: self._remove_sem_course(sem))

            else:
                try:
                    with open(os.path.join(BASE_DIR,"data","courses.txt")) as f:
                        total_cr = 0
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith("#"): continue
                            parts = line.split("|")
                            if len(parts) < 6: continue
                            if parts[0] != sem: continue
                            th  = int(parts[3])
                            lab = int(parts[4])
                            total_cr += th + lab
                            tree.insert("", "end", values=(
                                parts[1], parts[2],
                                parts[3], parts[4],
                                th+lab,   parts[5]
                            ))
                        tk.Label(inner,
                                text=f"Total Credits: {total_cr}",
                                bg=CARD, fg=TEXT2,
                                font=("Segoe UI", 9, "bold")
                                ).pack(anchor="e", pady=(8,0))
                except Exception as ex:
                    tk.Label(inner, text=f"Error: {ex}",
                            bg=CARD, fg=RED).pack()

    def _load_sem_courses(self, sem, tree=None):
        if tree is None:
            tree = self._sem_trees.get(sem)
        if tree is None:
            return
        tree.delete(*tree.get_children())
        try:
            with open(os.path.join(BASE_DIR,"data","courses.txt")) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"): continue
                    parts = line.split("|")
                    if len(parts) < 6 or parts[0] != sem: continue
                    th  = int(parts[3])
                    lab = int(parts[4])
                    tree.insert("", "end", values=(
                        parts[1], parts[2],
                        parts[3], parts[4],
                        th+lab,   parts[5]
                    ))
        except:
            pass

    def _get_sem_total_credits(self, sem):
        total = 0
        try:
            with open(os.path.join(BASE_DIR,"data","courses.txt")) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"): continue
                    parts = line.split("|")
                    if len(parts) < 6 or parts[0] != sem: continue
                    total += int(parts[3]) + int(parts[4])
        except:
            pass
        return total

    def _get_sem_course_count(self, sem):
        count = 0
        try:
            with open(os.path.join(BASE_DIR,"data","courses.txt")) as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) >= 2 and parts[0] == sem:
                        count += 1
        except:
            pass
        return count

    def _update_sem_credits(self, sem):
        total = self._get_sem_total_credits(sem)
        count = self._get_sem_course_count(sem)
        limit = SEM_LIMITS.get(sem, 22)
        remaining = limit - total
        color = RED if total > limit else YELLOW if total >= limit - 4 else CYAN
        lbl = self._sem_credit_labels.get(sem)
        if lbl:
            lbl.config(
                text=f"Credits used: {total}/{limit}  |  Courses: {count}  |  "
                     f"Remaining: {max(0,remaining)} credits",
                fg=color)

    def _add_sem_course(self, sem):
        fields = self._sem_fields.get(sem)
        if not fields:
            return

        code    = fields["code"].get().strip().upper()
        name    = fields["name"].get().strip()
        teacher = fields["teacher"].get().strip()

        try:
            th  = int(fields["th"].get().strip() or 0)
            lab = int(fields["lab"].get().strip() or 0)
        except:
            toast(self.root, "Credits must be numeric!", False)
            return

        if not code or not name:
            toast(self.root, "Course code and name are required!", False)
            return

        current_cr = self._get_sem_total_credits(sem)
        limit = SEM_LIMITS.get(sem, 22)
        if current_cr + th + lab > limit:
            toast(self.root,
                 f"Credit limit will be exceeded! ({current_cr}+{th+lab}={current_cr+th+lab})",
                 False)
            return

        line = f"\n{sem}|{code}|{name}|{th}|{lab}|{teacher or '—'}"
        try:
            with open(os.path.join(BASE_DIR,"data","courses.txt"), "a") as f:
                f.write(line)
            self._load_sem_courses(sem)
            self._update_sem_credits(sem)
            for e in fields.values():
                e.delete(0,"end")
            toast(self.root, f"Course '{name}' added to {sem}! ✅")
        except Exception as ex:
            toast(self.root, f"File error: {ex}", False)

    def _remove_sem_course(self, sem):
        tree = self._sem_trees.get(sem)
        if tree is None:
            return

        sel = tree.selection()
        if not sel:
            toast(self.root, "Please select a course first!", False)
            return

        code = tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirm",
            f"Remove '{code}' from {sem}?"):
            return

        try:
            path  = os.path.join(BASE_DIR,"data","courses.txt")
            with open(path) as f:
                lines = f.readlines()
            with open(path, "w") as f:
                for line in lines:
                    parts = line.strip().split("|")
                    if len(parts) >= 2 and parts[0] == sem and parts[1] == str(code):
                        continue
                    f.write(line)
            self._load_sem_courses(sem)
            self._update_sem_credits(sem)
            toast(self.root, f"Course '{code}' removed successfully! ✅")
        except Exception as ex:
            toast(self.root, f"Error: {ex}", False)


# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = App(root)
    root.mainloop()