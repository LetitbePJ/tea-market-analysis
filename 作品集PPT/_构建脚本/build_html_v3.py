# -*- coding: utf-8 -*-
"""生成单文件 HTML 作品集 V3：严格配色规范 + 克制的茶饮线稿点缀。
图表使用 assets_v3 重着色版本；所有分析文字与结论与 PPT 一致，一字未改。
"""
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.join(HERE, "assets_v3")
OUT = os.path.join(HERE, "茶饮门店竞争格局与选址分析.html")

IMG_MAP = {
    "Q1": "q1_city_distribution.png",
    "Q2": "q2_competitor_density.png",
    "Q5": "q5_blue_ocean.png",
    "Q6": "q6_philadelphia_map.png",
    "Q8": "q8_threshold.png",
    "Q9": "q9_robustness.png",
}


def uri(name):
    with open(os.path.join(V3, name), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")


HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>茶饮门店竞争格局与选址分析 · 面试作品集</title>
<style>
:root{
  --dark:#2C4447; --clay:#D48B5C; --paper:#F6F5F0;
  --ink:#444444; --note:#777777;
  --desk:#ECEAE3; --line:#DCD8CE; --shade:#EFEDE7;
  --on-dark:#B7C2C1; --on-dark2:#94A4A3;
  --fs:"PingFang SC","Microsoft YaHei","Hiragino Sans GB",sans-serif;
  --fn:Arial,Helvetica,sans-serif;
  --leaf:url("__MOTIF_LEAF__");
  --leaf-l:url("__MOTIF_LEAF_L__");
  --cup-l:url("__MOTIF_CUP_L__");
  --wave-l:url("__MOTIF_WAVE_L__");
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--desk);color:var(--ink);font-family:var(--fs);
  -webkit-font-smoothing:antialiased;line-height:1.7;font-size:16px}
img{max-width:100%;display:block}
a{color:inherit;text-decoration:none}

#progress{position:absolute;top:0;left:0;height:3px;background:var(--clay);z-index:1;width:0}

/* 定宽画布 */
.page{max-width:1180px;margin:0 auto;background:var(--paper)}

nav{position:fixed;top:0;left:50%;transform:translateX(-50%);width:100%;max-width:1180px;
  height:56px;z-index:90;background:rgba(246,245,240,.95);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--line)}
.nav-in{max-width:1180px;margin:0 auto;height:100%;display:flex;align-items:center;
  justify-content:space-between;padding:0 32px}
.brand{font-weight:700;font-size:15px;letter-spacing:.02em;color:var(--dark)}
.brand span{color:var(--clay)}
.nav-links{display:flex;gap:26px;font-size:13px;color:var(--ink)}
.nav-links a{position:relative;padding:4px 0;transition:color .2s}
.nav-links a:hover,.nav-links a.active{color:var(--clay)}
.nav-links a.active::after{content:"";position:absolute;left:0;right:0;bottom:-2px;height:2px;background:var(--clay)}
.nav-tag{font-family:var(--fn);font-size:11px;color:var(--note);letter-spacing:.08em}

.wrap{max-width:1180px;margin:0 auto;padding:0 32px}
section{padding:104px 0;border-bottom:1px solid var(--line)}
section:last-of-type{border-bottom:none}

.kicker{font-family:var(--fn);font-size:12px;font-weight:700;letter-spacing:.1em;color:var(--clay);margin-bottom:20px}
h2.sec{font-size:clamp(28px,4vw,42px);font-weight:700;line-height:1.25;
  letter-spacing:-.01em;margin-bottom:14px;color:var(--dark)}
.lead{font-size:17px;color:var(--ink);max-width:760px;line-height:1.8}

/* HERO：左茶青灰蓝（线稿暗纹在右上，避开标题），右米白 */
.hero{display:grid;grid-template-columns:38% 62%;padding-top:56px;min-height:620px}
.hero-l{background:var(--dark);color:#fff;padding:64px 48px 48px;
  display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden}
.hero-l::after{content:"";position:absolute;right:-150px;bottom:-30px;width:460px;height:460px;
  background:var(--leaf-l) center/contain no-repeat;opacity:.32;pointer-events:none}
.hero-l::before{content:"";position:absolute;right:0;top:0;bottom:0;width:2px;background:var(--clay)}
.hero-l>*{position:relative;z-index:1}
.hero-eyebrow{font-family:var(--fn);font-size:12px;letter-spacing:.14em;color:var(--on-dark);font-weight:700}
.hero-title{font-size:clamp(36px,4.4vw,56px);font-weight:700;line-height:1.18;margin:56px 0 0;color:#fff}
.hero-rule{width:80px;height:2px;background:var(--clay);margin:34px 0 24px}
.hero-sub{font-size:15px;color:var(--on-dark);line-height:1.8}
.hero-foot{font-family:var(--fn);font-size:13px;color:var(--on-dark2)}
.hero-r{padding:64px 56px 48px 64px;display:flex;flex-direction:column;
  justify-content:center;position:relative;overflow:hidden}
.hero-r::after{content:"";position:absolute;right:-30px;bottom:-30px;width:170px;height:170px;
  background:var(--cup-l) center/contain no-repeat;opacity:.14;pointer-events:none}
.hero-claim{font-size:clamp(27px,3.4vw,42px);font-weight:700;line-height:1.4;margin:0 0 30px;color:var(--dark)}
.hero-claim em{font-style:normal;color:var(--clay)}
.hero-divider{height:1px;background:var(--line);margin-bottom:28px}
.hero-stats{display:flex;flex-direction:column;gap:16px}
.stat{display:flex;align-items:baseline;gap:28px}
.stat-num{font-family:var(--fn);font-size:36px;font-weight:700;color:var(--dark);min-width:150px;line-height:1}
.stat-num.c{color:var(--clay)}
.stat-label{font-size:16px;color:var(--ink)}

/* 目录 */
.toc-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:0 72px;margin-top:44px;position:relative}
.toc-grid::after{content:"";position:absolute;right:-120px;bottom:-40px;width:220px;height:220px;
  background:var(--leaf) center/contain no-repeat;opacity:.7;pointer-events:none}
.toc-item{display:grid;grid-template-columns:88px 1fr;align-items:start;padding:28px 0;border-top:1px solid var(--line)}
.toc-num{font-family:var(--fn);font-size:44px;font-weight:700;line-height:1;color:var(--clay)}
.toc-num.d{color:var(--dark)}
.toc-name{font-size:23px;font-weight:700;margin-bottom:6px;color:var(--dark)}
.toc-desc{font-size:15px;color:var(--ink);line-height:1.6}

/* 证据图：无边框、无色条、无阴影 */
.figure{margin-top:34px}
.figure .cap{font-family:var(--fn);font-size:11px;color:var(--note);letter-spacing:.03em;margin-bottom:12px}
.figure img{width:100%;height:auto}

.finding{display:grid;grid-template-columns:1.12fr .88fr;gap:64px;align-items:start;margin-top:52px}
.finding.rev{grid-template-columns:.86fr 1.14fr}
.side{padding-top:8px}
.big-num{font-family:var(--fn);font-size:clamp(56px,7vw,90px);font-weight:700;line-height:1;color:var(--clay);letter-spacing:-.02em}
.big-num.d{color:var(--dark)}
.big-label{font-size:15px;color:var(--note);margin-top:10px}
.side-rule{height:1px;background:var(--line);margin:28px 0}
.side h3{font-size:19px;font-weight:700;margin-bottom:12px;color:var(--dark)}
.side p{color:var(--ink);font-size:16px;margin-bottom:14px;line-height:1.8}
.side p .mut{color:var(--note);font-size:15px}

/* 判断条：无底色块，仅左侧色线（功能性提示，非装饰） */
.verdict{border-left:3px solid var(--clay);padding:2px 0 2px 18px;margin-top:30px;
  display:grid;grid-template-columns:110px 1fr;align-items:start;gap:8px}
.verdict.d{border-left-color:var(--dark)}
.verdict .lab{font-weight:700;color:var(--clay);font-size:15px}
.verdict.d .lab{color:var(--dark)}
.verdict .txt{font-size:15.5px;line-height:1.7;color:var(--ink)}

/* 数据底座 */
.base-grid{display:grid;grid-template-columns:.9fr 1.1fr;gap:72px;margin-top:48px}
.qrow{display:grid;grid-template-columns:70px 1fr;padding:22px 0;border-top:1px solid var(--line)}
.qtag{font-family:var(--fn);font-size:22px;font-weight:700;color:var(--clay)}
.qtitle{font-size:19px;font-weight:700;color:var(--dark)}
.qdesc{font-size:15px;color:var(--ink);margin-top:4px}
.funnel{display:flex;flex-direction:column;gap:14px}
.fstep{color:#fff;padding:22px 0;text-align:center}
.fstep .n{font-family:var(--fn);font-size:36px;font-weight:700;line-height:1.1}
.fstep .l{font-size:14px;opacity:.92;margin-top:6px}
.fnote{font-size:15px;color:var(--ink);margin-top:24px;line-height:1.8}

/* 转折区：浅色底，仅边角极淡底纹 */
.turn{background:var(--shade);padding:88px 0}
.turn h2.sec{color:var(--clay);font-size:clamp(30px,4.4vw,44px)}
.num3{display:grid;grid-template-columns:repeat(3,1fr);gap:48px;margin-top:40px}
.n3{border-top:2px solid var(--clay);padding-top:16px}
.n3 .lab{font-size:13px;color:var(--note);margin-bottom:8px}
.n3 .val{font-family:var(--fn);font-size:clamp(22px,2.6vw,32px);font-weight:700;color:var(--dark)}
.n3 .val.c{color:var(--clay)}
.turn .verdict{margin-top:40px}

/* 对照 */
.compare{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-top:48px}
.cbox{padding:6px 0 8px 22px;border-left:3px solid var(--clay)}
.cbox.win{border-left-color:var(--dark)}
.cbox .ch{font-size:21px;font-weight:700;color:var(--clay);margin-bottom:18px}
.cbox.win .ch{color:var(--dark)}
.cbox .cv{font-family:var(--fn);font-size:clamp(28px,3.4vw,40px);font-weight:700;color:var(--dark);line-height:1.2;margin-bottom:20px}
.cbox p{color:var(--ink);font-size:16px;margin-bottom:12px;line-height:1.8}
.cbox p b{color:var(--dark)}
.cfoot{font-size:14px;color:var(--note);margin-top:24px}

/* 排名 */
.rank{margin-top:24px}
.rrow{display:grid;grid-template-columns:60px 1fr 100px;align-items:center;padding:18px 0;border-top:1px solid var(--line)}
.rrow .rn{font-family:var(--fn);font-size:21px;font-weight:700;color:var(--clay)}
.rrow .rn.d{color:var(--dark)}
.rrow .city{font-size:19px;font-weight:700;color:var(--dark)}
.rrow .pct{font-family:var(--fn);font-size:20px;font-weight:700;text-align:right;color:var(--clay)}
.rrow .pct.d{color:var(--dark)}

/* 稳健性数字 */
.robust{display:grid;grid-template-columns:1fr 1fr;gap:64px;margin-top:44px}
.rblock{border-top:2px solid var(--dark);padding-top:16px}
.rblock.p{border-top-color:var(--clay)}
.rblock .lab{font-size:13px;color:var(--note);margin-bottom:10px}
.rblock .val{font-family:var(--fn);font-size:clamp(22px,2.8vw,32px);font-weight:700;color:var(--dark)}
.rblock.p .val{color:var(--clay)}

/* 结尾：深色 + 同色系线稿暗纹 + 蒙版 */
.ending{background:var(--dark);color:#fff;padding:100px 0 72px;position:relative;overflow:hidden}
.ending::before{content:"";position:absolute;top:0;left:0;right:0;height:5px;background:var(--clay)}
.ending::after{content:"";position:absolute;right:-160px;bottom:-80px;width:600px;height:600px;
  background:var(--leaf-l) center/contain no-repeat;opacity:.3;pointer-events:none}
.ending .wrap{position:relative;z-index:1}
.ending h2{font-size:clamp(38px,5.4vw,68px);font-weight:700;line-height:1.15;color:#fff}
.ending .sub{font-size:clamp(18px,2.2vw,23px);color:var(--on-dark);margin:22px 0 56px}
.ending .bar{width:110px;height:3px;background:var(--clay);margin-bottom:26px}
.step{display:grid;grid-template-columns:80px 200px 1fr;gap:16px;align-items:center;
  padding:26px 0;border-top:1px solid rgba(255,255,255,.12)}
.step .sn{font-family:var(--fn);font-size:33px;font-weight:700;color:var(--clay)}
.step .st{font-size:23px;font-weight:700;color:#fff}
.step .sd{font-size:16px;color:var(--on-dark)}
.endnote{margin-top:52px;padding-top:24px;border-top:1px solid rgba(255,255,255,.12);
  display:flex;justify-content:space-between;gap:24px;font-size:13px;color:var(--on-dark2)}

footer{background:var(--paper);padding:36px 0;text-align:center;font-size:13px;color:var(--note)}

.reveal{opacity:0;transform:translateY(22px);transition:opacity .7s ease,transform .7s ease}
.reveal.in{opacity:1;transform:none}

#top{position:fixed;right:28px;bottom:28px;width:46px;height:46px;
  background:var(--dark);color:#fff;border:none;cursor:pointer;font-size:20px;
  opacity:0;pointer-events:none;transition:opacity .3s;z-index:80}
#top.show{opacity:1;pointer-events:auto}

@media(max-width:1240px){body{background:var(--paper)}.page{max-width:100%}nav{max-width:100%}}
@media(max-width:900px){
  .nav-links{display:none}
  .hero{grid-template-columns:1fr}
  .hero-l{min-height:auto;padding:72px 32px 56px}
  .hero-title{margin-top:36px}
  .hero-r{padding:72px 32px 56px}
  .finding,.finding.rev,.base-grid{grid-template-columns:1fr;gap:36px}
  .toc-grid{grid-template-columns:1fr}
  .num3{grid-template-columns:1fr;gap:24px}
  .compare,.robust{grid-template-columns:1fr}
  .verdict{grid-template-columns:90px 1fr}
  .step{grid-template-columns:56px 1fr;gap:8px}
  .step .sd{grid-column:2}
  section{padding:72px 0}
}
</style>
</head>
<body>
<nav>
  <div id="progress"></div>
  <div class="nav-in">
    <div class="brand">茶饮门店分析 <span>/</span> 作品集</div>
    <div class="nav-links">
      <a href="#hero">封面</a><a href="#data">背景与数据</a>
      <a href="#finding">核心发现</a><a href="#robust">稳健性</a><a href="#end">结论</a>
    </div>
    <div class="nav-tag">DATA ANALYTICS · 2026</div>
  </div>
</nav>

<div class="page">
<header class="hero" id="hero">
  <div class="hero-l">
    <div class="hero-eyebrow">DATA ANALYTICS / PORTFOLIO</div>
    <div>
      <h1 class="hero-title">茶饮门店<br>竞争格局与<br>选址分析</h1>
      <div class="hero-rule"></div>
      <div class="hero-sub">真实数据 · 自建特征 · 自我推翻</div>
    </div>
    <div class="hero-foot">潘约翰 &nbsp;|&nbsp; 2026</div>
  </div>
  <div class="hero-r">
    <div class="hero-claim">竞品数量是优质商圈的<br><em>症状，不是病因</em></div>
    <div class="hero-divider"></div>
    <div class="hero-stats">
      <div class="stat"><span class="stat-num">150,346</span><span class="stat-label">家真实商户样本</span></div>
      <div class="stat"><span class="stat-num">477</span><span class="stat-label">家奶茶门店为分析主体</span></div>
      <div class="stat"><span class="stat-num c">11</span><span class="stat-label">个蓝海候选城市</span></div>
    </div>
  </div>
</header>

<section id="contents">
  <div class="wrap reveal">
    <div class="kicker">CONTENTS</div>
    <h2 class="sec">四个部分，讲清一个决策问题</h2>
    <div class="toc-grid">
      <div class="toc-item"><div class="toc-num">01</div>
        <div><div class="toc-name">背景与数据</div><div class="toc-desc">真实商户替代模拟数据，竞品密度用经纬度自建</div></div></div>
      <div class="toc-item"><div class="toc-num d">02</div>
        <div><div class="toc-name">核心发现</div><div class="toc-desc">市场集中、竞争两极分化，一个漂亮结论被推翻</div></div></div>
      <div class="toc-item"><div class="toc-num d">03</div>
        <div><div class="toc-name">稳健性与边界</div><div class="toc-desc">换半径、做 bootstrap，检验结论是否站得住</div></div></div>
      <div class="toc-item"><div class="toc-num">04</div>
        <div><div class="toc-name">结论</div><div class="toc-desc">先选市场、再选商圈，不把竞品数量当信号</div></div></div>
    </div>
  </div>
</section>

<section id="data">
  <div class="wrap">
    <div class="reveal">
      <div class="kicker">01 / DATA FOUNDATION</div>
      <h2 class="sec">用真实商户数据回答选址问题，而不是模拟数据</h2>
    </div>
    <div class="base-grid reveal">
      <div>
        <div style="font-size:15px;color:var(--note);font-weight:700;margin-bottom:10px">要回答的三个问题</div>
        <div class="qrow"><div class="qtag">Q1</div><div><div class="qtitle">市场格局</div><div class="qdesc">茶饮门店集中在哪些城市</div></div></div>
        <div class="qrow"><div class="qtag">Q2</div><div><div class="qtitle">竞争效应</div><div class="qdesc">周边竞品越多，生意越差吗</div></div></div>
        <div class="qrow"><div class="qtag">Q3</div><div><div class="qtitle">选址决策</div><div class="qdesc">哪些市场需求已验证、供给未饱和</div></div></div>
      </div>
      <div>
        <div style="font-size:15px;color:var(--note);font-weight:700;margin-bottom:18px">数据底座 / Yelp Open Dataset</div>
        <div class="funnel">
          <div class="fstep" style="background:var(--dark)"><div class="n">150,346</div><div class="l">商户总数</div></div>
          <div class="fstep" style="background:#3A5659;width:88%;align-self:center"><div class="n">7,069</div><div class="l">茶饮门店（三类业态）</div></div>
          <div class="fstep" style="background:var(--clay);width:76%;align-self:center"><div class="n">477</div><div class="l">奶茶店 · 分析主体</div></div>
        </div>
        <div class="fnote">覆盖 8 个都市圈、15 州/省。无销量、无开店日期——需求只能用累计评论数代理。</div>
      </div>
    </div>
    <div class="verdict reveal"><div class="lab">关键前提</div><div class="txt">竞品密度数据里没有，必须用经纬度自己算；需求是代理变量，结论要讲边界。</div></div>
  </div>
</section>

<section id="finding" style="padding-bottom:0">
  <div class="wrap">
    <div class="reveal">
      <div class="kicker">02 / FINDING 01 — 02</div>
      <h2 class="sec">市场高度集中，竞争呈两极分化</h2>
      <p class="lead">先看结构，再看效应——这是后面所有判断的起点。</p>
    </div>
    <div class="finding reveal">
      <div class="figure"><div class="cap">EVIDENCE / 茶饮门店 TOP10 城市</div><img src="__IMG_Q1__" alt="茶饮门店城市分布"></div>
      <div class="side">
        <div class="big-num">956</div>
        <div class="big-label">家茶饮门店 · 费城（最大单一市场）</div>
        <div class="side-rule"></div>
        <h3>前 5 城占 34%</h3>
        <p>头部市场值得优先进入。但城市字段由用户填写，同一都市圈可能被拆成多个城市（费城 / Cherry Hill）。</p>
        <p class="mut">集中度数字受口径影响，非精确市占率。</p>
      </div>
    </div>
    <div class="finding rev reveal">
      <div class="side">
        <div class="big-num d">38%</div>
        <div class="big-label">门店 1km 内零竞品 · 独立区隔市场</div>
        <div class="side-rule"></div>
        <div class="big-num" style="font-size:62px">30%</div>
        <div class="big-label">门店 1km 内 ≥3 家 · 贴身竞争</div>
      </div>
      <div class="figure"><div class="cap">EVIDENCE / 1km 内竞品数分布</div><img src="__IMG_Q2__" alt="竞品密度分布"></div>
    </div>
    <div class="verdict reveal"><div class="lab">判断</div><div class="txt">市场不是均匀的，必须分组看——密度用 Haversine 球面距离自建，1km≈步行 10 分钟商圈。</div></div>
  </div>
</section>

<section class="turn" id="turn">
  <div class="wrap">
    <div class="reveal">
      <div class="kicker">02 / THE TURNING POINT</div>
      <h2 class="sec">初版结论“竞品越多越火”是假的</h2>
      <p class="lead">细粒度曲线非单调；23 家高密度店全部挤在费城唐人街一个街区。</p>
    </div>
    <div class="figure reveal" style="margin-top:44px">
      <div class="cap">EVIDENCE / 全样本曲线 · 剔除簇后 · 费城内对照</div>
      <img src="__IMG_Q8__" alt="阈值检验三联图">
    </div>
    <div class="num3 reveal">
      <div class="n3"><div class="lab">相关系数 r</div><div class="val">0.19 → 0.016</div></div>
      <div class="n3"><div class="lab">分组差异 p</div><div class="val">0.049 → 0.76</div></div>
      <div class="n3"><div class="lab">高密度门店来源</div><div class="val c">19107 · 23 家</div></div>
    </div>
    <div class="verdict reveal"><div class="lab">关键</div><div class="txt">23 家本质是 1 个观测（均评论 186 vs 费城其他 56）。竞品数量是优质商圈的症状，不是病因。</div></div>
    <p class="cfoot">口径：剔除 competitors_1km ≥ 20 的伪重复簇后重算；Mann-Whitney p&lt;0.001</p>
  </div>
</section>

<section id="finding2" style="padding-top:104px">
  <div class="wrap">
    <div class="reveal">
      <div class="kicker">02 / FINDING 03</div>
      <h2 class="sec">同一个检验，一个被推翻、一个幸存</h2>
    </div>
    <div class="compare reveal">
      <div class="cbox">
        <div class="ch">被推翻 · 热度结论</div>
        <div class="cv">r &nbsp;0.19 → 0.016</div>
        <p>剔除唐人街簇后相关性归零，分组差异 p 从 0.049 升到 0.76。</p>
        <p><b>密度不提升需求——初版判断被自己的检验推翻。</b></p>
      </div>
      <div class="cbox win">
        <div class="ch">幸存 · 评分结论</div>
        <div class="cv">p &nbsp;0.0001 → 0.0017</div>
        <p>独占区 4.18 → 最卷区 3.86，剔除簇后仍显著（H=15.19）。</p>
        <p><b>评分分化是全样本现象，不是单一街区伪造的。</b></p>
      </div>
    </div>
    <div class="verdict d reveal"><div class="lab">诚实的价值</div><div class="txt">同样的样本、同样的检验流程，一个被推翻、一个幸存——说明检验不是走过场。</div></div>
    <p class="cfoot reveal">评分下降的两种机制（低质店在无竞争区存活 / 高竞争区评分更分化）单期截面无法区分，属后续研究方向。</p>
  </div>
</section>

<section id="blue" style="padding-top:0;border-bottom:none">
  <div class="wrap">
    <div class="reveal">
      <div class="kicker">02 / FINDING 04</div>
      <h2 class="sec">蓝海候选池 11 城：前三名排序稳定</h2>
    </div>
    <div class="finding reveal">
      <div class="figure"><div class="cap">EVIDENCE / 需求 × 供给气泡图</div><img src="__IMG_Q5__" alt="蓝海城市气泡图"></div>
      <div class="side">
        <h3>蓝海指数（口径已统一）</h3>
        <p style="font-size:19px;font-weight:700;color:var(--dark)">需求强度 ×（1 − 奶茶渗透率）</p>
        <div class="side-rule"></div>
        <div style="font-size:14px;color:var(--note);margin-bottom:8px">bootstrap 1000 次 · 进前三概率</div>
        <div class="rank">
          <div class="rrow"><div class="rn">01</div><div class="city">Reno</div><div class="pct">87%</div></div>
          <div class="rrow"><div class="rn d">02</div><div class="city">New Orleans</div><div class="pct d">82%</div></div>
          <div class="rrow"><div class="rn d">03</div><div class="city">Indianapolis</div><div class="pct d">79%</div></div>
        </div>
        <p class="mut" style="margin-top:18px">入选门槛：奶茶店≥5、茶饮店≥50。口径修正后候选池从 18 城收敛到 11 城。</p>
      </div>
    </div>
    <div class="verdict reveal"><div class="lab">边界</div><div class="txt">只能讲“候选池排名”，不能讲“第一名绝对最好”。</div></div>

    <div class="finding rev reveal" style="margin-top:96px">
      <div class="side">
        <h3>费城 19107：需求被验证的样本</h3>
        <p>23 家奶茶店聚集，均评论 186 条——城市内部的热度差异远大于城市之间。</p>
        <p>但这批店与伪重复簇是同一批：热度高说明需求存在，也可能意味着市场接近饱和。</p>
        <div class="side-rule"></div>
        <p><span style="font-weight:700;color:var(--dark)">正确用法：</span>先确认“这里有被验证的需求”，再叠加竞品间距、租金、铺位可得性做二次筛选。</p>
      </div>
      <div class="figure"><div class="cap">EVIDENCE / 费城奶茶店地理分布</div><img src="__IMG_Q6__" alt="费城门店散点"></div>
    </div>
    <div class="verdict reveal"><div class="lab">不推荐</div><div class="txt">数据给方向，不给最终答案——不直接推荐在 19107 开店。</div></div>
  </div>
</section>

<section id="robust">
  <div class="wrap">
    <div class="reveal">
      <div class="kicker">03 / ROBUSTNESS</div>
      <h2 class="sec">结论不依赖参数选择，也不依赖单一城市排名</h2>
    </div>
    <div class="figure reveal" style="margin-top:44px">
      <div class="cap">EVIDENCE / 半径敏感性 · bootstrap 稳定性</div>
      <img src="__IMG_Q9__" alt="稳健性检验双图">
    </div>
    <div class="robust reveal">
      <div class="rblock"><div class="lab">半径敏感性 · 剔除簇后 r</div><div class="val">0.046 / 0.016 / −0.028</div></div>
      <div class="rblock p"><div class="lab">bootstrap 进前三概率</div><div class="val">Reno 87% · NOLA 82%</div></div>
    </div>
    <p class="cfoot reveal">三档半径（0.5/1/2km）下 p 均 &gt;0.05，“密度不提升需求”稳健；但评论数是累计值，含资历偏差——老店天然占优，这是 V2 首要待办。</p>
  </div>
</section>

<section class="ending" id="end">
  <div class="wrap">
    <div class="reveal">
      <div class="bar"></div>
      <h2>别怕竞品，别信竞品</h2>
      <div class="sub">先选市场，再选商圈，不把竞品数量当信号</div>
    </div>
    <div class="steps reveal">
      <div class="step"><div class="sn">01</div><div class="st">选市场</div><div class="sd">优先进入需求旺、奶茶店少的蓝海候选池</div></div>
      <div class="step"><div class="sn">02</div><div class="st">选商圈</div><div class="sd">进入需求已被验证的成熟商圈，但不追竞品数量</div></div>
      <div class="step"><div class="sn">03</div><div class="st">筛铺位</div><div class="sd">下沉到街区粒度，叠加租金与铺位可得性</div></div>
    </div>
    <div class="endnote"><span>限制：缺租金与开店成本，结论只谈需求侧，落地需实地验证。</span><span>14 / 14</span></div>
  </div>
</section>

<footer>数据来源：Yelp Open Dataset（2018/2022 快照） · 含伪重复识别、稳健性检验与自我推翻</footer>
</div>

<button id="top" title="回到顶部">↑</button>

<script>
const prog=document.getElementById('progress');
const topBtn=document.getElementById('top');
function onScroll(){
  const h=document.documentElement;
  const p=h.scrollTop/(h.scrollHeight-h.clientHeight)*100;
  prog.style.width=p+'%';
  topBtn.classList.toggle('show',h.scrollTop>600);
}
window.addEventListener('scroll',onScroll,{passive:true});onScroll();
const io=new IntersectionObserver((es)=>{
  es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})
},{threshold:.12});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
const links=[...document.querySelectorAll('.nav-links a')];
const ids=links.map(a=>a.getAttribute('href').slice(1));
const io2=new IntersectionObserver((es)=>{
  es.forEach(e=>{if(e.isIntersecting){
    links.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+e.target.id));
  }})
},{rootMargin:'-45% 0px -50% 0px'});
ids.forEach(id=>{const el=document.getElementById(id);if(el)io2.observe(el)});
topBtn.onclick=()=>window.scrollTo({top:0,behavior:'smooth'});
</script>
</body>
</html>
"""


def main():
    html = HTML
    for key, fname in IMG_MAP.items():
        html = html.replace("__IMG_%s__" % key, uri(fname))
    motifs = {
        "__MOTIF_LEAF__": uri("motif_leaf.png"),
        "__MOTIF_LEAF_L__": uri("motif_leaf_light.png"),
        "__MOTIF_CUP_L__": uri("motif_cup_light.png"),
        "__MOTIF_WAVE_L__": uri("motif_wave_light.png"),
    }
    for key, val in motifs.items():
        html = html.replace(key, val)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("已生成:", OUT)
    print("大小: %.1f KB" % (os.path.getsize(OUT) / 1024))
    print("剩余占位符:", html.count("__IMG_") + html.count("__MOTIF_"))


if __name__ == "__main__":
    main()
