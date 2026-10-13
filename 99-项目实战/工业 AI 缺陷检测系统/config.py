import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 上传文件存储目录
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
# 数据库文件路径
DB_PATH = os.path.join(BASE_DIR, 'db', 'defect.db')

# 自动创建目录
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ========== 业务参数配置 ==========
# 连通域连通方式：4=四连通，8=八连通
CONNECTIVITY = 4
# 最小有效缺陷面积（像素），小于该值视为噪点过滤
MIN_VALID_AREA = 3

# 缺陷等级阈值与配色
DEFECT_CONFIG = {
    "轻微": {"max_area": 50, "color": (255, 255, 0), "desc": "可放行"},
    "一般": {"max_area": 200, "color": (255, 165, 0), "desc": "需记录"},
    "严重": {"max_area": float("inf"), "color": (255, 0, 0), "desc": "不合格"}
}
