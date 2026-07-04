"""
台股相關係數分析工具
- 使用 twstock 取得全台灣上市櫃股票代碼
- 搜尋結果列表，每一筆都有「加入」按鈕
- 可選最多 4 檔，選完自動分析
"""

import sys
import yfinance as yf
import pandas as pd
import numpy as np
import twstock
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QFrame, QScrollArea, QListWidget,
    QListWidgetItem, QSizePolicy, QMessageBox, QProgressBar,
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QColor

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'Microsoft JhengHei', 'Noto Sans TC', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

QSS = """
QMainWindow { background-color: #0b0b10; }
QWidget#central { background-color: #0b0b10; }
QLabel {
    color: #e0e0ea;
    font-family: ".AppleSystemUIFont", "Helvetica Neue", Arial, sans-serif;
}
QLabel#title {
    font-size: 24px; font-weight: 700; color: #ffffff; letter-spacing: 0.5px;
}
QLabel#subtitle {
    font-size: 13px; color: #88889a;
}
QLabel#status {
    font-size: 13px; color: #88889a; padding: 4px 0;
}
QLabel#section {
    font-size: 14px; font-weight: 600; color: #c8c8d8;
}
QLabel#chip-text {
    color: #d8d0ea; font-size: 13px; font-weight: 500;
}
QLabel#hint {
    color: #5a5a6e; font-size: 14px;
}
QLineEdit {
    background-color: #181822; color: #e0e0ea;
    border: 1px solid #28283a; border-radius: 10px;
    padding: 12px 16px; font-size: 14px;
    font-family: ".AppleSystemUIFont", "Helvetica Neue", Arial, sans-serif;
}
QLineEdit:focus {
    border: 1px solid #7c6cf7; background-color: #1c1c2a;
}
QPushButton {
    color: #ffffff; border: none; border-radius: 8px;
    padding: 8px 18px; font-size: 13px; font-weight: 600;
    font-family: ".AppleSystemUIFont", "Helvetica Neue", Arial, sans-serif;
}
QPushButton#add-btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6c5ce7, stop:1 #a29bfe);
}
QPushButton#add-btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c6cf7, stop:1 #b2abff);
}
QPushButton#add-btn:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5c4cd7, stop:1 #928bfe);
}
QPushButton#add-btn:disabled {
    background: #2a2a3a; color: #5a5a6e;
}
QPushButton#remove-btn {
    background: transparent; color: #7a6a9a; border: none;
    font-size: 14px; font-weight: bold; padding: 0;
}
QPushButton#remove-btn:hover { color: #ff5252; }
QPushButton#result-add {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6c5ce7, stop:1 #a29bfe);
    border-radius: 6px; padding: 6px 14px; font-size: 12px;
}
QPushButton#result-add:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c6cf7, stop:1 #b2abff);
}
QTableWidget {
    background-color: #14141c; color: #e0e0ea;
    border: 1px solid #22222e; border-radius: 10px;
    gridline-color: #22222e; font-size: 13px;
}
QTableWidget::item { padding: 10px 12px; border-bottom: 1px solid #1a1a26; }
QHeaderView::section {
    background-color: #1a1a26; color: #9a9ab0;
    padding: 10px 12px; border: none;
    font-size: 12px; font-weight: 600;
    border-bottom: 1px solid #22222e;
}
QFrame#card {
    background-color: #14141c; border: 1px solid #22222e; border-radius: 12px;
}
QFrame#chip {
    background-color: #26203a; border: 1px solid #3e3060;
    border-radius: 18px;
}
QFrame#result-item {
    background-color: #14141c; border-radius: 6px;
}
QFrame#result-item:hover {
    background-color: #1c1c2a;
}
QListWidget {
    background-color: #14141c; border: 1px solid #28283a;
    border-radius: 10px; outline: none;
}
QListWidget::item { padding: 0; border: none; }
QProgressBar {
    background-color: #1a1a26; border: none; border-radius: 4px; height: 6px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6c5ce7, stop:1 #a29bfe);
    border-radius: 4px;
}
QScrollBar:vertical {
    background: #14141c; width: 6px; border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #2a2a3e; border-radius: 3px; min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QWidget#search-wrapper {
    background-color: #14141c; border: 1px solid #28283a;
    border-radius: 12px;
}
"""


def load_stock_list():
    twstock.__update_codes()
    stocks = []
    for code, info in twstock.codes.items():
        if info.type == '股票' and info.name and info.market in ('上市', '上櫃'):
            suffix = '.TW' if info.market == '上市' else '.TWO'
            stocks.append({
                'code': code,
                'name': info.name,
                'market': info.market,
                'suffix': suffix,
            })
    stocks.sort(key=lambda x: (
        x['market'] != '上市',
        int(x['code']) if x['code'].isdigit() else 999999,
    ))
    return stocks


ALL_STOCKS = []


class FetchWorker(QThread):
    finished = Signal(pd.DataFrame, pd.DataFrame)
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, stocks):
        super().__init__()
        self.stocks = stocks

    def run(self):
        try:
            self.progress.emit(10)
            symbols = [s['code'] + s['suffix'] for s in self.stocks]
            self.progress.emit(20)
            data = yf.download(
                symbols, start="2026-01-01",
                interval="1d", auto_adjust=True, progress=False,
            )
            self.progress.emit(60)
            if data.empty:
                self.error.emit("無法取得股價資料")
                return
            close_raw = data.get("Close", data)
            if isinstance(close_raw, pd.Series):
                close_raw = close_raw.to_frame()
            name_map = {s['code'] + s['suffix']: s['name'] for s in self.stocks}
            close_renamed = close_raw.rename(columns=name_map)
            self.progress.emit(80)
            returns = close_renamed.pct_change().dropna()
            corr = returns.corr()
            self.progress.emit(100)
            self.finished.emit(corr, returns)
        except Exception as e:
            self.error.emit(f"資料失敗: {str(e)}")


class CorrHeatmap(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5.5, 4.2), dpi=120)
        self.fig.patch.set_facecolor("#14141c")
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.set_facecolor("#14141c")

    def update_heatmap(self, corr_df):
        self.ax.clear()
        self.ax.set_facecolor("#14141c")
        labels = corr_df.columns.tolist()
        data = corr_df.values
        norm = matplotlib.colors.Normalize(vmin=-1, vmax=1)
        cmap = matplotlib.colormaps["RdYlBu_r"]

        im = self.ax.imshow(data, cmap=cmap, norm=norm, aspect="equal")
        self.ax.set_xticks(range(len(labels)))
        self.ax.set_yticks(range(len(labels)))
        self.ax.set_xticklabels(labels, fontsize=9, color="#9a9ab0")
        self.ax.set_yticklabels(labels, fontsize=9, color="#9a9ab0")

        cbar = self.fig.colorbar(im, ax=self.ax, shrink=0.8, pad=0.02,
                                 ticks=[-1.0, -0.5, 0, 0.5, 1.0])
        cbar.ax.yaxis.set_tick_params(color="#9a9ab0")
        for t in cbar.ax.yaxis.get_ticklabels():
            t.set_color("#9a9ab0")

        for (i, j), val in np.ndenumerate(data):
            text_color = "white" if abs(val) < 0.5 else "black"
            self.ax.text(j, i, f"{val:.3f}", ha="center", va="center",
                         fontsize=10, fontweight="bold", color=text_color)

        self.ax.tick_params(colors="#9a9ab0", length=0)
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.fig.tight_layout()
        self.draw()

    def clear_chart(self):
        self.ax.clear()
        self.ax.set_facecolor("#14141c")
        self.ax.text(0.5, 0.5, "請選擇 2 ~ 4 檔股票",
                     ha="center", va="center", fontsize=14, color="#5a5a6e")
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.draw()


class SearchResultItem(QFrame):
    added = Signal(dict)

    def __init__(self, stock):
        super().__init__()
        self.stock = stock
        self.setObjectName("result-item")
        self.setStyleSheet("QFrame#result-item { background-color: transparent; }")
        self.setFixedHeight(44)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 4, 10, 4)
        layout.setSpacing(10)

        code_label = QLabel(stock['code'])
        code_label.setStyleSheet("color: #7c6cf7; font-size: 13px; font-weight: 700;")
        code_label.setFixedWidth(55)
        layout.addWidget(code_label)

        name_label = QLabel(stock['name'])
        name_label.setStyleSheet("color: #e0e0ea; font-size: 13px;")
        layout.addWidget(name_label)

        market_label = QLabel(stock['market'])
        market_label.setStyleSheet("color: #6a6a80; font-size: 11px;")
        market_label.setFixedWidth(32)
        layout.addWidget(market_label)

        layout.addStretch()

        add_btn = QPushButton("＋加入")
        add_btn.setObjectName("result-add")
        add_btn.setFixedWidth(60)
        add_btn.clicked.connect(lambda: self.added.emit(self.stock))
        layout.addWidget(add_btn)


class CorrelationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("台股相關係數分析")
        self.setMinimumSize(940, 780)
        self.setStyleSheet(QSS)

        self.selected_stocks = []
        self.chip_widgets = {}
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.do_search)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(36, 28, 36, 28)
        root.setSpacing(16)

        # ── Header ──
        title = QLabel("📊 台股相關係數分析")
        title.setObjectName("title")
        root.addWidget(title)

        subtitle = QLabel("搜尋股票 → 點選「加入」→ 選取 2~4 檔後自動分析")
        subtitle.setObjectName("subtitle")
        root.addWidget(subtitle)

        # ── Search area ──
        search_card = QFrame()
        search_card.setObjectName("card")
        search_card.setStyleSheet(
            "QFrame#card { background-color: #14141c; border: 1px solid #22222e; "
            "border-radius: 12px; }"
        )
        search_card_layout = QVBoxLayout(search_card)
        search_card_layout.setContentsMargins(18, 14, 18, 14)
        search_card_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("輸入股票代號或名稱…")
        self.search_input.textChanged.connect(self.on_search_key)
        search_card_layout.addWidget(self.search_input)

        self.search_results = QListWidget()
        self.search_results.setVisible(False)
        self.search_results.setMaximumHeight(220)
        search_card_layout.addWidget(self.search_results)

        root.addWidget(search_card)

        # ── Chips ──
        chips_header = QHBoxLayout()
        chips_header.setSpacing(8)
        chips_label = QLabel("📌 已選取")
        chips_label.setObjectName("section")
        chips_header.addWidget(chips_label)
        self.chips_container = QHBoxLayout()
        self.chips_container.setSpacing(8)
        self.chips_container.setContentsMargins(0, 0, 0, 0)
        chips_header.addLayout(self.chips_container)
        chips_header.addStretch()
        root.addLayout(chips_header)

        # ── Status ──
        self.status_label = QLabel()
        self.status_label.setObjectName("status")
        root.addWidget(self.status_label)

        # ── Progress ──
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        root.addWidget(self.progress)

        # ── Table + Heatmap ──
        columns = QHBoxLayout()
        columns.setSpacing(18)

        # left: table
        left_col = QVBoxLayout()
        left_col.setSpacing(8)
        left_title = QLabel("📋 相關係數表")
        left_title.setObjectName("section")
        left_col.addWidget(left_title)
        self.table = QTableWidget()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setRowCount(1)
        self.table.setColumnCount(1)
        self.table.setItem(0, 0, QTableWidgetItem("請先選取股票"))
        left_col.addWidget(self.table)
        columns.addLayout(left_col, 1)

        # right: heatmap
        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        right_title = QLabel("🎨 熱力圖")
        right_title.setObjectName("section")
        right_col.addWidget(right_title)
        self.heatmap = CorrHeatmap()
        self.heatmap.clear_chart()
        right_col.addWidget(self.heatmap)
        columns.addLayout(right_col, 1)

        root.addLayout(columns)
        self.update_ui_state()
        self.load_stock_list_async()

    # ── Stock list loading ──

    def load_stock_list_async(self):
        global ALL_STOCKS
        if ALL_STOCKS:
            self.on_stocks_loaded()
        else:
            self.status_label.setText("正在載入股票清單…")
            QTimer.singleShot(50, self._load_stocks)

    def _load_stocks(self):
        global ALL_STOCKS
        try:
            ALL_STOCKS = load_stock_list()
            self.on_stocks_loaded()
        except Exception:
            self.status_label.setText("⚠️ 股票清單載入失敗，請檢查網路")

    def on_stocks_loaded(self):
        self.status_label.setText(
            f"✅ 已載入 {len(ALL_STOCKS)} 檔上市櫃股票，開始搜尋吧"
        )

    # ── Search ──

    def on_search_key(self, text):
        self.search_timer.stop()
        if text.strip():
            self.search_timer.start(250)
        else:
            self.search_results.setVisible(False)

    def do_search(self):
        q = self.search_input.text().strip()
        if not q:
            self.search_results.setVisible(False)
            return

        added_codes = {s['code'] for s in self.selected_stocks}
        hits = []
        for s in ALL_STOCKS:
            if s['code'] in added_codes:
                continue
            if q in s['code'] or q in s['name']:
                hits.append(s)
                if len(hits) >= 10:
                    break

        self.search_results.clear()
        if hits:
            for stock in hits:
                item = QListWidgetItem(self.search_results)
                w = SearchResultItem(stock)
                w.added.connect(self.add_stock)
                item.setSizeHint(w.sizeHint())
                self.search_results.addItem(item)
                self.search_results.setItemWidget(item, w)
            self.search_results.setVisible(True)
        else:
            self.search_results.setVisible(False)

    # ── Add / Remove stocks ──

    def add_stock(self, stock):
        if len(self.selected_stocks) >= 4:
            return
        if stock['code'] in {s['code'] for s in self.selected_stocks}:
            return

        self.selected_stocks.append(stock)

        chip = QFrame()
        chip.setObjectName("chip")
        chip.setFixedHeight(34)
        cl = QHBoxLayout(chip)
        cl.setContentsMargins(12, 0, 6, 0)
        cl.setSpacing(6)
        txt = QLabel(f"{stock['code']} {stock['name']}")
        txt.setObjectName("chip-text")
        cl.addWidget(txt)
        rm_btn = QPushButton("✕")
        rm_btn.setObjectName("remove-btn")
        rm_btn.setFixedSize(24, 24)
        rm_btn.clicked.connect(lambda: self.remove_stock(stock['code']))
        cl.addWidget(rm_btn)

        self.chip_widgets[stock['code']] = chip
        self.chips_container.addWidget(chip)
        self.search_input.clear()
        self.search_results.setVisible(False)
        self.search_input.setFocus()
        self.update_ui_state()
        self.trigger_fetch()

    def remove_stock(self, code):
        self.selected_stocks = [s for s in self.selected_stocks if s['code'] != code]
        chip = self.chip_widgets.pop(code, None)
        if chip:
            self.chips_container.removeWidget(chip)
            chip.deleteLater()
        self.update_ui_state()
        self.trigger_fetch()

    def update_ui_state(self):
        n = len(self.selected_stocks)
        if n < 2:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.heatmap.clear_chart()
            if n == 0:
                self.status_label.setText("請從上方搜尋股票，加入分析")
            else:
                self.status_label.setText(
                    f"🔍 已選取 {n} 檔，再選取 {2 - n} 檔即可自動分析"
                )

    # ── Fetch & display ──

    def trigger_fetch(self):
        if len(self.selected_stocks) < 2:
            return
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.status_label.setText("正在取得股價資料…")

        self.worker = FetchWorker(self.selected_stocks)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_finished(self, corr_df, returns_df):
        self.show_correlation(corr_df)
        self.progress.setVisible(False)
        rows = len(returns_df)
        self.status_label.setText(
            f"✅ {len(self.selected_stocks)} 檔股票 × {rows} 個交易日"
            f"　（{returns_df.index[0].date()} ~ {returns_df.index[-1].date()}）"
        )

    def on_error(self, msg):
        self.progress.setVisible(False)
        self.status_label.setText(f"⚠️ {msg}")
        QMessageBox.warning(self, "錯誤", msg)

    def show_correlation(self, corr_df):
        names = corr_df.columns.tolist()
        self.table.setRowCount(len(names))
        self.table.setColumnCount(len(names))
        self.table.setHorizontalHeaderLabels(names)
        self.table.setVerticalHeaderLabels(names)

        values = corr_df.values
        cmap = matplotlib.colormaps["RdYlBu_r"]
        norm = matplotlib.colors.Normalize(vmin=-1, vmax=1)

        for i in range(len(names)):
            for j in range(len(names)):
                val = values[i][j]
                item = QTableWidgetItem(f"{val:.4f}")
                item.setTextAlignment(Qt.AlignCenter)

                r, g, b, _ = cmap(norm(val))
                perceived = 0.299 * r + 0.587 * g + 0.114 * b
                if perceived > 0.45:
                    s = 0.45 / perceived
                    r, g, b = r * s, g * s, b * s
                ri, gi, bi = int(r * 255), int(g * 255), int(b * 255)
                item.setForeground(QColor("#ffffff"))
                item.setBackground(QColor(ri, gi, bi))

                font = QFont()
                font.setBold(True)
                font.setPointSize(11)
                item.setFont(font)
                self.table.setItem(i, j, item)

        self.heatmap.update_heatmap(corr_df)
        self.table.resizeColumnsToContents()


def main():
    app = QApplication(sys.argv)
    window = CorrelationApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
