# 论文解读博客 · 内容写作规范 (Content Spec)

为 `portal/content/<slug>.html` 编写**内容 HTML 片段**。渲染器已自动生成 Hero、导航、目录、页脚，
你只需写 `<section class="b-section">` 正文块。**不要**写 `<!DOCTYPE>`、`<head>`、`<body>`、`<nav>`。
风格锁 Venus（浮世绘蓝调）。目标：深度解读，而非论文摘要。

## 硬性深度要求（paper-reading-blog skill v5）
1. **章节量**：N 页论文至少 `ceil(N/3)` 个 `<section class="b-section">` 章节。
2. **每章 ≥ 2 个深度元素**（设计 rationale / 数学直觉 / 架构洞察 / 替代方案分析 / 跨论文连接 / 批判评估）。实验展示章可降为 1。
3. **≥ 5 个自绘内联 SVG**：范式对比 / 架构流 / 评估框架 / 因果链 / 概念关系图等（用下面 figure 组件）。
4. **≥ 2 个代码/伪代码块**（放文末「代码附录」章），每个标注 `[示意性实现]` 或 `[可运行实现]`。
5. **≥ 3 个深度洞察框**（insight-box）。
6. **专门一章「自主科研问题」**：3–5 个问题，每个含理论分析 + 连接 + 探究方向（用 research-question 组件）。
7. **批判评估**：不只夸，指出代价/局限 + 证据。
8. **公式**：从原文抽取，系数/符号务必核对；给直觉解释（用 formula 组件）。
9. Hero 不重复（渲染器已生成），正文开头用 lead 段落点明核心。

## 组件套件（Class 必须完全一致）

**章节**（每章带编号）：
```html
<section class="b-section">
  <h2><span class="num">01</span> 章节标题</h2>
  <p class="lead">首段（仅第 1 章用 lead）。</p>
  <p>普通段落，<strong>重点</strong>加粗。</p>
</section>
```

**深度洞察框**：
```html
<div class="insight-box"><span class="ib-tag">深度洞察</span>
  <h4>标题</h4><p>分析内容（设计哲学 / 理论联系 / 跨领域连接）。</p></div>
```

**批判评估卡**：
```html
<div class="critique-card"><span class="cc-tag">批判评估</span>
  <h4>标题</h4><p>代价 / 局限 + 具体证据或数学论据。</p></div>
```

**自主科研问题**：
```html
<div class="research-question"><span class="rq-tag">自主科研问题 · Q1</span>
  <h4>问题标题</h4>
  <div class="rq-body"><p><strong>未知与意义：</strong>…</p>
  <p><strong>理论分析：</strong>…</p><p><strong>连接：</strong>…</p><p><strong>探究方向：</strong>…</p></div></div>
```

**公式卡**（MathJax，用 `$$...$$` 或 `\(...\)`）：
```html
<div class="formula-card"><div class="f-label">Eq.1 · Flow Matching 目标</div>
  <div>$$ \mathcal{L}=\mathbb{E}_{t,x_0,x_1}\|v_\theta(x_t,t)-(x_1-x_0)\|^2 $$</div>
  <div class="f-intuition"><strong>直觉：</strong>…变量定义…</div></div>
```

**代码块**（放文末；先标注可信度）：
```html
<div class="code-cred skel">[示意性实现]</div>
<pre class="code-block"><span class="cm"># 注释</span>
<span class="kw">def</span> <span class="fn">forward</span>(self, x):
    <span class="kw">return</span> self.proj(x)</pre>
```

**自绘 SVG 图**（5+，宽 800 视窗，配色用 #1B4B6F/#5A8F7B/#E85D4E/#C9A86C/#2C3E50）：
```html
<div class="figure"><svg viewBox="0 0 800 360" xmlns="http://www.w3.org/2000/svg">
  <!-- 节点/连线/文字 -->
</svg><div class="figcap"><b>图 1</b> · 说明文字（点明它把哪个抽象概念具象化）</div></div>
```

**系统分解 def-grid**（Latent 与解码 / 训练与前置 等）：
```html
<div class="def-grid">
  <div class="def-item"><div class="dt">Latent 与解码</div>
    <div class="dd">…<span class="alt">替代方案：…</span></div></div>
  <div class="def-item"><div class="dt">训练与前置</div><div class="dd">…</div></div>
</div>
```

**流程条（pipeline）**：
```html
<div class="pipeline"><span class="pipe-step">Text</span><span class="pipe-arrow">→</span>
  <span class="pipe-step alt">TTS</span><span class="pipe-arrow">→</span><span class="pipe-step">Speech</span></div>
```

**表格**：
```html
<div class="table-wrap"><table class="data">
  <thead><tr><th>路线</th><th>工作</th><th>问题</th></tr></thead>
  <tbody><tr><td class="route">…</td><td>…</td><td>…</td></tr></tbody></table></div>
```

## 推荐章节骨架（按需裁剪/合并，勿硬凑）
01 一句话读懂 & 问题动机 · 02 范式定位（sequential vs joint，配 SVG 范式对比）
03 系统分解（架构 + def-grid + 架构流 SVG）· 04 关键公式（formula 卡）
05 Latent 与解码（def-grid + 对齐 SVG）· 06 训练与前置 · 07 优势与证据（表格+解读）
08 深度洞察 & 批判评估 · 09 自主科研问题 · 10 代码附录（code 块）

## 注意
- 语言：中文，术语可保留英文。
- SVG 内文字用中文标签，配色统一，`<text>` 用 `font-family="Noto Sans SC,sans-serif"`。
- 事实（数字、模块名、超参）以 `_extracted` 原文为准，勿臆造；不确定处标注「论文表述」。
- 只输出 HTML 片段正文（从第一个 `<section class="b-section">` 开始）。
