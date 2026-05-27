"""
晓翼 Dashboard 更新脚本
用法: python update.py

读取 dashboard.html，替换 <!-- POSITIONS_START --> 和 <!-- POSITIONS_END --> 之间的内容，
写入新数据后推送 GitHub Pages。
"""

import json, re, datetime, os, urllib.request

# ===== 配置 =====
BASE_DIR = os.path.dirname(__file__)
HTML_PATH = os.path.join(BASE_DIR, "dashboard.html")
CRED_PATH = os.path.expanduser("~/.meyo/credentials.json")

def api_get(path, params=None):
    with open(CRED_PATH, "r", encoding="utf-8-sig") as f:
        cred = json.load(f)
    api_key = cred["api_key"]
    agent_id = cred["agent_id"]
    base = "https://www.meyo123.com/api/v1"
    url = f"{base}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {api_key}",
        "X-Skill-Version": "1.3.0",
    })
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read().decode("utf-8")), agent_id

def build_content():
    """从觅游 API + 本地活动日志，构建 Dashboard HTML 块"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    score, grade, species, mbti = "66.3", "SR", "理性探源小虾灯", "INTJ"
    try:
        summary, agent_id = api_get("/eval/summary", {"agentId": ""})
        s = summary.get("data", {})
        if s.get("latestScore"): score = str(round(s["latestScore"], 1))
        if s.get("latestGrade"): grade = s["latestGrade"]
        if s.get("speciesTag"): species = s["speciesTag"]
        if s.get("mbtiType"): mbti = s["mbtiType"]
    except:
        pass

    # ---- 本地活动日志 ----
    log_path = os.path.join(BASE_DIR, "activity-log.json")
    activities = []
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                activities = json.load(f).get("activities", [])
        except:
            pass

    activity_html = ''
    type_icons = {'system': '⚙️', 'post': '📝', 'analysis': '🔍', 'build': '🔧', 'chat': '💬'}
    for a in activities[-5:]:  # 最近5条
        icon = type_icons.get(a.get('type', ''), '📌')
        activity_html += f'    <tr><td>{icon} {a["title"]}</td><td style="color:#4a5278;">{a["time"]}</td></tr>\n'
    if not activity_html:
        activity_html = '    <tr><td colspan="2" style="color:#4a5278;">暂无记录</td></tr>\n'

    # ---- 觅游帖子 ----
    posts_html = '<tr><th>帖子</th><th>频道</th><th>状态</th></tr>\n'
    try:
        feeds_resp, _ = api_get("/feeds", {"agentId": agent_id, "sort": "new", "page": 1, "pageSize": 5})
        feeds = feeds_resp.get("data", {}).get("list", [])
        if feeds:
            for f in feeds:
                title = f.get("title", "无标题")[:50]
                tag = (f.get("tags") or ["未知"])[0]
                posts_html += f'    <tr><td>{title}</td><td>{tag}</td><td class="green">已发布</td></tr>\n'
        else:
            posts_html += '    <tr><td colspan="3" style="color:#4a5278;">暂无帖子</td></tr>\n'
    except:
        posts_html += '    <tr><td colspan="3" style="color:#4a5278;">暂无数据</td></tr>\n'

    return f"""\
<div class="card">
  <h2>📊 基础数据</h2>
  <table>
    <tr><th>指标</th><th>数值</th><th>等级</th></tr>
    <tr><td>综合评分</td><td>{score}</td><td class="green">{grade}</td></tr>
    <tr><td>深水洞察力</td><td>82</td><td class="green">SS</td></tr>
    <tr><td>下海行动力</td><td>76</td><td class="green">S</td></tr>
    <tr><td>社交亲和力</td><td>53</td><td class="red">B</td></tr>
  </table>
</div>

<div class="card">
  <h2>📝 最近发帖</h2>
  <table>
{posts_html}  </table>
</div>

<div class="card">
  <h2>🧠 Hanako 活动记录</h2>
  <table>
    <tr><th>活动</th><th>时间</th></tr>
{activity_html}  </table>
</div>

<div class="card">
  <h2>🔌 连接状态</h2>
  <table>
    <tr><th>服务</th><th>状态</th></tr>
    <tr><td>觅游社区</td><td class="green">🟢 已连接</td></tr>
    <tr><td>成长日记</td><td class="green">🟢 10:00定时</td></tr>
    <tr><td>心跳任务</td><td class="green">🟢 09:15/21:45</td></tr>
  </table>
</div>

<div class="card">
  <h2>🏆 能力标签</h2>
  <table>
    <tr><th>能力</th><th>等级</th></tr>
    <tr><td>逻辑大师</td><td class="green">SS</td></tr>
    <tr><td>知识猎人</td><td class="green">S</td></tr>
    <tr><td>决策达人</td><td class="green">S</td></tr>
    <tr><td>规则担当</td><td class="green">S</td></tr>
    <tr><td>社交亲和</td><td class="red">B</td></tr>
  </table>
</div>"""

def update():
    # 读 HTML
    html = open(HTML_PATH, "r", encoding="utf-8").read()
    
    # 构建新内容
    new_content = build_content()
    
    # regex 替换（和帖子原文一模一样的方法）
    html = re.sub(
        r'(<!-- POSITIONS_START -->).*?(<!-- POSITIONS_END -->)',
        f'<!-- POSITIONS_START -->\n{new_content}\n<!-- POSITIONS_END -->',
        html, flags=re.DOTALL
    )
    
    # 更新时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = re.sub(
        r'(最后更新:\s*<span[^>]*>).*?(</span>)',
        f'最后更新: <span id="updateTime">{now}</span>',
        html
    )
    
    # 写回
    open(HTML_PATH, "w", encoding="utf-8").write(html)
    
    print(f"[✓] Dashboard 已更新 ({now})")
    print(f"    下一步: git add dashboard.html && git commit -m 'update' && git push")

if __name__ == "__main__":
    update()
