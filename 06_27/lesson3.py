"""
台灣鄉鎮市區人口密度查詢系統
使用 pandas 處理資料，並以 tkinter/ttk 建立 GUI 介面
"""

import os
import pandas as pd
import tkinter as tk
from tkinter import ttk


def load_and_process_data(file_path: str) -> pd.DataFrame:
    """
    讀取 CSV 並進行資料整理，回處理後的 DataFrame。
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


class PopulationQueryApp:
    """台灣鄉鎮市區人口密度查詢系統的主視窗類別"""

    def __init__(self, root: tk.Tk, data: pd.DataFrame):
        self.root = root
        self.data = data

        # 設定視窗標題與大小
        self.root.title('台灣鄉鎮市區人口密度查詢系統')
        self.root.geometry('900x600')

        # 建立上方控制區
        control_frame = ttk.Frame(root)
        control_frame.pack(pady=10)

        label = ttk.Label(control_frame, text='輸入區域名稱：')
        label.pack(side=tk.LEFT, padx=(0, 5))

        self.keyword_entry = ttk.Entry(control_frame, width=30)
        self.keyword_entry.pack(side=tk.LEFT, padx=(0, 5))

        query_button = ttk.Button(control_frame, text='查詢', command=self.query_data)
        query_button.pack(side=tk.LEFT)

        # 建立下方表格區
        columns = ('區域別', '人口數', '土地面積', '人口密度')
        self.tree = ttk.Treeview(root, columns=columns, show='headings', height=25)

        # 設定各欄位標題與寬度（各 180，置中對齊）
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.CENTER)
            self.tree.column(col, width=180, anchor=tk.CENTER)

        # 加入垂直與水平捲軸
        v_scroll = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        # 預設顯示所有資料
        self.refresh_table(self.data)

    def refresh_table(self, df: pd.DataFrame) -> None:
        """
        清空表格並填入指定的 DataFrame 資料。
        人口密度四捨五入至小數點後兩位，人口數顯示為整數。
        """
        # 清除現有資料
        for row in self.tree.get_children():
            self.tree.delete(row)

        # 逐筆插入資料
        for _, row in df.iterrows():
            self.tree.insert(
                '',
                tk.END,
                values=(
                    row['區域別'],
                    int(row['人口數']),
                    row['土地面積'],
                    round(row['人口密度'], 2),
                ),
            )

    def query_data(self) -> None:
        """
        根據使用者輸入的關鍵字篩選區域別，並更新表格。
        若關鍵字為空，則顯示所有資料。
        """
        keyword = self.keyword_entry.get().strip()
        if keyword == '':
            filtered = self.data
        else:
            filtered = self.data[self.data['區域別'].str.contains(keyword, na=False)]
        self.refresh_table(filtered)


def main():
    """應用程式進入點"""
    # 以程式所在目錄為基準，建構 CSV 檔案路徑
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '各鄉鎮市區人口密度.csv')

    # 讀取並處理資料
    data = load_and_process_data(csv_path)

    # 建立 GUI
    root = tk.Tk()
    app = PopulationQueryApp(root, data)
    root.mainloop()


if __name__ == '__main__':
    main()
