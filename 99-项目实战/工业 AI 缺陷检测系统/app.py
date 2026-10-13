import cv2
import numpy as np
import base64
import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory

from config import UPLOAD_DIR, MIN_VALID_AREA, CONNECTIVITY, DEFECT_CONFIG
from models.segment_model import model_instance
from db.database import init_db, insert_record, get_records, get_statistics

# ===================== 应用初始化 =====================
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 单文件最大20MB
init_db()  # 初始化数据库表


# ===================== 核心算法：连通域后处理 =====================
def defect_postprocess_opencv(mask):
    mask = np.array(mask, dtype=np.uint8)
    if mask.max() == 1:
        mask = mask * 255

    # OpenCV 连通域分析核心函数
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        mask, connectivity=CONNECTIVITY, ltype=cv2.CV_32S
    )

    defect_list = []
    for label_id in range(1, num_labels):
        x = stats[label_id, cv2.CC_STAT_LEFT]
        y = stats[label_id, cv2.CC_STAT_TOP]
        w = stats[label_id, cv2.CC_STAT_WIDTH]
        h = stats[label_id, cv2.CC_STAT_HEIGHT]
        area = stats[label_id, cv2.CC_STAT_AREA]
        center_y, center_x = centroids[label_id]

        # 过滤微小噪点
        if area < MIN_VALID_AREA:
            continue

        # 判定缺陷等级
        level = "严重"
        level_desc = DEFECT_CONFIG["严重"]["desc"]
        for lv, cfg in DEFECT_CONFIG.items():
            if area < cfg["max_area"]:
                level = lv
                level_desc = cfg["desc"]
                break

        defect_info = {
            "defect_id": len(defect_list) + 1,
            "level": level,
            "level_desc": level_desc,
            "area": int(area),
            "center": [round(center_x, 2), round(center_y, 2)],
            "bbox": {
                "x_min": int(x), "y_min": int(y),
                "x_max": int(x + w - 1), "y_max": int(y + h - 1),
                "width": int(w), "height": int(h)
            }
        }
        defect_list.append(defect_info)

    # 全局统计
    stats_summary = {
        "total_defects": len(defect_list),
        "level_count": {
            "轻微": sum(1 for d in defect_list if d["level"] == "轻微"),
            "一般": sum(1 for d in defect_list if d["level"] == "一般"),
            "严重": sum(1 for d in defect_list if d["level"] == "严重")
        },
        "is_qualified": sum(1 for d in defect_list if d["level"] == "严重") == 0
    }

    # 生成标注可视化图
    vis_img = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    for d in defect_list:
        bbox = d["bbox"]
        color = DEFECT_CONFIG[d["level"]]["color"]
        cv2.rectangle(vis_img,
                     (bbox["x_min"], bbox["y_min"]),
                     (bbox["x_max"], bbox["y_max"]),
                     color, 2)
        cv2.putText(vis_img, f"#{d['defect_id']}",
                   (bbox["x_min"], max(bbox["y_min"] - 5, 15)),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return defect_list, stats_summary, vis_img


# ===================== 页面路由 =====================
@app.route('/')
def index():
    return render_template('index.html')


# ===================== 缺陷检测接口 =====================
@app.route('/api/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return jsonify({"error": "请上传图片文件"}), 400

    file = request.files['image']
    try:
        # 1. 保存原始图片
        file_ext = os.path.splitext(file.filename)[1] or '.png'
        save_name = f"{uuid.uuid4().hex}{file_ext}"
        save_path = os.path.join(UPLOAD_DIR, save_name)
        file.save(save_path)

        # 2. 读取图片
        image = cv2.imread(save_path)
        if image is None:
            return jsonify({"error": "图片读取失败，格式不支持"}), 400

        # 3. 分割模型推理，生成缺陷掩码
        mask = model_instance.predict(image)

        # 4. 连通域后处理分析
        defects, statistics, vis_img = defect_postprocess_opencv(mask)

        # 5. 保存标注结果图
        vis_save_name = f"vis_{save_name}"
        vis_save_path = os.path.join(UPLOAD_DIR, vis_save_name)
        cv2.imwrite(vis_save_path, vis_img)

        # 6. 检测记录写入数据库
        insert_record(
            image_path=f"/static/uploads/{save_name}",
            total_defects=statistics["total_defects"],
            level_count=statistics["level_count"],
            is_qualified=statistics["is_qualified"],
            defect_details=defects
        )

        # 7. 标注图转base64返回前端
        _, vis_encoded = cv2.imencode('.png', vis_img)
        vis_base64 = "data:image/png;base64," + base64.b64encode(vis_encoded.tobytes()).decode('utf-8')

        return jsonify({
            "code": 0,
            "message": "检测成功",
            "defects": defects,
            "statistics": statistics,
            "visualization": vis_base64
        })

    except Exception as e:
        return jsonify({"error": f"处理失败: {str(e)}"}), 500


# ===================== 历史记录接口 =====================
@app.route('/api/records')
def records():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    data = get_records(limit, offset)
    return jsonify({"code": 0, "data": data})


# ===================== 全局统计接口 =====================
@app.route('/api/stats')
def stats():
    data = get_statistics()
    return jsonify({"code": 0, "data": data})


# ===================== 静态文件访问 =====================
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
