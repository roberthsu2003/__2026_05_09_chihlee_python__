```
import pandas as pd
import numpy as np

# 讀取 CSV 檔
dataFrame = pd.read_csv('各班圖書借閱統計.csv')

# 第 0 列(index 為 0)才是真正的中文欄位名稱,把它設為欄位名
dataFrame.columns = dataFrame.loc[0]

# 刪除第 0 列(已經拿來當欄位名,資料中不需要重複)
dataFrame = dataFrame.drop(0)

# 提示:整理後資料最後面有「合計列」與 4 列說明文字要刪掉
# 先印出 dataFrame 看看那些列的 index 是多少
print(dataFrame)

# 請完成:刪除合計列與 4 列說明文字(用 drop,可加 inplace=True)
# dataFrame.drop([______], inplace=True)


# 取得目前的列數與欄數
rowCount, columnCount = dataFrame.shape

# 請完成:把索引重設為從 0 開始的連續編號
# dataFrame.index = ______


# 請完成:只保留「班級」「學生人數」「借閱冊數」三個欄位
# dataFrame1 = dataFrame.reindex(columns=[______])


print(dataFrame1)
```