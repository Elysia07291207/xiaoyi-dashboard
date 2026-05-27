"""
晓翼 · 活动记录助手
用法：python log.py <类型> "<标题>" "<详情>"

类型: system / post / analysis / build / chat
示例: python log.py build "重构Dashboard" "将活动日志接入update.py"
"""

import json, sys, os, datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), "activity-log.json")

def log(type_name, title, detail=""):
    # 读现有日志
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"version": 1, "activities": []}
    
    # 生成新 ID
    ids = [a.get("id", 0) for a in data["activities"]]
    new_id = max(ids) + 1 if ids else 1
    
    # 添加
    data["activities"].append({
        "id": new_id,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": type_name,
        "title": title,
        "detail": detail,
    })
    
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[✓] 已记录: {title}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    log(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
