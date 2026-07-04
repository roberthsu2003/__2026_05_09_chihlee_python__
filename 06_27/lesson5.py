#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
lesson5.py - PyQtGraph 強大功能測試與演示儀表板
使用 PySide6 與 PyQtGraph 建立一個現代化、高效能且具高度互動性的科學數據視覺化應用程式。
此應用程式特別展示了 PyQtGraph 在高頻即時刷新、大數據量局部縮放、動態2D影像計算與散佈圖滑鼠互動等方面的卓越表現。
"""

import sys
import os
import time
import numpy as np

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QSlider, QCheckBox, QPushButton,
                               QTabWidget, QSplitter, QGroupBox, QFormLayout, QStatusBar,
                               QComboBox, QStackedWidget, QFrame, QScrollArea)
from PySide6.QtCore import QTimer, Qt, Slot, QPointF
from PySide6.QtGui import QFont, QColor

import pyqtgraph as pg

# 設定 PyQtGraph 全域選項（在建立任何 Widget 之前設定）
pg.setConfigOption('background', "#4b7cd1")  # 設定圖表背景色為柔粉白
pg.setConfigOption('foreground', '#831843')  # 設定圖表前景色為深玫瑰色
pg.setConfigOptions(antialias=True)          # 預設啟用抗鋸齒以提供平滑線條


# MODERN_STYLE 是一個「多行字串」變數，裡面寫的是 QSS 語法
# QSS = Qt Style Sheet，長得很像 CSS，專門用來幫 PySide6 的視窗元件「化妝」
# 三個雙引號 """...""" 是 Python 的多行字串語法，可以跨行寫內容
# 裡面的 "QMainWindow"、"QLabel" 這些是 Qt 元件的名稱
# 大括號 { } 裡面放的是要套用的樣式規則
# 這整個字串最後會透過 setStyleSheet(MODERN_STYLE) 套用到整個視窗
MODERN_STYLE = """
QMainWindow {
    background-color: #fdf2f8;
}

QWidget#centralWidget {
    background-color: #fdf2f8;
}

QLabel {
    color: #831843;
    font-family: ".AppleSystemUIFont", "Noto Sans TC", "Microsoft JhengHei", sans-serif;
    font-size: 13px;
}

QLabel#titleLabel {
    color: #9d174d;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 4px;
}

QLabel#subTitleLabel {
    color: #db2777;
    font-size: 12px;
    margin-bottom: 12px;
}

QGroupBox {
    border: 1px solid #fbcfe8;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
    color: #9d174d;
    font-family: ".AppleSystemUIFont", "Noto Sans TC", "Microsoft JhengHei", sans-serif;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 0 5px;
    background-color: #fdf2f8;
}

QPushButton {
    background-color: #ec4899;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
    font-family: ".AppleSystemUIFont", "Noto Sans TC", "Microsoft JhengHei", sans-serif;
}

QPushButton:hover {
    background-color: #f472b6;
}

QPushButton:pressed {
    background-color: #db2777;
}

/* 控制播放暫停按鈕的特殊樣式 */
QPushButton#playPauseBtn {
    background-color: #34d399;
}
QPushButton#playPauseBtn:hover {
    background-color: #6ee7b7;
}
QPushButton#playPauseBtn:pressed {
    background-color: #10b981;
}

QPushButton#playPauseBtn[checked="true"] {
    background-color: #fb7185;
}
QPushButton#playPauseBtn[checked="true"]:hover {
    background-color: #fda4af;
}
QPushButton#playPauseBtn[checked="true"]:pressed {
    background-color: #f43f5e;
}

QPushButton#actionBtn {
    background-color: #fce7f3;
    color: #831843;
    border: 1px solid #fbcfe8;
}
QPushButton#actionBtn:hover {
    background-color: #fbcfe8;
}
QPushButton#actionBtn:pressed {
    background-color: #f9a8d4;
}

QSlider::groove:horizontal {
    border: 1px solid #fbcfe8;
    height: 6px;
    background: #fce7f3;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ec4899;
    border: none;
    width: 14px;
    margin: -4px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #f472b6;
}

QComboBox {
    background-color: #ffffff;
    border: 1px solid #fbcfe8;
    border-radius: 6px;
    padding: 6px 12px;
    color: #831843;
    font-size: 13px;
    font-family: ".AppleSystemUIFont", "Noto Sans TC", sans-serif;
    min-width: 100px;
}

QComboBox:on {
    border: 1px solid #ec4899;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #fbcfe8;
    selection-background-color: #fce7f3;
    selection-color: #9d174d;
    color: #831843;
}

QCheckBox {
    color: #831843;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #fbcfe8;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #ec4899;
    border: 1px solid #ec4899;
}

QTabWidget::pane {
    border: 1px solid #fbcfe8;
    border-radius: 8px;
    background-color: #ffffff;
    padding: 4px;
}

QTabBar::tab {
    background-color: #fce7f3;
    color: #9d174d;
    border: 1px solid #fbcfe8;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 4px;
    font-weight: 500;
    font-family: ".AppleSystemUIFont", "Noto Sans TC", sans-serif;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #be185d;
    border: 1px solid #fbcfe8;
    border-bottom: 1px solid #ffffff;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background-color: #fbcfe8;
    color: #831843;
}

QScrollBar:vertical {
    background: #fdf2f8;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #fbcfe8;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #f9a8d4;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #fdf2f8;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background: #fbcfe8;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background: #f9a8d4;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QStatusBar {
    background-color: #fdf2f8;
    color: #db2777;
    border-top: 1px solid #fbcfe8;
    font-family: ".AppleSystemUIFont", "Noto Sans TC", sans-serif;
}
"""

class PyQtGraphDemoApp(QMainWindow):
    """PyQtGraph 功能測試儀表板主視窗"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("國堂老師展示-強大功能測試與展示儀表板")
        self.resize(1200, 800)
        self.setStyleSheet(MODERN_STYLE)

        # 全域計時與 FPS 統計相關變數
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self.update_plots)
        self.last_time = time.time()
        self.fps_buffer = []
        self.time_offset = 0.0

        # 初始化各功能模組的參數
        self._init_parameters()

        # 建立 UI 配置
        self._setup_ui()

        # 初始化資料與繪圖狀態
        self.regenerate_scatter_data()
        self.regenerate_zoom_data()
        
        # 啟動即時更新定時器 (預設 60 FPS = ~16ms)
        self.fps_timer.start(16)

    def _init_parameters(self):
        """初始化預設數值"""
        # 示波器設定
        self.oscilloscope_noise = 0.3
        self.oscilloscope_freq1 = 1.0
        self.oscilloscope_freq2 = 2.0
        self.oscilloscope_amp = 1.0

        # 熱圖設定
        self.heatmap_speed = 1.0
        self.heatmap_resolution = 128
        self.heatmap_t = 0.0

        # 散佈圖設定
        self.scatter_count = 1000

    def _setup_ui(self):
        """建立主要 UI 版面配置"""
        # 中央主 Widget
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # 建立狀態列 (提前建立，避免 TabWidget 新增 Tab 時觸發 on_tab_changed 報錯)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 主水平佈局，分割左控制區與右展示區
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # 建立 QSplitter 用於自由調整左側控制欄與右側圖表大小
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #fbcfe8; width: 2px; }")

        # ================== 左側側邊欄：控制面板 ==================
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(12)

        # 側邊欄標題
        title_label = QLabel("PyQtGraph 測試面板")
        title_label.setObjectName("titleLabel")
        sub_title = QLabel("即時、互動、高渲染效能")
        sub_title.setObjectName("subTitleLabel")
        sidebar_layout.addWidget(title_label)
        sidebar_layout.addWidget(sub_title)

        # 1. 全域控制群組 (每個分頁都通用)
        global_group = QGroupBox("全域控制")
        global_layout = QFormLayout(global_group)
        global_layout.setSpacing(10)

        # 播放/暫停按鈕
        self.play_pause_btn = QPushButton("暫停即時渲染")
        self.play_pause_btn.setObjectName("playPauseBtn")
        self.play_pause_btn.setCheckable(True)
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        global_layout.addRow(self.play_pause_btn)

        # 目標刷新率滑桿
        self.fps_slider = QSlider(Qt.Horizontal)
        self.fps_slider.setRange(5, 120)
        self.fps_slider.setValue(60)
        self.fps_slider.valueChanged.connect(self.change_target_fps)
        self.fps_slider_label = QLabel("目標刷新率: 60 FPS")
        global_layout.addRow(self.fps_slider_label, self.fps_slider)

        # 實測 FPS 顯示
        self.fps_display = QLabel("實測刷新率: 0.0 FPS")
        self.fps_display.setStyleSheet("color: #ec4899; font-weight: bold;")
        global_layout.addRow("引擎狀態:", self.fps_display)

        # 抗鋸齒開關
        self.antialias_cb = QCheckBox("啟用全域抗鋸齒 (平滑線條)")
        self.antialias_cb.setChecked(True)
        self.antialias_cb.stateChanged.connect(self.toggle_antialias)
        global_layout.addRow(self.antialias_cb)

        sidebar_layout.addWidget(global_group)

        # 2. 動態控制群組 (使用 QStackedWidget，根據右側選擇的分頁切換控制面板)
        self.param_stack = QStackedWidget()
        
        # --- 分頁一控制面板：示波器設定 ---
        oscilloscope_widget = QWidget()
        osc_layout = QFormLayout(oscilloscope_widget)
        osc_layout.setContentsMargins(0, 0, 0, 0)
        
        osc_group = QGroupBox("即時示波器參數")
        osc_group_layout = QFormLayout(osc_group)

        # 通道一頻率
        self.osc_freq1_slider = QSlider(Qt.Horizontal)
        self.osc_freq1_slider.setRange(5, 50)  # 代表 0.5Hz 到 5.0Hz
        self.osc_freq1_slider.setValue(10)
        self.osc_freq1_slider.valueChanged.connect(self.update_osc_params)
        self.osc_freq1_label = QLabel("通道一頻率: 1.0 Hz")
        osc_group_layout.addRow(self.osc_freq1_label, self.osc_freq1_slider)

        # 通道二頻率
        self.osc_freq2_slider = QSlider(Qt.Horizontal)
        self.osc_freq2_slider.setRange(5, 50)
        self.osc_freq2_slider.setValue(20)
        self.osc_freq2_slider.valueChanged.connect(self.update_osc_params)
        self.osc_freq2_label = QLabel("通道二頻率: 2.0 Hz")
        osc_group_layout.addRow(self.osc_freq2_label, self.osc_freq2_slider)

        # 噪聲強度
        self.osc_noise_slider = QSlider(Qt.Horizontal)
        self.osc_noise_slider.setRange(0, 15)  # 代表 0.0 到 1.5
        self.osc_noise_slider.setValue(3)
        self.osc_noise_slider.valueChanged.connect(self.update_osc_params)
        self.osc_noise_label = QLabel("通道二噪聲: 0.3")
        osc_group_layout.addRow(self.osc_noise_label, self.osc_noise_slider)

        # 顯示網格
        self.osc_grid_cb = QCheckBox("顯示背景網格線")
        self.osc_grid_cb.setChecked(True)
        self.osc_grid_cb.stateChanged.connect(self.toggle_osc_grid)
        osc_group_layout.addRow(self.osc_grid_cb)

        # 啟用十字游標
        self.osc_crosshair_cb = QCheckBox("啟用游標座標讀取")
        self.osc_crosshair_cb.setChecked(True)
        self.osc_crosshair_cb.stateChanged.connect(self.toggle_osc_crosshair)
        osc_group_layout.addRow(self.osc_crosshair_cb)

        osc_layout.addRow(osc_group)
        self.param_stack.addWidget(oscilloscope_widget)

        # --- 分頁二控制面板：連動縮放設定 ---
        zoom_widget = QWidget()
        zoom_layout = QFormLayout(zoom_widget)
        zoom_layout.setContentsMargins(0, 0, 0, 0)

        zoom_group = QGroupBox("大數據選取控制")
        zoom_group_layout = QVBoxLayout(zoom_group)
        
        info_label = QLabel(
            "<b>互動提示：</b><br>"
            "1. 請拖曳上方圖表中的<b>半透明灰色區間</b>來變更局部放大範圍。<br>"
            "2. 可以在選取區間的<b>左右邊緣</b>拖曳以調整寬度。<br>"
            "3. 在下方圖表使用滑鼠滾輪縮放或右鍵拖曳時，上方選取框亦會<b>即時逆向同步</b>。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #9d174d; line-height: 15px;")
        zoom_group_layout.addWidget(info_label)

        self.zoom_regen_btn = QPushButton("重新生成 random walk 趨勢線")
        self.zoom_regen_btn.setObjectName("actionBtn")
        self.zoom_regen_btn.clicked.connect(self.regenerate_zoom_data)
        zoom_group_layout.addWidget(self.zoom_regen_btn)

        zoom_layout.addRow(zoom_group)
        self.param_stack.addWidget(zoom_widget)

        # --- 分頁三控制面板：熱圖設定 ---
        heatmap_widget = QWidget()
        heatmap_layout = QFormLayout(heatmap_widget)
        heatmap_layout.setContentsMargins(0, 0, 0, 0)

        heatmap_group = QGroupBox("2D 熱圖運算參數")
        heatmap_group_layout = QFormLayout(heatmap_group)

        # 波動速度
        self.heat_speed_slider = QSlider(Qt.Horizontal)
        self.heat_speed_slider.setRange(1, 30)  # 代表 0.1x 到 3.0x
        self.heat_speed_slider.setValue(10)
        self.heat_speed_slider.valueChanged.connect(self.update_heat_params)
        self.heat_speed_label = QLabel("波動演進速度: 1.0x")
        heatmap_group_layout.addRow(self.heat_speed_label, self.heat_speed_slider)

        # 色彩地圖選擇
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(["viridis", "plasma", "magma", "inferno", "turbo", "cividis"])
        self.colormap_combo.currentTextChanged.connect(self.change_colormap)
        heatmap_group_layout.addRow("色彩地圖 (Colormap):", self.colormap_combo)

        # 解析度選擇 (測試 PyQtGraph 渲染 2D 矩陣的效率)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItem("64 x 64 (極速)", 64)
        self.resolution_combo.addItem("128 x 128 (標準)", 128)
        self.resolution_combo.addItem("256 x 256 (高精細)", 256)
        self.resolution_combo.setCurrentIndex(1)
        self.resolution_combo.currentIndexChanged.connect(self.change_heatmap_resolution)
        heatmap_group_layout.addRow("運算網格解析度:", self.resolution_combo)

        info_heat = QLabel("提示：右側的色彩條 (Histogram) 可以直接用滑鼠拖曳上下界限來調整影像對比度。")
        info_heat.setWordWrap(True)
        info_heat.setStyleSheet("color: #db2777; font-size: 11px;")
        heatmap_group_layout.addRow(info_heat)

        heatmap_layout.addRow(heatmap_group)
        self.param_stack.addWidget(heatmap_widget)

        # --- 分頁四控制面板：散佈圖設定 ---
        scatter_widget = QWidget()
        scatter_layout = QFormLayout(scatter_widget)
        scatter_layout.setContentsMargins(0, 0, 0, 0)

        scatter_group = QGroupBox("隨機散佈點參數")
        scatter_group_layout = QFormLayout(scatter_group)

        # 資料點數量
        self.scatter_count_combo = QComboBox()
        self.scatter_count_combo.addItem("500 點", 500)
        self.scatter_count_combo.addItem("1,000 點", 1000)
        self.scatter_count_combo.addItem("5,000 點 (效能測試)", 5000)
        self.scatter_count_combo.addItem("10,000 點 (極限效能)", 10000)
        self.scatter_count_combo.currentIndexChanged.connect(self.change_scatter_count)
        scatter_group_layout.addRow("資料點數 (Size):", self.scatter_count_combo)

        # 隨機重建按鈕
        self.scatter_regen_btn = QPushButton("隨機重新分佈資料點")
        self.scatter_regen_btn.setObjectName("actionBtn")
        self.scatter_regen_btn.clicked.connect(self.regenerate_scatter_data)
        scatter_group_layout.addRow(self.scatter_regen_btn)

        info_scatter = QLabel(
            "<b>互動提示：</b><br>"
            "1. 滑鼠移到資料點上時，點會<b>自動高亮變紅</b>並在狀態列顯示座標。<br>"
            "2. 使用滑鼠<b>左鍵點擊</b>任一點，該點會被加上<b>紅色追蹤框</b>以標示選取。<br>"
            "3. 點選後，視窗底部狀態列將永久保留該點的資訊。"
        )
        info_scatter.setWordWrap(True)
        info_scatter.setStyleSheet("color: #9d174d; line-height: 15px;")
        scatter_group_layout.addRow(info_scatter)

        scatter_layout.addRow(scatter_group)
        self.param_stack.addWidget(scatter_widget)

        sidebar_layout.addWidget(self.param_stack)
        sidebar_layout.addStretch()

        # ================== 右側展示區：主分頁 Widget ==================
        self.main_tab = QTabWidget()
        self.main_tab.currentChanged.connect(self.on_tab_changed)

        # 建立四個展示分頁的實體
        self._create_tab_oscilloscope()
        self._create_tab_zoom()
        self._create_tab_heatmap()
        self._create_tab_scatter()

        # 將側邊欄與主要展示區加入 Splitter 容器
        # 側邊欄放置一個容器，以固定其最小寬度
        sidebar_container = QWidget()
        sidebar_container.setLayout(sidebar_layout)
        sidebar_container.setMinimumWidth(260)
        sidebar_container.setMaximumWidth(350)
        
        splitter.addWidget(sidebar_container)
        splitter.addWidget(self.main_tab)
        
        # 設定 Splitter 初始分配比例 (20% : 80%)
        splitter.setSizes([280, 900])

        # 主版面佈局加入 Splitter
        main_layout.addWidget(splitter)

        # 設定狀態列初始訊息
        self.status_bar.showMessage("系統就緒。當前分頁：即時示波器模式")

    # ================== 分頁一：即時多通道示波器 ==================
    def _create_tab_oscilloscope(self):
        # 建立 PyQtGraph 的 GraphicsLayoutWidget 容器 (用來靈活組織多個 Plot)
        self.osc_widget = pg.GraphicsLayoutWidget()
        
        # 通道一
        self.p1 = self.osc_widget.addPlot(row=0, col=0, title="通道一：模擬正弦波 (CH1 Sine Wave)")
        self.p1.showGrid(x=True, y=True, alpha=0.25)
        self.p1.setLabel('left', '振幅', units='V')
        self.p1.setLabel('bottom', '時間點', units='sample')
        self.curve1 = self.p1.plot(pen=pg.mkPen(color='#ec4899', width=2), name="CH1")

        # 通道二
        self.p2 = self.osc_widget.addPlot(row=1, col=0, title="通道二：含噪聲波 (CH2 Sine + Noise)")
        self.p2.showGrid(x=True, y=True, alpha=0.25)
        self.p2.setLabel('left', '振幅', units='V')
        self.p2.setLabel('bottom', '時間點', units='sample')
        self.curve2 = self.p2.plot(pen=pg.mkPen(color='#a855f7', width=1.5), name="CH2")

        # 連動兩個圖表的 X 軸限制 (縮放與拖曳時，兩者會自動對齊)
        self.p2.setXLink(self.p1)

        # 建立十字定位線 (CH1)
        self.vLine1 = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#f472b6', width=1, style=Qt.DashLine))
        self.hLine1 = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('#f472b6', width=1, style=Qt.DashLine))
        self.p1.addItem(self.vLine1, ignoreBounds=True)
        self.p1.addItem(self.hLine1, ignoreBounds=True)

        # 建立十字定位線 (CH2)
        self.vLine2 = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#c084fc', width=1, style=Qt.DashLine))
        self.hLine2 = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('#c084fc', width=1, style=Qt.DashLine))
        self.p2.addItem(self.vLine2, ignoreBounds=True)
        self.p2.addItem(self.hLine2, ignoreBounds=True)

        # 用於圖表內的座標文字顯示
        self.coord_label1 = pg.TextItem(anchor=(1, 0), color='#ec4899')
        self.coord_label2 = pg.TextItem(anchor=(1, 0), color='#a855f7')
        self.p1.addItem(self.coord_label1)
        self.p2.addItem(self.coord_label2)

        # 建立滑鼠事件 Proxy，避免在密集滑鼠移動下造成介面阻塞 (限流在 60Hz 內)
        self.osc_mouse_proxy = pg.SignalProxy(
            self.osc_widget.scene().sigMouseMoved, 
            rateLimit=60, 
            slot=self.on_osc_mouse_moved
        )

        self.main_tab.addTab(self.osc_widget, "即時多通道示波器")

    def on_osc_mouse_moved(self, evt):
        """處理示波器分頁的滑鼠滑過事件，並移動十字游標與更新座標顯示"""
        if not self.osc_crosshair_cb.isChecked():
            return
            
        pos = evt[0]
        # 檢查滑鼠是在哪一個 ViewBox 內
        if self.p1.sceneBoundingRect().contains(pos):
            mouse_point = self.p1.vb.mapSceneToView(pos)
            x_val, y_val = mouse_point.x(), mouse_point.y()
            
            # 更新 CH1 十字線
            self.vLine1.setPos(x_val)
            self.hLine1.setPos(y_val)
            # 同步更新 CH2 的垂直線 (因為 X 軸已鎖定連動)
            self.vLine2.setPos(x_val)
            
            # 顯示座標字串
            self.coord_label1.setText(f"X: {x_val:.1f}\nY: {y_val:.3f}")
            # 將文字固定在目前顯示畫面視窗的右上角
            x_range, y_range = self.p1.viewRange()
            self.coord_label1.setPos(x_range[1], y_range[1])
            
        elif self.p2.sceneBoundingRect().contains(pos):
            mouse_point = self.p2.vb.mapSceneToView(pos)
            x_val, y_val = mouse_point.x(), mouse_point.y()
            
            # 更新 CH2 十字線
            self.vLine2.setPos(x_val)
            self.hLine2.setPos(y_val)
            # 同步更新 CH1 的垂直線
            self.vLine1.setPos(x_val)
            
            self.coord_label2.setText(f"X: {x_val:.1f}\nY: {y_val:.3f}")
            x_range, y_range = self.p2.viewRange()
            self.coord_label2.setPos(x_range[1], y_range[1])

    # ================== 分頁二：互動式區間縮放 ==================
    def _create_tab_zoom(self):
        self.zoom_widget = pg.GraphicsLayoutWidget()
        
        # 上方的全局概覽圖
        self.p_overview = self.zoom_widget.addPlot(row=0, col=0, title="全局走勢 (請調整灰色半透明區間)")
        self.p_overview.showGrid(x=True, y=True, alpha=0.15)
        # 固定高度，不隨視窗調整比例而無限延伸
        self.p_overview.setFixedHeight(180)
        
        # 下方的局部放大圖
        self.p_detail = self.zoom_widget.addPlot(row=1, col=0, title="選取範圍局部放大 (雙向同步)")
        self.p_detail.showGrid(x=True, y=True, alpha=0.25)
        self.p_detail.getAxis('bottom').setPen(pg.mkPen('#ec4899', width=1))

        # 建立區間選擇器 (LinearRegionItem)
        self.region = pg.LinearRegionItem([3000, 5000])
        self.region.setZValue(10)  # 確保繪製在曲線上方
        self.p_overview.addItem(self.region)

        # 雙向連動訊號綁定
        # 1. 當上方選擇區間改變時，更新下方圖表的 X 軸範圍
        self.region.sigRegionChanged.connect(self.sync_zoom_detail_plot)
        # 2. 當下方圖表被拖曳/縮放 (X 軸範圍改變) 時，反向更新上方的選擇區間
        self.p_detail.sigXRangeChanged.connect(self.sync_zoom_region_box)

        # 設定一個鎖以防止無限循環呼叫
        self.zoom_updating_lock = False

        self.main_tab.addTab(self.zoom_widget, "區間選取與縮放")

    def regenerate_zoom_data(self):
        """生成並重新繪製 random walk 趨勢"""
        # 模擬 10,000 點的隨機走勢
        np.random.seed(int(time.time()))
        steps = np.random.normal(0, 0.2, 10000)
        self.zoom_data = steps.cumsum() + 50

        # 清除舊線條
        self.p_overview.clear()
        self.p_detail.clear()
        
        # 重新加入區間與連動物件
        self.p_overview.addItem(self.region)

        # 繪製曲線
        self.p_overview.plot(self.zoom_data, pen=pg.mkPen('#f9a8d4', width=1))
        self.p_detail.plot(self.zoom_data, pen=pg.mkPen('#ec4899', width=1.8))
        
        # 重設區域與顯示範圍
        self.region.setRegion([3000, 5000])
        self.sync_zoom_detail_plot()

    def sync_zoom_detail_plot(self):
        """將上方的 LinearRegionItem 位置同步到下方的詳細 Plot"""
        if self.zoom_updating_lock:
            return
        self.zoom_updating_lock = True
        min_x, max_x = self.region.getRegion()
        # 更新下方 X 軸範圍
        self.p_detail.setXRange(min_x, max_x, padding=0)
        self.zoom_updating_lock = False

    def sync_zoom_region_box(self):
        """當下方詳細 Plot 變更範圍時，逆向更新上方 LinearRegionItem 區間"""
        if self.zoom_updating_lock:
            return
        self.zoom_updating_lock = True
        # 取得下方 Plot 目前可見的 X 軸範圍
        min_x, max_x = self.p_detail.viewRange()[0]
        # 限制範圍不要超出數據長度
        min_x = max(0, min_x)
        max_x = min(len(self.zoom_data), max_x)
        self.region.setRegion([min_x, max_x])
        self.zoom_updating_lock = False

    # ================== 分頁三：即時 2D 漣漪干涉熱圖 ==================
    def _create_tab_heatmap(self):
        self.heat_widget = pg.GraphicsLayoutWidget()
        
        # 建立圖像的 Plot 外框
        self.p_image = self.heat_widget.addPlot(row=0, col=0, title="波源干涉即時干涉圖 (2D ImageItem)")
        # 隱藏刻度以便於觀察影像
        self.p_image.showAxis('left', False)
        self.p_image.showAxis('bottom', False)

        # 建立 ImageItem
        self.image_item = pg.ImageItem()
        self.p_image.addItem(self.image_item)

        # 建立右側的長條狀色彩與強度直方圖調整器 (HistogramLUTItem)
        self.lut_item = pg.HistogramLUTItem()
        self.lut_item.setImageItem(self.image_item)
        self.heat_widget.addItem(self.lut_item)

        # 設定預設色彩表為 viridis
        self.change_colormap("viridis")

        self.main_tab.addTab(self.heat_widget, "即時 2D 熱圖")

    def update_heatmap_grid(self):
        """根據解析度重新計算網格矩陣"""
        res = self.heatmap_resolution
        x = np.linspace(-15, 15, res)
        y = np.linspace(-15, 15, res)
        self.heat_X, self.heat_Y = np.meshgrid(x, y)

    def change_colormap(self, name):
        """更換 Histogram 的色彩映照表"""
        try:
            cmap = pg.colormap.get(name)
            self.lut_item.gradient.setColorMap(cmap)
        except Exception as e:
            print(f"更換色彩映射表失敗: {e}")

    def change_heatmap_resolution(self, index):
        """更換熱圖運算的解析度"""
        self.heatmap_resolution = self.resolution_combo.currentData()
        self.update_heatmap_grid()
        self.status_bar.showMessage(f"解析度變更為: {self.heatmap_resolution} x {self.heatmap_resolution}")

    # ================== 分頁四：互動式散佈圖 ==================
    def _create_tab_scatter(self):
        self.scatter_widget = pg.GraphicsLayoutWidget()
        self.p_scatter = self.scatter_widget.addPlot(title="互動式散佈圖 (1,000隨機常態分佈點)")
        self.p_scatter.showGrid(x=True, y=True, alpha=0.2)
        
        # 用於標記點選的紅色光圈 ScatterItem
        self.clicked_marker = pg.ScatterPlotItem(
            size=18, 
            pen=pg.mkPen('#be185d', width=2), 
            brush=pg.mkBrush(None), 
            symbol='o'
        )
        self.p_scatter.addItem(self.clicked_marker)
        self.clicked_marker.setVisible(False)
        self.selected_point_idx = None

        # 建立滑鼠懸停限流 Proxy 以偵測最接近的點
        self.scatter_mouse_proxy = pg.SignalProxy(
            self.scatter_widget.scene().sigMouseMoved, 
            rateLimit=60, 
            slot=self.on_scatter_mouse_moved
        )

        self.main_tab.addTab(self.scatter_widget, "互動式散佈圖")

    def regenerate_scatter_data(self):
        """重新生成散佈圖數據"""
        self.p_scatter.clear()
        
        # 重新加入點選圈圈
        self.clicked_marker.setVisible(False)
        self.p_scatter.addItem(self.clicked_marker)
        self.selected_point_idx = None

        # 建立點的座標 (常態分佈)
        np.random.seed(int(time.time() * 100) % 10000)
        self.scatter_x = np.random.normal(0, 1.0, self.scatter_count)
        self.scatter_y = np.random.normal(0, 1.0, self.scatter_count)

        # 建立高互動性 ScatterPlotItem
        # 建立 QColor 並設定 alpha，解決 pyqtgraph.mkBrush 無法直接解析字串加 alpha 的問題
        s_color = pg.mkColor('#ec4899')
        s_color.setAlpha(150)
        h_color = pg.mkColor('#be185d')
        h_color.setAlpha(220)

        # hoverable=True 讓滑鼠移過時會自動觸發 hover 事件，並改用 hoverBrush / hoverPen 的外觀
        self.scatter_item = pg.ScatterPlotItem(
            size=10, 
            pen=pg.mkPen('#fbcfe8', width=0.5), 
            brush=pg.mkBrush(s_color),
            hoverable=True,
            hoverBrush=pg.mkBrush(h_color),  # 懸停時變為亮粉紅色
            hoverPen=pg.mkPen('#ffffff', width=1.5)
        )
        
        # 封裝點的結構資訊
        spots = [{'pos': (self.scatter_x[i], self.scatter_y[i]), 'data': i} for i in range(self.scatter_count)]
        self.scatter_item.addPoints(spots)
        
        # 綁定點擊事件
        self.scatter_item.sigClicked.connect(self.on_scatter_clicked)
        
        self.p_scatter.addItem(self.scatter_item)
        self.p_scatter.setTitle(f"互動式散佈圖 (共 {self.scatter_count:,} 點)")

    def change_scatter_count(self, index):
        """切換散佈圖點的數量"""
        self.scatter_count = self.scatter_count_combo.currentData()
        self.regenerate_scatter_data()
        self.status_bar.showMessage(f"已隨機生成 {self.scatter_count:,} 個常態分佈點，已備妥以測試效能！")

    def on_scatter_clicked(self, item, points):
        """當玩家點選散佈圖的任一點時"""
        if not points:
            return
        
        # 取得點擊到的第一個點資訊
        point = points[0]
        pos = point.pos()
        idx = point.data()
        
        self.selected_point_idx = idx
        
        # 在點的位置加上紅色環狀標記圈
        self.clicked_marker.setData(x=[pos.x()], y=[pos.y()])
        self.clicked_marker.setVisible(True)
        
        msg = f"📍 選取點編號: {idx} | 座標: ({pos.x():.4f}, {pos.y():.4f})"
        self.status_bar.showMessage(msg)

    def on_scatter_mouse_moved(self, evt):
        """偵測滑鼠位置並提示最近點的座標"""
        pos = evt[0]
        if self.p_scatter.sceneBoundingRect().contains(pos):
            mouse_point = self.p_scatter.vb.mapSceneToView(pos)
            
            # 使用 numpy 向量化快速計算與所有點的直線歐氏距離
            distances = (self.scatter_x - mouse_point.x())**2 + (self.scatter_y - mouse_point.y())**2
            nearest_idx = np.argmin(distances)
            min_dist = np.sqrt(distances[nearest_idx])
            
            # 滑鼠必須足夠靠近該點 (例如在 0.15 繪圖坐標系單位內)
            if min_dist < 0.18:
                x_val = self.scatter_x[nearest_idx]
                y_val = self.scatter_y[nearest_idx]
                
                # 如果該點就是已選取的點，就不重複洗掉選取狀態
                if self.selected_point_idx == nearest_idx:
                    return
                self.status_bar.showMessage(f"👀 懸停點編號: {nearest_idx} | 座標: ({x_val:.4f}, {y_val:.4f})")
            else:
                # 若滑鼠移開，恢復顯示目前選取的點，或是一般說明
                if self.selected_point_idx is not None:
                    pos_x = self.scatter_x[self.selected_point_idx]
                    pos_y = self.scatter_y[self.selected_point_idx]
                    self.status_bar.showMessage(f"📍 選取點編號: {self.selected_point_idx} | 座標: ({pos_x:.4f}, {pos_y:.4f})")
                else:
                    self.status_bar.showMessage("互動式散佈圖：滑鼠懸停顯示最近點，左鍵點擊可鎖定點。")

    # ================== 動態更新核心與定時器 ==================
    def update_plots(self):
        """定時更新圖表 (核心主迴圈，提供即時動態效果)"""
        # 計算實際的渲染 FPS
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # 避免除以零
        if dt > 0:
            self.fps_buffer.append(1.0 / dt)
            if len(self.fps_buffer) > 40:
                self.fps_buffer.pop(0)
            avg_fps = sum(self.fps_buffer) / len(self.fps_buffer)
            self.fps_display.setText(f"實測刷新率: {avg_fps:.1f} FPS")

        # 根據播放按鈕狀態決定是否跳過更新
        if self.play_pause_btn.isChecked():
            return

        # 取得當前作用中的分頁索引
        active_tab = self.main_tab.currentIndex()

        # 分頁一：即時多通道示波器更新
        if active_tab == 0:
            self.time_offset += 0.05
            
            # 生成 500 個點的時間軸
            x = np.arange(500)
            
            # 計算正弦波 CH1: y = sin(x * w + phi)
            phi1 = self.time_offset * self.oscilloscope_freq1
            y1 = self.oscilloscope_amp * np.sin(x * 0.05 + phi1)
            
            # 計算含噪聲波 CH2: y = sin(x * w + phi) + noise
            phi2 = self.time_offset * self.oscilloscope_freq2
            noise = np.random.normal(0, self.oscilloscope_noise, size=len(x))
            y2 = self.oscilloscope_amp * np.sin(x * 0.04 + phi2) + noise
            
            # 透過 setData 更新曲線，相比於 matplotlib 這是極速更新的核心方法！
            self.curve1.setData(x, y1)
            self.curve2.setData(x, y2)

        # 分頁三：即時 2D 熱圖更新
        elif active_tab == 2:
            self.heatmap_t += 0.12 * self.heatmap_speed
            
            # 建立兩個動態旋轉的點電荷波源
            x1 = 5.0 * np.sin(self.heatmap_t * 0.7)
            y1 = 5.0 * np.cos(self.heatmap_t * 0.4)
            x2 = -5.0 * np.sin(self.heatmap_t * 0.5)
            y2 = -5.0 * np.cos(self.heatmap_t * 0.8)
            
            # 運算與波源的歐式距離矩陣
            dist1 = np.sqrt((self.heat_X - x1)**2 + (self.heat_Y - y1)**2)
            dist2 = np.sqrt((self.heat_X - x2)**2 + (self.heat_Y - y2)**2)
            
            # 雙波源疊加方程式與距離衰減 (波的擴散干涉)
            # z = sin(2 * r - t) / (r + 1.2)
            wave1 = np.sin(1.8 * dist1 - self.heatmap_t) / (dist1 + 1.2)
            wave2 = np.sin(1.8 * dist2 - self.heatmap_t) / (dist2 + 1.2)
            z = wave1 + wave2
            
            # 呼叫 setImage 實現 60FPS 的 2D 矩陣極速渲染
            self.image_item.setImage(z)

    # ================== 控制面板信號觸發槽 ==================
    @Slot(int)
    def on_tab_changed(self, index):
        """當主要展示分頁切換時，同步切換左側控制面板的細項設定"""
        self.param_stack.setCurrentIndex(index)
        
        # 同步狀態列顯示
        tab_names = ["即時示波器模式", "區間選取與縮放模式", "即時 2D 熱圖模式", "互動式散佈圖模式"]
        self.status_bar.showMessage(f"切換至: {tab_names[index]}")

        # 若切換到不需要定時器的分頁，可保留定時器，但若切換到 2D 熱圖，需先確認網格是否已建立
        if index == 2:
            if not hasattr(self, 'heat_X'):
                self.update_heatmap_grid()

    @Slot()
    def toggle_play_pause(self):
        """暫停/恢復即時動畫更新"""
        paused = self.play_pause_btn.isChecked()
        if paused:
            self.play_pause_btn.setText("恢復即時渲染")
            self.status_bar.showMessage("已暫停即時繪圖更新")
            # 不用停止 Timer，這樣 FPS 計算與滑鼠互動依然順暢，只是跳過波形數據更新
        else:
            self.play_pause_btn.setText("暫停即時渲染")
            self.status_bar.showMessage("已恢復即時繪圖更新")
            self.last_time = time.time()

    @Slot(int)
    def change_target_fps(self, value):
        """調整 QTimer 觸發頻率以調整目標 FPS"""
        self.fps_slider_label.setText(f"目標刷新率: {value} FPS")
        interval_ms = int(1000 / value)
        self.fps_timer.setInterval(interval_ms)
        self.status_bar.showMessage(f"已調整目標刷新率為: {value} Hz (~{interval_ms} 毫秒間隔)")

    @Slot(int)
    def toggle_antialias(self, state):
        """開關全域抗鋸齒 (有助於改善密集線條在某些顯卡上的渲染速度)"""
        enabled = (state == Qt.Checked.value)
        pg.setConfigOptions(antialias=enabled)
        # 重新整理一下，讓抗鋸齒選項作用
        self.status_bar.showMessage(f"全域抗鋸齒選項已變更為: {enabled}")

    @Slot()
    def update_osc_params(self):
        """同步示波器控制面板數值"""
        self.oscilloscope_freq1 = self.osc_freq1_slider.value() / 10.0
        self.oscilloscope_freq2 = self.osc_freq2_slider.value() / 10.0
        self.oscilloscope_noise = self.osc_noise_slider.value() / 10.0
        
        self.osc_freq1_label.setText(f"通道一頻率: {self.oscilloscope_freq1:.1f} Hz")
        self.osc_freq2_label.setText(f"通道二頻率: {self.oscilloscope_freq2:.1f} Hz")
        self.osc_noise_label.setText(f"通道二噪聲: {self.oscilloscope_noise:.1f}")

    @Slot(int)
    def toggle_osc_grid(self, state):
        """開關示波器的背景格線"""
        show = (state == Qt.Checked.value)
        self.p1.showGrid(x=show, y=show, alpha=0.25 if show else 0)
        self.p2.showGrid(x=show, y=show, alpha=0.25 if show else 0)
        self.status_bar.showMessage(f"顯示格線: {show}")

    @Slot(int)
    def toggle_osc_crosshair(self, state):
        """隱藏或顯示示波器的十字游標與座標標籤"""
        show = (state == Qt.Checked.value)
        self.vLine1.setVisible(show)
        self.hLine1.setVisible(show)
        self.vLine2.setVisible(show)
        self.hLine2.setVisible(show)
        self.coord_label1.setVisible(show)
        self.coord_label2.setVisible(show)
        
        if not show:
            self.status_bar.showMessage("已隱藏十字坐標游標")
        else:
            self.status_bar.showMessage("已啟用十字坐標游標（滑鼠移入波形圖即可顯示座標）")

    @Slot()
    def update_heat_params(self):
        """同步熱圖控制面板數值"""
        self.heatmap_speed = self.heat_speed_slider.value() / 10.0
        self.heat_speed_label.setText(f"波動演進速度: {self.heatmap_speed:.1f}x")

def main():
    """主程式啟動入口"""
    # 建立應用程式
    app = QApplication(sys.argv)
    
    # 解決高 DPI 螢幕字型渲染鋸齒問題，設定全域微軟正黑體/系統預設黑體
    font = QFont(".AppleSystemUIFont", 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    # 建立視窗並顯示
    window = PyQtGraphDemoApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
