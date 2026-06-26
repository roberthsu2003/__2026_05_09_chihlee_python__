from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

import pandas as pd


SUBJECT_COLUMNS = ["語文", "數學", "英語", "物理", "化學"]
BIN_LABELS = ["0-59", "60-69", "70-79", "80-89", "90-100"]


class ScoreData:
    def __init__(self, path: Path | None = None) -> None:
        self.df = self._load_data(path or Path(__file__).with_name("考試分數_3年6班.csv"))

    @staticmethod
    def _load_data(csv_path: Path) -> pd.DataFrame:
        try:
            df = pd.read_csv(csv_path)
        except Exception as exc:
            messagebox.showerror("讀取失敗", f"無法讀取資料檔：\n{csv_path}\n\n{exc}")
            raise

        required = ["學生姓名", *SUBJECT_COLUMNS]
        missing = [col for col in required if col not in df.columns]
        if missing:
            messagebox.showerror("欄位錯誤", f"CSV 缺少必要欄位：{', '.join(missing)}")
            raise ValueError("CSV 欄位不完整")

        return df

    def get_series(self, subject: str) -> tuple[pd.Series, str]:
        if subject == "全科平均":
            return self.df[SUBJECT_COLUMNS].mean(axis=1), subject
        return self.df[subject].astype(float), subject


@dataclass
class ScoreStats:
    count: int
    mean: float
    median: float
    std: float
    max_score: float
    min_score: float
    pass_rate: float


class ScoreAnalyzer:
    @staticmethod
    def compute_stats(series: pd.Series) -> ScoreStats:
        return ScoreStats(
            count=len(series),
            mean=series.mean(),
            median=series.median(),
            std=series.std(ddof=0),
            max_score=series.max(),
            min_score=series.min(),
            pass_rate=(series >= 60).sum() / len(series) * 100,
        )

    @staticmethod
    def count_bins(series: pd.Series) -> list[int]:
        counts = [0, 0, 0, 0, 0]
        for value in series:
            if value < 60:
                counts[0] += 1
            elif value < 70:
                counts[1] += 1
            elif value < 80:
                counts[2] += 1
            elif value < 90:
                counts[3] += 1
            else:
                counts[4] += 1
        return counts

    @staticmethod
    def rank_students(names: pd.Series, scores: pd.Series) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
        ranking = pd.DataFrame({"name": names, "score": scores})
        top = ranking.sort_values("score", ascending=False).head(3)
        bottom = ranking.sort_values("score", ascending=True).head(3)
        top_list = [(row["name"], row["score"]) for _, row in top.iterrows()]
        bottom_list = [(row["name"], row["score"]) for _, row in bottom.iterrows()]
        return top_list, bottom_list


class BarChartRenderer:
    def __init__(self, canvas: tk.Canvas, colors: dict[str, str]) -> None:
        self.canvas = canvas
        self.colors = colors

    def draw(self, series: pd.Series, subject: str) -> None:
        canvas = self.canvas
        canvas.delete("all")

        width = max(canvas.winfo_width(), 600)
        height = max(canvas.winfo_height(), 420)

        left_pad, right_pad = 64, 28
        top_pad, bottom_pad = 46, 74

        plot_w = width - left_pad - right_pad
        plot_h = height - top_pad - bottom_pad
        if plot_w <= 0 or plot_h <= 0:
            return

        bins = ScoreAnalyzer.count_bins(series)
        max_count = max(max(bins), 1)

        x0 = left_pad
        y0 = height - bottom_pad
        x1 = width - right_pad
        y1 = top_pad

        canvas.create_rectangle(0, 0, width, height, fill="#fcfdff", outline="")
        canvas.create_line(x0, y0, x1, y0, width=2, fill="#475569")
        canvas.create_line(x0, y0, x0, y1, width=2, fill="#475569")

        step = 1 if max_count <= 8 else 2 if max_count <= 16 else 5
        y_ticks = list(range(0, max_count + 1, step))
        if y_ticks[-1] != max_count:
            y_ticks.append(max_count)

        for tick in y_ticks:
            y = y0 - (tick / max_count) * plot_h
            canvas.create_line(x0 - 6, y, x0, y, fill="#64748b")
            canvas.create_text(x0 - 24, y, text=str(tick), fill="#475569", font=("PingFang TC", 10))
            if tick > 0:
                canvas.create_line(x0, y, x1, y, fill=self.colors["grid"])

        slot_w = plot_w / len(BIN_LABELS)
        bar_w = slot_w * 0.62

        for idx, (label, count) in enumerate(zip(BIN_LABELS, bins)):
            center_x = x0 + slot_w * (idx + 0.5)
            bar_h = (count / max_count) * plot_h
            bx0 = center_x - bar_w / 2
            by0 = y0 - bar_h
            bx1 = center_x + bar_w / 2
            by1 = y0

            fill_color = self.colors["bar"] if idx % 2 == 0 else self.colors["bar_alt"]
            canvas.create_rectangle(bx0, by0, bx1, by1, fill=fill_color, outline="")
            canvas.create_text(center_x, by0 - 12, text=f"{count} 人", fill="#0f172a", font=("PingFang TC", 10, "bold"))
            canvas.create_text(center_x, y0 + 20, text=label, fill="#334155", font=("PingFang TC", 11, "bold"))

        canvas.create_text(width / 2, 20, text=f"{subject} 分數分布", fill="#0f172a", font=("PingFang TC", 16, "bold"))
        canvas.create_text(width / 2, height - 30, text="分數區間", fill="#475569", font=("PingFang TC", 11))
        canvas.create_text(20, height / 2, text="人數", angle=90, fill="#475569", font=("PingFang TC", 11))


class ScoreDistributionApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("分數分布分析儀表板")
        self.root.geometry("1120x700")
        self.root.minsize(960, 620)

        self.data = ScoreData()
        self.analyzer = ScoreAnalyzer()

        self.selected_subject = tk.StringVar(value="全科平均")
        self.summary_var = tk.StringVar(value="")
        self.top3_var = tk.StringVar(value="")
        self.bottom3_var = tk.StringVar(value="")

        self._configure_style()
        self._build_ui()
        self.update_dashboard()

    def _configure_style(self) -> None:
        self.colors = {
            "bg": "#f4f7fb",
            "panel": "#ffffff",
            "title": "#0f172a",
            "text": "#334155",
            "muted": "#64748b",
            "accent": "#0ea5e9",
            "accent_dark": "#0284c7",
            "grid": "#dbeafe",
            "bar": "#38bdf8",
            "bar_alt": "#7dd3fc",
            "ok": "#16a34a",
        }
        self.root.configure(bg=self.colors["bg"])

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Modern.TCombobox",
            fieldbackground="#ffffff",
            background="#ffffff",
            bordercolor="#cbd5e1",
            lightcolor="#cbd5e1",
            darkcolor="#cbd5e1",
            padding=6,
            arrowsize=14,
        )

    def _build_ui(self) -> None:
        outer = tk.Frame(self.root, bg=self.colors["bg"], padx=18, pady=18)
        outer.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(outer, bg=self.colors["panel"], padx=16, pady=12)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="班級分數分布分析",
            bg=self.colors["panel"],
            fg=self.colors["title"],
            font=("PingFang TC", 21, "bold"),
        ).pack(side=tk.LEFT)

        control_wrap = tk.Frame(header, bg=self.colors["panel"])
        control_wrap.pack(side=tk.RIGHT)

        tk.Label(
            control_wrap,
            text="分析科目",
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            font=("PingFang TC", 11, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 8))

        subject_box = ttk.Combobox(
            control_wrap,
            textvariable=self.selected_subject,
            values=["全科平均", *SUBJECT_COLUMNS],
            state="readonly",
            width=12,
            style="Modern.TCombobox",
            font=("PingFang TC", 12),
        )
        subject_box.pack(side=tk.LEFT)
        subject_box.bind("<<ComboboxSelected>>", lambda _event: self.update_dashboard())

        body = tk.Frame(outer, bg=self.colors["bg"])
        body.pack(fill=tk.BOTH, expand=True, pady=(14, 0))

        left = tk.Frame(body, bg=self.colors["bg"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = tk.Frame(body, bg=self.colors["bg"], width=330)
        right.pack(side=tk.LEFT, fill=tk.Y, padx=(14, 0))
        right.pack_propagate(False)

        self.chart_card = tk.Frame(left, bg=self.colors["panel"], padx=14, pady=14)
        self.chart_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            self.chart_card,
            textvariable=self.summary_var,
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("PingFang TC", 12),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 8))

        self.chart_canvas = tk.Canvas(self.chart_card, bg="#fcfdff", highlightthickness=0)
        self.chart_canvas.pack(fill=tk.BOTH, expand=True)
        self.chart_canvas.bind("<Configure>", lambda _event: self.update_dashboard())

        self.chart_renderer = BarChartRenderer(self.chart_canvas, self.colors)

        stats_card = tk.Frame(right, bg=self.colors["panel"], padx=12, pady=12)
        stats_card.pack(fill=tk.X)

        tk.Label(
            stats_card,
            text="關鍵統計",
            bg=self.colors["panel"],
            fg=self.colors["title"],
            font=("PingFang TC", 13, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        self.stats_grid = tk.Frame(stats_card, bg=self.colors["panel"])
        self.stats_grid.pack(fill=tk.X)

        self.stat_vars: dict[str, tk.StringVar] = {}
        stat_items = [
            ("樣本數", "count"),
            ("平均", "mean"),
            ("中位數", "median"),
            ("標準差", "std"),
            ("最高分", "max"),
            ("最低分", "min"),
            ("及格率", "pass"),
        ]

        for row, (label, key) in enumerate(stat_items):
            tk.Label(
                self.stats_grid,
                text=label,
                bg=self.colors["panel"],
                fg=self.colors["muted"],
                font=("PingFang TC", 11),
            ).grid(row=row, column=0, sticky="w", pady=2)

            var = tk.StringVar(value="-")
            tk.Label(
                self.stats_grid,
                textvariable=var,
                bg=self.colors["panel"],
                fg=self.colors["text"],
                font=("PingFang TC", 11, "bold"),
            ).grid(row=row, column=1, sticky="e", pady=2)
            self.stat_vars[key] = var

        rank_card = tk.Frame(right, bg=self.colors["panel"], padx=12, pady=12)
        rank_card.pack(fill=tk.BOTH, expand=True, pady=(14, 0))

        tk.Label(
            rank_card,
            text="排名觀察",
            bg=self.colors["panel"],
            fg=self.colors["title"],
            font=("PingFang TC", 13, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(
            rank_card,
            text="前 3 名",
            bg=self.colors["panel"],
            fg=self.colors["ok"],
            font=("PingFang TC", 11, "bold"),
        ).pack(anchor="w")
        tk.Label(
            rank_card,
            textvariable=self.top3_var,
            justify=tk.LEFT,
            anchor="w",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("PingFang TC", 11),
        ).pack(fill=tk.X, pady=(2, 10))

        tk.Label(
            rank_card,
            text="後 3 名",
            bg=self.colors["panel"],
            fg="#ef4444",
            font=("PingFang TC", 11, "bold"),
        ).pack(anchor="w")
        tk.Label(
            rank_card,
            textvariable=self.bottom3_var,
            justify=tk.LEFT,
            anchor="w",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("PingFang TC", 11),
        ).pack(fill=tk.X, pady=(2, 0))

    def update_dashboard(self) -> None:
        series, subject = self.data.get_series(self.selected_subject.get())
        stats = self.analyzer.compute_stats(series)

        self.summary_var.set(
            f"分析項目：{subject}    全班平均：{stats.mean:.1f}    中位數：{stats.median:.1f}"
        )

        self.stat_vars["count"].set(str(stats.count))
        self.stat_vars["mean"].set(f"{stats.mean:.1f}")
        self.stat_vars["median"].set(f"{stats.median:.1f}")
        self.stat_vars["std"].set(f"{stats.std:.2f}")
        self.stat_vars["max"].set(f"{stats.max_score:.0f}")
        self.stat_vars["min"].set(f"{stats.min_score:.0f}")
        self.stat_vars["pass"].set(f"{stats.pass_rate:.1f}%")

        top3, bottom3 = self.analyzer.rank_students(self.data.df["學生姓名"], series)
        top_lines = [f"{i + 1}. {name}  {score:.1f}" for i, (name, score) in enumerate(top3)]
        bottom_lines = [f"{i + 1}. {name}  {score:.1f}" for i, (name, score) in enumerate(bottom3)]
        self.top3_var.set("\n".join(top_lines))
        self.bottom3_var.set("\n".join(bottom_lines))

        self.chart_renderer.draw(series, subject)


def main() -> None:
    root = tk.Tk()
    ScoreDistributionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
