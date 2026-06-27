import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# 設定中文字型（macOS 使用 Heiti TC，Windows 使用 Microsoft JhengHei）
plt.rcParams['font.sans-serif'] = ['Heiti TC', 'Arial Unicode MS', 'Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False  # 避免負號顯示異常

# 建立圖表
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(bottom=0.3)  # 下方預留空間給滑桿

# X 軸範圍 0 ~ 4π
x = np.linspace(0, 4 * np.pi, 1000)

# 初始參數
A_init = 1.0      # 振幅
omega_init = 1.0  # 頻率
phi_init = 0.0    # 相位偏移

# 繪製初始曲線
sin_line, = ax.plot(x, A_init * np.sin(omega_init * x + phi_init),
                    label='y = A·sin(ωx + φ)', color='#1f77b4', linewidth=2)
cos_line, = ax.plot(x, A_init * np.cos(omega_init * x + phi_init),
                    label='y = A·cos(ωx + φ)', color='#ff7f0e', linewidth=2)

# 圖表設定
ax.set_title('正弦 (sin) 與餘弦 (cos) 波形圖', fontsize=14)
ax.set_xlabel('x (弧度)', fontsize=12)
ax.set_ylabel('y', fontsize=12)
ax.set_xlim(0, 4 * np.pi)
ax.set_ylim(-5.5, 5.5)
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(loc='upper right', fontsize=10)

# ----- 建立滑桿 -----

# 滑桿顏色
slider_color = 'lightgoldenrodyellow'

# 振幅滑桿
ax_amp = plt.axes([0.2, 0.20, 0.6, 0.03], facecolor=slider_color)
slider_amp = Slider(ax_amp, '振幅 A', 0.1, 5.0, valinit=A_init, valstep=0.1)

# 頻率滑桿
ax_freq = plt.axes([0.2, 0.14, 0.6, 0.03], facecolor=slider_color)
slider_freq = Slider(ax_freq, '頻率 ω', 0.1, 10.0, valinit=omega_init, valstep=0.1)

# 相位偏移滑桿
ax_phase = plt.axes([0.2, 0.08, 0.6, 0.03], facecolor=slider_color)
slider_phase = Slider(ax_phase, '相位 φ', 0, 2 * np.pi, valinit=phi_init, valstep=0.05)


# 更新函數：當滑桿數值變動時重新繪製波形
def update(val):
    A = slider_amp.val
    omega = slider_freq.val
    phi = slider_phase.val

    sin_line.set_ydata(A * np.sin(omega * x + phi))
    cos_line.set_ydata(A * np.cos(omega * x + phi))

    # 根據振幅動態調整 Y 軸範圍
    y_max = max(A * 1.2, 1.5)
    ax.set_ylim(-y_max, y_max)

    fig.canvas.draw_idle()


# 註冊滑桿事件
slider_amp.on_changed(update)
slider_freq.on_changed(update)
slider_phase.on_changed(update)

# 顯示互動視窗
plt.show()
