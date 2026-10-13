import sqlite3
import json
import time
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表结构，程序启动时自动调用"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            total_defects INTEGER NOT NULL,
            level_count TEXT NOT NULL,
            is_qualified INTEGER NOT NULL,
            defect_details TEXT,
            create_time REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def insert_record(image_path, total_defects, level_count, is_qualified, defect_details):
    """
    插入一条检测记录
    :return: 记录ID
    """
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO detection_records 
        (image_path, total_defects, level_count, is_qualified, defect_details, create_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        image_path,
        total_defects,
        json.dumps(level_count, ensure_ascii=False),
        1 if is_qualified else 0,
        json.dumps(defect_details, ensure_ascii=False),
        time.time()
    ))
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id


def get_records(limit=20, offset=0):
    """分页查询历史记录，按时间倒序"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, image_path, total_defects, level_count, is_qualified, create_time
        FROM detection_records
        ORDER BY create_time DESC
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "image_path": row["image_path"],
            "total_defects": row["total_defects"],
            "level_count": json.loads(row["level_count"]),
            "is_qualified": bool(row["is_qualified"]),
            "create_time": row["create_time"]
        })
    conn.close()
    return result


def get_statistics():
    """获取全局检测统计数据"""
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM detection_records')
    total = cursor.fetchone()["total"]
    
    cursor.execute('SELECT COUNT(*) as pass FROM detection_records WHERE is_qualified = 1')
    pass_count = cursor.fetchone()["pass"]
    
    cursor.execute('SELECT SUM(total_defects) as sum_def FROM detection_records')
    sum_defects = cursor.fetchone()["sum_def"] or 0
    
    conn.close()
    return {
        "total_records": total,
        "pass_rate": round(pass_count / total * 100, 2) if total > 0 else 0,
        "total_defects": int(sum_defects)
    }
