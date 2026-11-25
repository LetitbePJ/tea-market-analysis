"""公共绘图配置：中文字体回退与缺失告警

Windows 的 SimHei / macOS 的 PingFang SC / Linux 的 Noto Sans CJK SC 都试一遍，
可用哪个用哪个；都没有则告警并退回默认字体（图上中文会变方框，但脚本不崩）。
"""
import sys
import warnings

import matplotlib.pyplot as plt
from matplotlib import font_manager

# 按顺序探测：Windows -> macOS -> Linux 常见中文字体
_CANDIDATES = ["SimHei", "Microsoft YaHei", "PingFang SC", "Heiti SC",
               "Noto Sans CJK SC", "WenQuanYi Micro Hei", "Arial Unicode MS"]


def setup_chinese_font():
    """配置 matplotlib 中文字体并关闭负号乱码；找不到时给出明确告警。"""
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = next((name for name in _CANDIDATES if name in available), None)
    if chosen is None:
        warnings.warn(
            "未找到任何中文字体（已试：" + "、".join(_CANDIDATES) +
            "）。图表中的中文可能显示为方框，请安装其中一种字体后重试。",
            RuntimeWarning, stacklevel=2,
        )
        print(f"[字体告警] 无可用中文字体，图表中文可能显示为方框（已试 {len(_CANDIDATES)} 种）",
              file=sys.stderr)
        return None
    plt.rcParams["font.sans-serif"] = [chosen]
    plt.rcParams["axes.unicode_minus"] = False
    return chosen
