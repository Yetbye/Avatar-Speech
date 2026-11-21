#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Venus Reading Portal renderer.
- Reads  portal/data/papers.json  (metadata + taxonomy)
- Reads  portal/content/<slug>.html (per-paper reading content, Venus component kit)
- Writes  portal/blogs/<slug>.html  (reading blog pages)  +  portal/index.html (hub)
Style locked to Venus (Palette A · Ukiyo Blue). Cover art = per-paper meaningful SVG motif.
"""
import json, os, re, html

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "papers.json")
CONTENT = os.path.join(BASE, "content")
BLOGS = os.path.join(BASE, "blogs")
os.makedirs(BLOGS, exist_ok=True)

# Palette A — Ukiyo Blue (kept in sync with venus.css)
P = {
    "bg": "#FAF9F6", "bg2": "#F5F5F0", "bg3": "#E8E8E4",
    "ink": "#2C3E50", "ink2": "#5D6D7E", "muted": "#95A5A6",
    "primary": "#1B4B6F", "secondary": "#5A8F7B", "tertiary": "#2E4057",
    "warm": "#E85D4E", "gold": "#C9A86C", "soft": "#FFB7C5",
}

# ---------------------------------------------------------------- NAV / FOOTER
NAV = """
<header class="nav">
  <div class="container nav-inner">
    <a class="nav-brand" href="{root}index.html">Avatar<span class="dot">·</span>Speech</a>
    <nav class="nav-links" id="navLinks">
      <a class="nav-link" href="{root}index.html#taxonomy">分类地图</a>
      <a class="nav-link" href="{root}index.html#av-foundation">基础模型</a>
      <a class="nav-link" href="{root}index.html#speech-video">语音-视频</a>
      <a class="nav-link" href="{root}index.html#whiteboard">白板要点</a>
      <a class="nav-link" href="{root}index.html#routes">路线对照</a>
      <a class="nav-cta" href="{root}index.html#library">全部博客</a>
    </nav>
    <button class="nav-toggle" id="navToggle" aria-label="menu">☰</button>
  </div>
</header>
"""

FOOTER = """
<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <h4>Avatar · Speech 阅读门户</h4>
        <p style="color:#b9c4ce;font-size:0.92rem;max-width:360px">
          按白板要点梳理「音视频联合生成」的论文谱系：从 <em>sequential 串行生成</em> 到
          <em>Vid + Speech 联合生成</em>，覆盖基础模型与语音-视频生成两条主线。
          风格锁定 Venus 可组合设计系统。
        </p>
      </div>
      <div>
        <h4>分类</h4>
        <ul class="footer-links">
          <li><a href="{root}index.html#av-foundation">音视频基础模型</a></li>
          <li><a href="{root}index.html#speech-video">语音-视频生成</a></li>
          <li><a href="{root}index.html#routes">路线对照</a></li>
        </ul>
      </div>
      <div>
        <h4>阅读</h4>
        <ul class="footer-links">
          <li><a href="{root}index.html#library">全部解读博客</a></li>
          <li><a href="{root}index.html#whiteboard">研究要点地图</a></li>
          <li><a href="{root}index.html#recent">近半年新增</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      Venus 可组合设计系统 · Palette A 浮世绘蓝调 · 仅供研究学习 · 数据来源于公开论文
    </div>
  </div>
</footer>
"""

SCRIPTS = """
<script>
  const t=document.getElementById('navToggle'),l=document.getElementById('navLinks');
  if(t){t.addEventListener('click',()=>l.classList.toggle('open'));}
  const io=new IntersectionObserver((es)=>{es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');io.unobserve(e.target);}});},{threshold:0.12});
  document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
</script>
"""

# ---------------------------------------------------------------- COVER MOTIFS
def motif_svg(motif, title):
    prim, sec, warm, gold, ink = P["primary"], P["secondary"], P["warm"], P["gold"], P["ink"]
    W, H = 820, 430
    def node(x, y, w, h, fill, stroke, label, tcol="#fff", fs=17, r=12):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
                f'<text x="{x+w/2}" y="{y+h/2+6}" text-anchor="middle" font-family="Noto Sans SC,sans-serif" font-size="{fs}" font-weight="700" fill="{tcol}">{label}</text>')
    def arrow(x1, y1, x2, y2, col=None, w=3):
        col = col or warm
        return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}" marker-end="url(#ah)"/>')
    defs = (f'<defs><marker id="ah" markerWidth="10" markerHeight="10" refX="7" refY="5" orient="auto">'
            f'<path d="M0,0 L8,5 L0,10 z" fill="{warm}"/></marker>'
            f'<linearGradient id="gbg" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{P["bg2"]}"/><stop offset="1" stop-color="{P["bg"]}"/></linearGradient></defs>')
    body = ""
    if motif == "dual-stream":
        body += node(90, 90, 180, 70, prim, prim, "Video Tokens")
        body += node(90, 250, 180, 70, sec, sec, "Audio Tokens")
        body += node(560, 170, 180, 70, ink, ink, "Joint DiT")
        for y in (125, 285):
            body += arrow(285, y, 555, 205)
        body += f'<text x="410" y="150" text-anchor="middle" font-family="Noto Sans SC" font-size="15" fill="{warm}" font-weight="700">Joint / Cross Attention</text>'
    elif motif == "single-stream":
        xs = 70
        cols = [prim, warm, prim, gold, prim, warm, prim, sec]
        for i in range(8):
            body += f'<rect x="{xs+i*86}" y="175" width="72" height="72" rx="10" fill="{cols[i]}" opacity="0.9"/>'
        body += f'<text x="410" y="130" text-anchor="middle" font-family="Noto Sans SC" font-size="22" font-weight="800" fill="{ink}">Single Stream · Video+Audio interleaved</text>'
        body += f'<text x="410" y="300" text-anchor="middle" font-family="Noto Sans SC" font-size="15" fill="{P["ink2"]}">大道至简 · 更少模块 = 更快</text>'
    elif motif == "unified-token":
        body += node(70, 100, 170, 66, prim, prim, "Video")
        body += node(70, 250, 170, 66, sec, sec, "Audio")
        body += node(325, 175, 175, 66, gold, gold, "Codebook", tcol="#fff")
        body += node(585, 100, 165, 66, prim, prim, "Videô")
        body += node(585, 250, 165, 66, sec, sec, "Audiô")
        body += arrow(245, 133, 325, 205); body += arrow(245, 283, 325, 215)
        body += arrow(505, 205, 585, 133); body += arrow(505, 215, 585, 283)
    elif motif == "bridge":
        body += node(70, 170, 190, 76, prim, prim, "Video DiT")
        body += node(560, 170, 190, 76, sec, sec, "Audio DiT")
        body += f'<rect x="330" y="120" width="160" height="180" rx="16" fill="{warm}" opacity="0.14" stroke="{warm}" stroke-width="2"/>'
        body += f'<text x="410" y="215" text-anchor="middle" font-family="Noto Sans SC" font-size="18" font-weight="800" fill="{warm}">Bridge</text>'
        body += arrow(265, 205, 335, 205); body += arrow(485, 205, 555, 205)
    elif motif == "ar":
        for i in range(6):
            h = 46 + i * 32
            body += f'<rect x="{80+i*116}" y="{320-h}" width="92" height="{h}" rx="10" fill="{prim if i%2==0 else sec}" opacity="0.9"/>'
            body += f'<text x="{80+i*116+46}" y="345" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="13" fill="{P["ink2"]}">t{i+1}</text>'
        body += arrow(60, 330, 760, 330, gold, 2)
        body += f'<text x="410" y="120" text-anchor="middle" font-family="Noto Sans SC" font-size="22" font-weight="800" fill="{ink}">Progressive Resolution · Autoregressive</text>'
    elif motif == "streaming":
        for i in range(20):
            hh = 30 + (i % 5) * 16
            body += f'<rect x="{70+i*35}" y="{210-hh/2}" width="16" height="{hh}" rx="4" fill="{sec}" opacity="0.85"/>'
        for i in range(12):
            body += f'<rect x="{72+i*58}" y="255" width="46" height="34" rx="6" fill="{prim}" opacity="0.85"/>'
        body += arrow(70, 120, 750, 120, warm, 2)
        body += f'<text x="410" y="105" text-anchor="middle" font-family="Noto Sans SC" font-size="16" font-weight="700" fill="{warm}">异步双流 · 流式时间轴</text>'
    elif motif == "expressive":
        body += f'<circle cx="410" cy="215" r="120" fill="{warm}" opacity="0.12"/>'
        for ang, lab in [(90,"Tone"),(210,"Text"),(330,"Motion")]:
            import math
            x = 410 + 150*math.cos(math.radians(ang)); y = 215 + 150*math.sin(math.radians(ang))
            body += node(x-70, y-33, 140, 66, prim, prim, lab)
            body += arrow(x + (410-x)*0.28, y + (215-y)*0.28, x + (410-x)*0.6, y + (215-y)*0.6, gold)
        body += f'<circle cx="410" cy="215" r="52" fill="{gold}"/><text x="410" y="222" text-anchor="middle" font-family="Noto Sans SC" font-size="18" font-weight="800" fill="#fff">表现力</text>'
    elif motif == "conversation":
        body += f'<rect x="90" y="120" width="270" height="120" rx="22" fill="{prim}"/><text x="225" y="192" text-anchor="middle" font-family="Noto Sans SC" font-size="19" font-weight="700" fill="#fff">说话 Speaking</text>'
        body += f'<rect x="460" y="230" width="270" height="120" rx="22" fill="{sec}"/><text x="595" y="302" text-anchor="middle" font-family="Noto Sans SC" font-size="19" font-weight="700" fill="#fff">倾听 Listening</text>'
        body += arrow(360, 250, 455, 275); body += arrow(455, 200, 365, 175, gold)
    elif motif == "alignment":
        for i in range(6):
            y1 = 130 + i*30; y2 = 250 + i*20
            body += f'<circle cx="{150+i*100}" cy="{y1}" r="13" fill="{prim}"/>'
            body += f'<circle cx="{150+i*100}" cy="{y2}" r="13" fill="{sec}"/>'
            body += f'<line x1="{150+i*100}" y1="{y1+16}" x2="{150+i*100}" y2="{y2-16}" stroke="{gold}" stroke-width="2.5"/>'
        body += f'<text x="410" y="410" text-anchor="middle" font-family="Noto Sans SC" font-size="17" font-weight="700" fill="{ink}">Latent 对齐 · 共享语义坐标</text>'
    else:
        body += node(280, 170, 260, 90, prim, prim, "Avatar · Speech", fs=22)
    return (f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title}">'
            f'<rect width="{W}" height="{H}" fill="url(#gbg)"/>{defs}{body}</svg>')

def pick_motif(p):
    tags = " ".join(p.get("tags", [])) + " " + p.get("route", "")
    tl = tags.lower()
    for key, m in [("streaming","streaming"),("real-time","streaming"),("single-stream","single-stream"),
                   ("autoregressive","ar"),("progressive","ar"),("unified-representation","unified-token"),
                   ("tokenizer","unified-token"),("codebook","unified-token"),("expressive","expressive"),
                   ("conversation","conversation"),("talking-listening","conversation"),("listening","conversation"),
                   ("embodied","conversation"),("bridge","bridge"),("align","alignment"),("contrastive","alignment")]:
        if key in tl:
            return m
    return "dual-stream"

# ---------------------------------------------------------------- SHELL
def page(title, desc, root, body):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;700;900&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400;600&family=Ma+Shan+Zheng&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}css/venus.css">
<link rel="stylesheet" href="{root}css/blog.css">
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)'],['$','$']],displayMath:[['$$','$$']]}}}};</script>
</head>
<body>
{NAV.replace("{root}", root)}
<main>
{body}
</main>
{FOOTER.replace("{root}", root)}
{SCRIPTS}
</body>
</html>"""

def build_toc(content):
    hs = re.findall(r'<h2[^>]*>(.*?)</h2>', content, re.S)
    items = []
    for i, h in enumerate(hs, 1):
        clean = re.sub(r'<[^>]+>', '', h).strip()
        anchor = re.sub(r'<span class="num">\s*\d+\s*</span>', '', h).strip()
        anchor = re.sub(r'<[^>]+>', '', anchor)
        aid = f"s{i}"
        items.append(f'<li><a href="#{aid}">{html.escape(clean)}</a></li>')
        content = content.replace(h, h, 1)  # no-op keep
    # inject ids onto h2s
    idx = [0]
    def repl(m):
        idx[0] += 1
        return f'<h2 id="s{idx[0]}" {m.group(1)}>{m.group(2)}</h2>'
    content = re.sub(r'<h2([^>]*)>(.*?)</h2>', repl, content, flags=re.S)
    toc = f'<div class="toc"><div class="toc-title">本文目录</div><ol>{"".join(items)}</ol></div>' if items else ""
    return toc, content

def build_blog(p, all_papers):
    slug = p["slug"]
    cpath = os.path.join(CONTENT, slug + ".html")
    if os.path.exists(cpath):
        with open(cpath, encoding="utf-8") as f:
            content = f.read()
    else:
        content = ("<section class=\"b-section\"><h2><span class=\"num\">00</span> 待补充</h2>"
                   "<p>本篇解读正在撰写中（内容占位）。核心方法见首页卡片与路线对照。</p></section>")
    toc, content = build_toc(content)
    root = "../"
    motif = pick_motif(p)
    cover = motif_svg(motif, p["short"])
    hero = f"""
<section class="hero">
  <div class="hero-wrap">
    <div class="hero-badge">{html.escape(p.get("venue","arXiv 2025 · Preprint"))}</div>
    <h1>{html.escape(p["short"])}</h1>
    <p class="hero-tagline">{html.escape(p.get("hero_tagline",""))}</p>
    <p class="hero-desc">{html.escape(p.get("one_liner",""))}</p>
    <div class="hero-art">{cover}<p class="hero-caption">封面语义图 · 范式隐喻（自绘 SVG）：{html.escape(p.get("route",""))}</p></div>
  </div>
  <div class="scroll-hint"><span>↓</span> Scroll to Read</div>
</section>"""
    body = hero + f"""
<div class="blog-body">
  <div class="blog-container">
    <div class="breadcrumb"><a href="{root}index.html">阅读门户</a><span class="sep">/</span><a href="{root}index.html#{p['category']}">{p['category']}</a><span class="sep">/</span>{html.escape(p["short"])}</div>
    {toc}
    {content}
    <div class="blog-nav">
      <a class="bn-card" href="{root}index.html"><div class="bn-dir">← 返回</div><div class="bn-title">全部解读博客</div></a>
      <a class="bn-card next" href="{root}index.html#routes"><div class="bn-dir">路线对照 →</div><div class="bn-title">看它落在哪条路线</div></a>
    </div>
  </div>
</div>"""
    return page(p["short"] + " · 论文解读", p.get("one_liner",""), root, body)

# ---------------------------------------------------------------- INDEX
def cat_card(p, root):
    motif = pick_motif(p)
    thumb = motif_svg(motif, p["short"])
    tags = "".join(f'<span class="chip">{html.escape(t)}</span>' for t in p.get("tags", [])[:4])
    return f"""<a class="card reveal" href="{root}blogs/{p['slug']}.html">
  <div class="card-tag">{html.escape(p.get('venue','arXiv'))}</div>
  <div style="border-radius:12px;overflow:hidden;margin-bottom:14px">{thumb}</div>
  <h3>{html.escape(p['short'])}</h3>
  <p>{html.escape(p.get('one_liner',''))}</p>
  <div class="card-meta">{tags}</div>
</a>"""

def build_index(data, root=""):
    papers = data["papers"]
    cats = {c["id"]: c for c in data["categories"]}
    def cat_section(cid):
        c = cats[cid]
        items = [p for p in papers if p["category"] == cid]
        cards = "".join(cat_card(p, root) for p in items)
        return f"""
<section class="section" id="{cid}">
  <div class="section-color-blocks"></div>
  <div class="container">
    <div class="section-header reveal">
      <span class="section-tag">{html.escape(c['en'])}</span>
      <h2 class="section-title">{html.escape(c['name'])}</h2>
      <p class="section-subtitle">{html.escape(c['desc'])}</p>
      <p style="color:var(--accent-warm);font-family:var(--font-mono);font-size:12px;margin-top:10px">白板要点 · {html.escape(c['whiteboard'])}</p>
    </div>
    <div class="grid grid-2">{cards}</div>
  </div>
</section>"""

    # web landscape (verified via arXiv API)
    wl_path = os.path.join(BASE, "data", "web_landscape.json")
    wl_data = {}
    if os.path.exists(wl_path):
        with open(wl_path, encoding="utf-8") as f:
            wl_data = json.load(f)
    wlp = wl_data.get("papers", [])
    wlp_sorted = sorted(wlp, key=lambda w: w.get("date", ""), reverse=True)   # recent first
    wlp_sorted = sorted(wlp_sorted, key=lambda w: 0 if w.get("anchor") else 1)  # anchors first (stable)
    wl_rows = ""
    for w in wlp_sorted:
        anchor = ('<span class="chip" style="background:rgba(232,93,78,0.12);color:#E85D4E;'
                  'border-color:rgba(232,93,78,0.35)">★ 白板点名</span>') if w.get("anchor") else ""
        wl_rows += (
            f'<tr><td class="route">{html.escape(w.get("short",""))}<br>'
            f'<span style="font-family:var(--font-mono);font-size:11px;color:var(--text-muted)">'
            f'arXiv {html.escape(w.get("arxiv",""))} · {html.escape(w.get("date",""))}</span> {anchor}</td>'
            f'<td>{html.escape(w.get("route",""))}</td>'
            f'<td>{html.escape(w.get("one_liner",""))}</td></tr>')
    unfound = wl_data.get("unfound", [])
    unfound_note = (f'<p style="color:var(--text-muted);font-size:0.86rem;margin-top:12px">'
                    f'未在 arXiv 检索到（<strong>不臆造</strong>）：{html.escape(", ".join(unfound))}</p>') if unfound else ""
    # explicit whiteboard-name -> arXiv mapping card grid
    wb_names = ["LTX-2", "JavisDiT++", "Ovi", "MOVA", "VDN (Video DeltaNet)", "MiniMax-H3",
                "OmniForcing", "Apollo", "Seedance 2.0", "OmniHuman"]
    by_short = {w.get("short", ""): w for w in wlp}
    def wb_card(name):
        w = by_short.get(name) or {}
        arx = w.get("arxiv", "")
        dt = w.get("date", "")
        line = w.get("one_liner", w.get("route", ""))
        return (f'<div class="card reveal"><div class="card-tag">arXiv {html.escape(arx)} · {html.escape(dt)}</div>'
                f'<h3 style="font-size:1.12rem">{html.escape(name)}</h3>'
                f'<p style="font-size:0.88rem">{html.escape(line[:150])}</p></div>')
    wb_anchor_cards = "".join(wb_card(n) for n in wb_names if by_short.get(n))
    web_block = f"""
<section class="section" id="recent">
  <div class="section-color-blocks"></div>
  <div class="container">
    <div class="section-header reveal">
      <span class="section-tag">Web Landscape · arXiv 核对</span>
      <h2 class="section-title">近半年 <span class="hl">相关论文</span> 谱系</h2>
      <p class="section-subtitle">从白板要点出发，经 arXiv API 逐条核对的联合生成 / 数字人工作（★ = 白板点名模型）。</p>
    </div>
    <div class="table-wrap reveal"><table class="data">
      <thead><tr><th>工作 / arXiv</th><th>路线 / 范式</th><th>定位要点（摘自摘要）</th></tr></thead>
      <tbody>{wl_rows}</tbody>
    </table></div>
    {unfound_note}
    <h3 class="reveal" style="margin-top:40px;font-size:1.35rem">白板点名模型 · 落点</h3>
    <div class="grid grid-4" style="margin-top:18px">{wb_anchor_cards}</div>
  </div>
</section>"""

    # route comparison (from notes)
    route_rows = [
        ("双流／双塔联合生成", "MOVA、Ovi、LTX-2、UniTalking、JoVA、Vorch-Human", "生成过程中如何交互、对齐时间，并平衡语音与视频质量"),
        ("单流极简高效", "Speed by Simplicity", "更少模块换速度，何时简单胜过复杂"),
        ("统一／对齐表示", "AVTok、OmniVAE、Vorch-Human", "tokenizer / codebook / VAE latent 应共享与对齐到什么程度"),
        ("先对齐后共享融合", "NAVA", "模态专属对齐与共享生成如何衔接，如何注入台词与音色"),
        ("自回归 / 渐进分辨率", "TaoMate-HD", "自回归 + 渐进分辨率如何支撑高清长时音视频"),
        ("多声源分轨控制", "Soundwich、Unison", "speech / 背景声 / 音效如何同步生成并独立编辑"),
        ("实时流式数字人", "Hallo-Live、OmniMate、EmbodiedHead、UniLS、Beyond Monologue", "流式延迟、异步双流、听-说交互如何达成实时"),
    ]
    rr = "".join(f'<tr><td class="route">{html.escape(a)}</td><td>{html.escape(b)}</td><td>{html.escape(c)}</td></tr>' for a,b,c in route_rows)
    routes_block = f"""
<section class="section" id="routes">
  <div class="container">
    <div class="section-header reveal">
      <span class="section-tag">Route Comparison</span>
      <h2 class="section-title">路线对照 <span class="hl">矩阵</span></h2>
      <p class="section-subtitle">把所有论文按「代表要研究的问题」归位——这是白板「task angle analysis」的落点。</p>
    </div>
    <div class="table-wrap reveal"><table class="data">
      <thead><tr><th>路线</th><th>代表工作</th><th>对应要研究的问题</th></tr></thead>
      <tbody>{rr}</tbody>
    </table></div>
    <div class="insight-box reveal" style="margin-top:24px">
      <span class="ib-tag">深度洞察</span>
      <h4>白板的两条主轴：S+A 对齐 vs 任务角度</h4>
      <p>白板把「speech-audio alignment（S-A 对齐）」与「task angle analysis（任务角度）」并列为核心分析维度：前者关乎 <strong>Latent / 时间 / 声画同步</strong>的对齐粒度（shared DiT、Bridge、对比对齐、Aligned RoPE），后者关乎把生成拆成 <strong>A/S/V 任务</strong>后如何调度训练与损失（60% Audio / 40% Speech 的 A 分布、into loss / delay、loss function / reward）。</p>
    </div>
  </div>
</section>"""

    # whiteboard key points
    wb_items = [
        ("生成范式", "Sequential（Text→TTS→Speech→VidGen→Video） vs Joint（Vid+Speech 联合生成）。联合生成是主流趋势。", "从串行到联合"),
        ("架构", "DiT 为主干（LTX 2.5 / AV-GM 起点）；双流·双塔·单流·共享 DiT；Joint / Cross Attention；LoRA 适配；into loss / delay。", "DiT 家族"),
        ("模态表示与对齐", "S / V / SV / A 模态分工；S+V 对齐；共享 latent vs 各自 latent；audio latent 远比 video 稠密。", "S-A 对齐"),
        ("数据与场景", "开源数据集 → 单人场景（speaking / singing）；长尾数据；能量/背景声；口型同步过滤与 ASR 台词。", "单人场景"),
        ("评估", "metrics / benchmark / user study；SAV（Speech-AV）与 ASV（AV-Speech）双向任务；Sync、WER、LSE-C、PQ。", "任务角度"),
        ("训练目标", "loss function / reward；Flow Matching、偏好蒸馏（human-centric preference）；跨模态 forcing 从同步噪声到独立噪声。", "损失与奖励"),
    ]
    wb_cards = "".join(f"""
      <div class="card reveal">
        <div class="card-tag">{html.escape(k)}</div>
        <h3 style="font-size:1.15rem">{html.escape(t)}</h3>
        <p>{html.escape(d)}</p>
      </div>""" for k,d,t in wb_items)
    wb_block = f"""
<section class="section" id="whiteboard">
  <div class="section-color-blocks"></div>
  <div class="container">
    <div class="section-header reveal">
      <span class="section-tag">Whiteboard Key Points</span>
      <h2 class="section-title">研究要点 <span class="hl">地图</span></h2>
      <p class="section-subtitle">白板六要点——所有论文都在这张坐标里被梳理、对比与定位。</p>
    </div>
    <div class="double-border reveal" style="padding:22px 26px;margin-bottom:28px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:18px">
      <div style="flex:1;min-width:280px">
        <div class="card-tag">★ 核心 · 白板梳理</div>
        <h3 style="font-size:1.3rem;margin:4px 0 6px">逐模型梳理 · Task Angle × S-A Alignment</h3>
        <p style="color:var(--text-secondary);font-size:0.96rem;margin:0">严格复刻白板例子：LTX-2.3 / JavisDiT++ / OVI / MOVA / VDN / MiniMax-H3 与 OmniForcing / Hallo-Live / Lynn / TaoMate 逐个定位，落点任务角度与语音-音频对齐。</p>
      </div>
      <a class="btn btn-warm" href="blogs/whiteboard-map.html">阅读白板梳理 →</a>
    </div>
    <div class="grid grid-3">{wb_cards}</div>
  </div>
</section>"""

    # taxonomy map
    taxonomy_block = f"""
<section class="section" id="taxonomy">
  <div class="container">
    <div class="section-header reveal">
      <span class="section-tag">Taxonomy</span>
      <h2 class="section-title">分类 <span class="hl">地图</span></h2>
      <p class="section-subtitle">Vid + Speech → Joint Generation：从通用基座到说话人生成的两条主线。</p>
    </div>
    <div class="double-border reveal" style="padding:24px">
      <div class="grid grid-2">
        <div>
          <div class="card-tag">主线一 · {html.escape(cats['av-foundation']['en'])}</div>
          <h3>{html.escape(cats['av-foundation']['name'])}</h3>
          <p>{html.escape(cats['av-foundation']['desc'])}</p>
        </div>
        <div>
          <div class="card-tag">主线二 · {html.escape(cats['speech-video']['en'])}</div>
          <h3>{html.escape(cats['speech-video']['name'])}</h3>
          <p>{html.escape(cats['speech-video']['desc'])}</p>
        </div>
      </div>
    </div>
  </div>
</section>"""

    # hero for index
    idx_hero = f"""
<section class="hero">
  <div class="hero-wrap">
    <div class="hero-badge">Venus · Paper Reading Portal</div>
    <h1>Avatar · Speech</h1>
    <p class="hero-tagline">Vid + Speech → 联合生成 · 论文阅读门户</p>
    <p class="hero-desc">按白板要点，把「音视频联合生成」的论文谱系梳理成一张可导航的知识地图：基础模型 × 语音-视频生成 × 路线对照。</p>
    <div class="hero-art">{motif_svg("dual-stream","hero")}<p class="hero-caption">联合生成范式：视频流 + 音频流 → Joint Attention / Cross Attention 联合去噪</p></div>
    <div style="margin-top:26px">
      <a class="btn btn-primary" href="#library">开始阅读</a>
      <a class="btn btn-outline" href="#routes" style="margin-left:12px">看路线对照</a>
    </div>
  </div>
  <div class="scroll-hint"><span>↓</span> Scroll to Read</div>
</section>"""

    # library: all blogs grid
    lib_cards = "".join(cat_card(p, root) for p in papers)
    library_block = f"""
<section class="section" id="library">
  <div class="container">
    <div class="section-header reveal">
      <span class="section-tag">Reading Library</span>
      <h2 class="section-title">全部 <span class="hl">解读博客</span></h2>
      <p class="section-subtitle">每篇一个深度解读页：方法分解 · Latent 与解码 · 训练与前置 · 优势与证据 · 批判 · 自主科研问题。</p>
    </div>
    <div class="grid grid-3">{lib_cards}</div>
  </div>
</section>"""

    body = (idx_hero + taxonomy_block + cat_section("av-foundation") + cat_section("speech-video")
            + library_block + web_block + routes_block + wb_block)
    return page("Avatar·Speech 音视频联合生成 · 论文阅读门户", data.get("subtitle",""), root, body)

# ---------------------------------------------------------------- MAIN
_AMP = re.compile(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)')
def sanitize(s):
    """Escape lone '&' that are not already part of an HTML entity (keeps &amp; etc.)."""
    return _AMP.sub('&amp;', s)

def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    # write blogs
    for p in data["papers"]:
        html_doc = sanitize(build_blog(p, data["papers"]))
        with open(os.path.join(BLOGS, p["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(html_doc)
        print("blog:", p["slug"])
    # write index
    idx = sanitize(build_index(data, root=""))
    with open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as f:
        f.write(idx)
    print("index.html written")
    # write a root copy pointer? index lives at portal/index.html
if __name__ == "__main__":
    main()
