"""
台灣鄉鎮市區人口密度查詢系統 (上下版面 + 滾動圖表版)
使用 pandas 處理資料，並以 PySide6 與 Matplotlib 建立現代化 GUI 介面與即時資料視覺化圖表
"""

import os
import sys
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QAbstractItemView,
                             QHeaderView, QScrollArea, QSplitter)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# 導入 Matplotlib 元件
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# 設定 Matplotlib 全域中文字型相容性，以避免中文字型顯示為方塊與粗體警告
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'Microsoft JhengHei', 'DejaVu Sans', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常顯示負號

# 現代化深色主題 QSS 樣式表
MODERN_STYLE = """
QMainWindow {
    background-color: #121214;
}

QWidget#centralwidget {
    background-color: #121214;
}

QLabel {
    color: #e1e1e6;
    font-size: 14px;
    font-weight: 500;
    font-family: ".AppleSystemUIFont", "Noto Sans TC", "Helvetica Neue", Arial, sans-serif;
}

QLabel#chartTitle {
    font-size: 15px;
    font-weight: 600;
    color: #ffffff;
}

QLineEdit {
    background-color: #202024;
    color: #e1e1e6;
    border: 1px solid #29292e;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    font-family: ".AppleSystemUIFont", "Noto Sans TC", "Helvetica Neue", Arial, sans-serif;
}

QLineEdit:focus {
    border: 1px solid #996dff;
    background-color: #252529;
}

QPushButton {
    background-color: #996dff;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
    font-family: ".AppleSystemUIFont", "Noto Sans TC", "Helvetica Neue", Arial, sans-serif;
}

QPushButton:hover {
    background-color: #a880ff;
}

QPushButton:pressed {
    background-color: #8859ff;
}

QTableWidget {
    background-color: #202024;
    color: #e1e1e6;
    border: 1px solid #29292e;
    border-radius: 10px;
    gridline-color: #29292e;
    font-size: 13px;
    font-family: ".AppleSystemUIFont", "Noto Sans TC", "Helvetica Neue", Arial, sans-serif;
    outline: none;
}

QTableWidget::item {
    padding: 12px;
    border-bottom: 1px solid #1a1a1e;
}

QTableWidget::item:selected {
    background-color: #292238;
    color: #996dff;
    font-weight: 600;
}

QHeaderView::section {
    background-color: #18181b;
    color: #aeaeae;
    padding: 12px;
    border: none;
    border-bottom: 2px solid #29292e;
    font-weight: 700;
    font-size: 13px;
    font-family: ".AppleSystemUIFont", "Noto Sans TC", "Helvetica Neue", Arial, sans-serif;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

/* 垂直滾動條美化 */
QScrollBar:vertical {
    background: #121214;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #29292e;
    min-height: 30px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #3e3e4a;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* 水平滾動條美化 */
QScrollBar:horizontal {
    background: #121214;
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background: #29292e;
    min-width: 30px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background: #3e3e4a;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}
"""


def load_and_process_data(file_path: str) -> pd.DataFrame:
    """
    讀取 CSV 並進行資料整理，回傳處理後的 DataFrame。
    """
    # 讀取 CSV，使用第 2 列（index=1）作為欄位名稱
    df = pd.read_csv(file_path, header=1)

    # 移除最後 5 筆非資料內容（尾部說明資訊）
    df = df.iloc[:-5].reset_index(drop=True)

    # 僅保留需要的三個欄位：區域別、年底人口數、土地面積
    df = df[['區域別', '年底人口數', '土地面積']].copy()

    # 將年底人口數重新命名為人口數
    df.rename(columns={'年底人口數': '人口數'}, inplace=True)

    # 將人口數與土地面積轉換為數值型態
    df['人口數'] = pd.to_numeric(df['人口數'], errors='coerce')
    df['土地面積'] = pd.to_numeric(df['土地面積'], errors='coerce')

    # 移除含有空值的列
    df = df.dropna().reset_index(drop=True)

    # 新增人口密度欄位
    df['人口密度'] = df['人口數'] / df['土地面積']

    return df


class PopulationQueryApp(QMainWindow):
    """台灣鄉鎮市區人口密度查詢系統的主視窗類別 (上下版面 + 滾動圖表版)"""

    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self.data = data

        # 設定視窗標題與大視窗尺寸
        self.setWindowTitle('台灣鄉鎮市區人口密度查詢與視覺化系統')
        self.resize(1100, 800)

        # 套用 QSS 樣式
        self.setStyleSheet(MODERN_STYLE)

        # 建立中央 Widget
        central_widget = QWidget()
        central_widget.setObjectName("centralwidget")
        self.setCentralWidget(central_widget)

        # 主要的垂直佈局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # 建立一個 QSplitter 作為上下比例調整器
        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("QSplitter::handle { background-color: #29292e; height: 2px; }")

        # ================== 上半部面板 (數據與篩選) ==================
        top_panel = QWidget()
        top_layout = QVBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 8)
        top_layout.setSpacing(12)

        # 建立上方控制區（水平佈局）
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)

        label = QLabel('輸入區域名稱：')
        control_layout.addWidget(label)

        self.keyword_entry = QLineEdit()
        self.keyword_entry.setPlaceholderText('例如：板橋、信義區、大安...')
        self.keyword_entry.setFixedWidth(280)
        # 輸入文字時即時篩選資料與更新圖表
        self.keyword_entry.textChanged.connect(lambda: self.query_data())
        control_layout.addWidget(self.keyword_entry)

        query_button = QPushButton('查詢')
        query_button.setCursor(Qt.PointingHandCursor)
        query_button.clicked.connect(self.query_data)
        control_layout.addWidget(query_button)

        control_layout.addStretch()
        top_layout.addLayout(control_layout)

        # 建立表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['區域別', '人口數 (人)', '土地面積 (km²)', '人口密度 (人/km²)'])
        
        # 表格設定
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 唯讀不可編輯
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 整列選取
        self.table.setSelectionMode(QAbstractItemView.SingleSelection) # 單選模式
        self.table.setShowGrid(True)                                   # 顯示網格線
        self.table.verticalHeader().setVisible(False)                  # 隱藏行號

        # 表格 Header 與列高設定
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        self.table.verticalHeader().setDefaultSectionSize(38)

        for i in range(4):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        top_layout.addWidget(self.table)
        splitter.addWidget(top_panel)                                  # 將上半部加入 Splitter

        # ================== 下半部面板 (圖表視覺化) ==================
        bottom_panel = QWidget()
        bottom_panel.setObjectName("chartPanel")
        bottom_panel.setStyleSheet("QWidget#chartPanel { background-color: #202024; border: 1px solid #29292e; border-radius: 10px; }")
        
        bottom_layout = QVBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(16, 16, 16, 16)
        bottom_layout.setSpacing(8)

        # 圖表區域標題
        chart_title = QLabel('人口密度即時分析圖 (可左右滾動看完全部數據)')
        chart_title.setObjectName("chartTitle")
        bottom_layout.addWidget(chart_title)

        # 建立 QScrollArea 來裝載 Matplotlib 畫布
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # 隱藏垂直滾動條
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded) # 必要時顯示水平滾動條

        # 建立 Matplotlib Figure 與 Canvas
        # 初始大小可以大一點，稍後會根據資料筆數動態設寬
        self.fig = Figure(figsize=(10, 3.2), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        
        # 設定畫布背景色為深色以配合整體主題
        self.fig.patch.set_facecolor('#202024')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#202024')

        # 將 Canvas 設為 ScrollArea 的主 Widget
        self.scroll_area.setWidget(self.canvas)
        bottom_layout.addWidget(self.scroll_area)
        splitter.addWidget(bottom_panel)                               # 將下半部加入 Splitter

        # 設定 Splitter 上下初始分配比例 (50% : 50%)
        splitter.setSizes([380, 380])
        main_layout.addWidget(splitter)

        # 預設顯示所有資料並繪製初始圖表
        self.refresh_table(self.data)

    def refresh_table(self, df: pd.DataFrame) -> None:
        """
        清空表格並填入指定的 DataFrame 資料，隨後同步更新圖表。
        """
        # 清除現有資料並設定列數
        self.table.setRowCount(0)
        self.table.setRowCount(len(df))

        # 逐筆插入資料到表格中
        for row_idx, (_, row) in enumerate(df.iterrows()):
            item_area = QTableWidgetItem(str(row['區域別']))
            item_pop = QTableWidgetItem(f"{int(row['人口數']):,}") 
            item_size = QTableWidgetItem(f"{row['土地面積']:.4f}") 
            item_density = QTableWidgetItem(f"{row['人口密度']:.2f}")

            # 文字置中
            for item in (item_area, item_pop, item_size, item_density):
                item.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(row_idx, 0, item_area)
            self.table.setItem(row_idx, 1, item_pop)
            self.table.setItem(row_idx, 2, item_size)
            self.table.setItem(row_idx, 3, item_density)

        # 同步更新圖表 (包含所有內容)
        self.update_chart(df)

    def update_chart(self, df: pd.DataFrame) -> None:
        """
        根據目前的資料動態更新下方的 Matplotlib 柱狀圖。
        會顯示所有篩選出來的數據，並利用 QScrollArea 進行水平滾動。
        """
        self.ax.clear()

        if df.empty:
            # 當沒有資料時，在圖表中央顯示提示文字
            self.ax.text(0.5, 0.5, '無符合搜尋條件的資料',
                         color='#aeaeae', fontsize=14,
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes)
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            for spine in self.ax.spines.values():
                spine.set_color('#29292e')
            # 重設畫布為預設寬度
            default_width = max(1000, self.scroll_area.width() - 10)
            self.fig.set_size_inches(default_width / 100.0, 2.8)
            self.canvas.setMinimumSize(default_width, 280)
            self.canvas.draw()
            return

        # 依人口密度從高到低排序以利於呈現
        chart_df = df.sort_values(by='人口密度', ascending=False)
        num_items = len(chart_df)

        # 動態計算畫布寬度以容納所有內容而不重疊！
        # 每個柱子加上間距給予 32 像素寬度，最小寬度為當前 scroll_area 的寬度
        scroll_area_width = self.scroll_area.width()
        # 避免初次載入時 width() 為 0 或極小值，預設為 1000
        base_width = max(1000, scroll_area_width - 10)
        dynamic_width = max(base_width, num_items * 32)
        
        # 同步設定 Matplotlib Figure 的尺寸 (寬度英吋 = 像素/DPI) 與 Canvas 最小尺寸，確保圖表從最左側開始繪製而不留白
        self.fig.set_size_inches(dynamic_width / 100.0, 2.8)
        self.canvas.setMinimumSize(dynamic_width, 280)

        # 繪製柱狀圖
        bars = self.ax.bar(chart_df['區域別'], chart_df['人口密度'], color='#996dff', width=0.55)

        # 美化圖表外觀，套用深色模式
        title_text = f"區域人口密度分佈 (共 {num_items} 筆資料)"
        self.ax.set_title(title_text, color='#ffffff', fontsize=12, pad=10)
        self.ax.set_xlabel("區域別", color='#aeaeae', fontsize=9, labelpad=6)
        self.ax.set_ylabel("人口密度 (人/km²)", color='#aeaeae', fontsize=9, labelpad=6)

        # 網格線設定 (極淡的網格)
        self.ax.grid(True, axis='y', linestyle='--', alpha=0.08, color='#e1e1e6')

        # 調整軸線邊框顏色
        for spine in self.ax.spines.values():
            spine.set_color('#29292e')

        # 刻度樣式
        self.ax.tick_params(colors='#aeaeae', which='both', labelsize=8)
        self.ax.tick_params(axis='x', labelrotation=45)

        # 只有當總資料量較少時 (例如 <= 20 筆)，才在柱子上方顯示數值標記，避免大量數據時重疊
        if num_items <= 20:
            for bar in bars:
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2.0, height + (height * 0.01),
                             f"{height:.0f}",
                             ha='center', va='bottom', color='#e1e1e6', fontsize=7.5)

        # X 軸的範圍緊貼兩端以善用空間
        self.ax.set_xlim(-0.5, num_items - 0.5)

        self.fig.tight_layout()
        self.canvas.draw()

    def query_data(self) -> None:
        """
        根據使用者輸入的關鍵字篩選區域別，並更新表格。
        """
        keyword = self.keyword_entry.text().strip()
        if keyword == '':
            filtered = self.data
        else:
            filtered = self.data[self.data['區域別'].str.contains(keyword, na=False)]
        self.refresh_table(filtered)


def main():
    """應用程式進入點"""
    app = QApplication(sys.argv)

    # 設定全域字型（解決中文字型鋸齒與渲染問題）
    font = QFont(".AppleSystemUIFont", 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    # 以程式所在目錄為基準，建構 CSV 檔案路徑
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '各鄉鎮市區人口密度.csv')

    # 讀取並處理資料
    try:
        data = load_and_process_data(csv_path)
    except FileNotFoundError:
        print(f"錯誤：找不到 CSV 檔案 {csv_path}")
        return
    except Exception as e:
        print(f"處理資料時發生錯誤：{e}")
        return

    # 建立與顯示 GUI
    window = PopulationQueryApp(data)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
