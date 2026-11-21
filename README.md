# Avatar·Speech — 音视频联合生成论文阅读门户

> 按白板要点梳理「Vid + Speech → 联合生成」的论文谱系 · 风格锁定 **Venus 可组合设计系统**（配方 A · 浮世绘蓝调）

一个**论文深度解读博客 + 阅读门户**：把音视频联合生成 / 数字人（说话人视频）方向的论文做成深度解读，并按研究要点组织成可导航的知识地图。

**🔗 在线浏览：** https://yetbye.github.io/Avatar-Speech/

## 规模

- **33 篇深度解读博客** · 合计 **298 章节 / 196 自绘 SVG / 159 深度洞察框 / 115 自主科研问题 / 69 代码附录**
- 覆盖 **本地 11 篇论文 + 2 篇路线总览 + 1 篇白板逐模型梳理 + 19 篇近半年论文**（全部经 arXiv 原文抽取撰写）
- **白板要点地图 + 路线对照矩阵**（生成范式 / 架构 / S-A 对齐 / 数据场景 / 评估 / 训练目标）

## 分类（Taxonomy）

| 主线 | 含义 | 白板要点 |
|---|---|---|
| **音视频基础模型** `av-foundation` | 通用联合生成基座：双流 / 单流 / 统一 tokenizer / 跨模态对齐 | DiT 架构 · LTX 2.5 / AV-GM · A 分布 · SAV / ASV |
| **语音-视频生成** `speech-video` | 说话人 / 数字人：口型、听-说、实时流式、表情身份 | S+V 对齐 · 单人场景 · 长尾数据 · user study |

交叉分析维度：**task angle analysis（任务角度）** · **s-a alignment（语音-音频对齐）**。

## 近半年论文（19 篇，原文级解读）

LTX-2 · Ovi · Apollo · MiniMax-H3（评测论文）· MOVA · Video DeltaNet (VDN) · OmniForcing ·
Omni-LiveAvatar · FlowLong · LeapTalk · JAVIS · Salt++ · OmniHuman（数据集）·
JavisDiT (ICLR 2026) · JavisDiT++ (ICLR 2026) · AVC-Reward · Seedance 2.0（模型卡）·
Lynn = LynnReal-Omni · Duo（全双工交互世界模型）

## 目录结构

```
.
├─ index.html          # 阅读门户首页（分类地图 · 图书馆 · 近半年 · 路线对照 · 白板要点）
├─ css/
│  ├─ venus.css        # Venus 可组合设计系统（配方 A · 浮世绘蓝调）
│  └─ blog.css         # 解读博客布局（Hero 模板 A）
├─ blogs/<slug>.html   # 33 篇深度解读博客
├─ content/<slug>.html # 每篇正文片段（HTML 组件套件）
├─ data/
│  ├─ papers.json      # 论文元数据 + 分类 + 路线
│  └─ web_landscape.json
└─ render.py           # 渲染管线：data + content → blogs + index
```

## 本地运行

```bash
python -m http.server 8790
# 打开 http://127.0.0.1:8790/
```

或直接打开 `index.html`（相对链接；字体与 MathJax 走 CDN，需联网）。

## 重新生成

```bash
python render.py
```

读取 `data/*.json`（元数据）与 `content/*.html`（正文），生成 `blogs/*.html` 与 `index.html`。

## 写作与严谨性

每篇解读遵循深度门控：≥ceil(N/3) 章、≥5 自绘内联 SVG、≥3 深度洞察框、≥2 代码附录（标注可信度）、独立「自主科研问题」章、批判评估、公式原文核对。

- 事实来自各论文原文抽取，不确定处标注「论文表述」。
- 近半年论文经 **arXiv API 逐条核对**，避免张冠李戴（如 MiniMax-H3 为评测论文、Seedance 2.0 为模型卡、Lynn = LynnReal-Omni）。
- 封面为**自绘语义 SVG 范式隐喻**（本环境无图像生成工具）。

## 说明

本仓库仅含**原创的解读正文、设计系统与站点代码**，不含任何论文 PDF 或原文全文（受版权保护的论文版权归原作者/出版方所有）。引用论文数据请以原始 arXiv 条目为准。
