#!/usr/bin/env python3
"""Generate find-a-tool.html: three questions (role, size of the work, what's going on) that recommend three tools.

NEEDS below maps each situation to a Scenario Playbook entry (_content/scenarios.md), whose tools are the candidates.
They're ranked towards the role's tools (ROLES in build_roles.py) and the size's starter kit (STARTER_KITS in
build_recipes.py). Every combination is worked out here, at build time, and checked; the page only looks it up.

Run:  python3 _generator/build_picker.py
"""
import json
import re
import sys
from html import escape, unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402  (where each file lives; see paths.py)
from build_roles import TOOLS, ROLES, FONT_URL  # noqa: E402
from build_recipes import STARTER_KITS  # noqa: E402
from build_scenarios import parse  # noqa: E402
from brand import ACCENT, NAVY, CREDIT  # noqa: E402

OUT = Path(__file__).resolve().parent.parent

# (id, what the person sees, Scenario Playbook title or None, tools to use when there's no scenario)
NEEDS = [
    ("start", "We're starting something new", "A new team doesn't know where to start", []),
    ("stuck", "Lots is started, little gets finished", "Lots of work is started but little is finished", []),
    ("agree", "We can't agree what to build", "Nobody can agree what to build next", []),
    ("value", "We're not sure we're building the right thing", "Users aren't using what we built", []),
    ("deadline", "A deadline is putting us under pressure", "The deadline has just been moved earlier", []),
    ("interrupt", "Urgent work keeps interrupting us", "Urgent work keeps interrupting the iteration", []),
    ("priorities", "Priorities keep changing under us", "A senior stakeholder keeps overriding priorities", []),
    ("teams", "Teams keep blocking each other", "Teams keep blocking each other", []),
    ("release", "Releases are slow or scary", "Releases are slow, scary and happen late at night", []),
    ("quality", "Bugs keep reaching users", "Bugs keep reaching production", []),
    ("retro", "Our retros have gone stale", "Retrospectives have gone stale", []),
    ("morale", "Morale is low", "Morale is low and people seem disengaged", []),
    ("change", "A change is meeting resistance", "A change is meeting resistance", []),
    ("improve", "We just want to get better", None, ["health", "marginal", "retro", "experiment", "lean"]),
]
SIZES = [(f"s{i}", name, sub) for i, (name, sub, *_r) in enumerate(STARTER_KITS)]

slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")  # same as build_scenarios.py's anchors
SCENARIOS = {s["title"]: s for area in parse() for s in area["items"]}
INDEX = paths.read_index()
BLURB = {m.group(2): unescape(re.sub(r"<[^>]+>", "", m.group(1)))
         for m in re.finditer(r'<div class="body"><h3>.*?</h3><p>(.*?)</p>.*?class="primary" href="([^"]+)"', INDEX)}
for _id, _label, title, fallback in NEEDS:
    assert title is None or title in SCENARIOS, f"no scenario called “{title}”"
    assert all(k in TOOLS for k in fallback)


def recommend(role, size, need):
    """Three tool keys, with a reason for each, for one combination. role is None for "not sure"."""
    _nid, _label, title, fallback = need
    cands = SCENARIOS[title]["tools"] if title else fallback
    _name, _sub, _col, kit_start, kit_grow = STARTER_KITS[size]
    kit_start, kit_grow = [k for k, _ in kit_start], [k for k, _ in kit_grow]
    start, also = (role[3], role[4]) if role else ([], [])
    score = {}
    for i, k in enumerate(cands):
        score[k] = 10 - i + (3 if k in start else 1 if k in also else 0) + (2 if k in kit_start else 1 if k in kit_grow else 0)
    picks = sorted(score, key=lambda k: -score[k])[:3]
    for extra in list(start) + kit_start:  # top up when a scenario lists fewer than three tools
        if len(picks) == 3:
            break
        if extra not in picks:
            picks.append(extra)
    out = []
    for k in picks:
        why = []
        if k in cands:
            why.append("recommended for this situation" if title else "a good place to start improving")
        if k in start:
            why.append(f"a starting tool for {role[1]}s" if not role[1].endswith("s") else f"a starting tool for {role[1]}")
        elif k in also:
            why.append("useful in your role")
        if k in kit_start:
            why.append(f"in the {STARTER_KITS[size][0].lower()} starter kit")
        out.append([k, "; ".join(why) or "a strong companion tool"])
    assert len(out) == 3 and len({k for k, _ in out}) == 3, (role, size, need)
    return out


def build():
    roles = [(r[0], r[1].split(" / ")[0]) for r in ROLES] + [("any", "Not sure, or something else")]
    results = {}
    for rid, _ in roles:
        role = next((r for r in ROLES if r[0] == rid), None)
        for si in range(len(STARTER_KITS)):
            for need in NEEDS:
                results[f"{rid}|s{si}|{need[0]}"] = recommend(role, si, need)
    used = sorted({k for v in results.values() for k, _ in v})
    tools = {}
    for k in used:
        title, board, guide, _p = TOOLS[k]
        ex = f"worked-example-{board}"
        # links from find-a-tool.html (at the site root), since the page builds them in JavaScript
        link = lambda name: paths.href("find-a-tool.html", name)
        tools[k] = {"t": title, "b": link(board), "g": link(guide) if guide else "", "d": BLURB.get(board, ""),
                    "x": link(ex) if paths.path(ex).exists() else ""}
    needs = {n[0]: {"label": n[1], "sc": slug(n[2]) if n[2] else "", "st": n[2] or ""} for n in NEEDS}
    sizes = {sid: {"label": name, "sub": sub} for sid, name, sub in SIZES}
    data = json.dumps({"roles": roles, "sizes": sizes, "needs": needs, "tools": tools, "results": results},
                      ensure_ascii=False, separators=(",", ":"), sort_keys=True).replace("</", "<\\/")
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Find a Tool</title>
<link rel="stylesheet" href="{FONT_URL}">
<style>
:root{{--accent:{ACCENT};--navy:{NAVY};--ink:#1E293B;--muted:#5B6B82;--rule:#E2E8F0;}}
*{{box-sizing:border-box;}}
html,body{{margin:0;background:#F1F5F9;}}
body{{font-family:'Geist',Inter,system-ui,sans-serif;color:var(--ink);font-size:14.5px;line-height:1.55;}}
header{{background:var(--navy);border-top:4px solid var(--accent);color:#fff;padding:36px 16px 26px;}}
.wrap{{max-width:860px;margin:0 auto;padding:0 16px;}}
h1{{font:400 44px/1.05 'Instrument Serif',Georgia,serif;margin:0 0 8px;}}
header p{{color:#94A3B8;margin:0;max-width:680px;}}
header a.back{{color:#94A3B8;font:500 11px 'Geist Mono',monospace;letter-spacing:.06em;}}
main{{padding:24px 0 48px;}}
.step{{background:#fff;border:1px solid var(--rule);border-radius:10px;padding:18px 22px;margin:0 0 14px;}}
.step h2{{font:400 26px/1.15 'Instrument Serif',Georgia,serif;margin:0 0 4px;}}
.step .n{{font:600 9.5px 'Geist Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:#9A3412;}}
.opts{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;}}
.opts button{{font:500 13.5px 'Geist',system-ui,sans-serif;color:var(--ink);background:#F8FAFC;border:1px solid #CBD5E1;border-radius:999px;padding:8px 15px;cursor:pointer;text-align:left;}}
.opts button:hover{{border-color:var(--accent);}}
.opts button[aria-pressed="true"]{{background:#0C1A2E;color:#fff;border-color:#0C1A2E;}}
.opts button small{{display:block;font-size:11.5px;color:var(--muted);}}
.opts button[aria-pressed="true"] small{{color:#CBD5E1;}}
.step.done{{padding:12px 22px;}}
.step.done .opts,.step.done .sub{{display:none;}}
.step.done h2{{font-size:18px;}}
.chosen{{display:none;margin-left:6px;font:500 13px 'Geist',sans-serif;color:var(--ink);}}
.step.done .chosen{{display:inline;}}
.edit{{display:none;float:right;font-size:12.5px;color:#9A3412;background:none;border:0;cursor:pointer;text-decoration:underline;}}
.step.done .edit{{display:inline;}}
.sub{{color:var(--muted);font-size:13px;margin:0;}}
[hidden]{{display:none !important;}}
#result h2{{font:400 30px/1.1 'Instrument Serif',Georgia,serif;margin:22px 0 12px;}}
.rec{{background:#fff;border:1px solid var(--rule);border-left:5px solid var(--accent);border-radius:10px;padding:16px 20px;margin:0 0 12px;}}
.rec h3{{margin:0 0 4px;font-size:17px;}}
.rec .num{{font:600 11px 'Geist Mono',monospace;color:#9A3412;margin-right:6px;}}
.rec p{{margin:0 0 6px;}}
.rec .why{{color:var(--muted);font-size:13px;}}
.rec .links a{{display:inline-block;margin:6px 8px 0 0;font:500 12.5px 'Geist',sans-serif;text-decoration:none;color:var(--ink);border:1px solid #CBD5E1;border-radius:999px;padding:5px 12px;}}
.rec .links a.primary{{background:#0C1A2E;color:#fff;border-color:#0C1A2E;}}
.rec .links a:hover{{border-color:var(--accent);}}
.more{{background:#fff;border:1px solid var(--rule);border-radius:10px;padding:14px 20px;font-size:13.5px;}}
.more a{{color:#9A3412;}}
.more ul{{margin:6px 0;padding-left:18px;}}
#again{{font:500 13px 'Geist',sans-serif;color:#fff;background:#C2410C;border:0;border-radius:999px;padding:8px 16px;cursor:pointer;margin-top:12px;}}
footer{{font:9px 'Geist Mono',monospace;letter-spacing:.08em;color:#5B6B82;text-align:center;padding:0 16px 32px;}}
</style>
</head>
<body>
<header><div class="wrap">
  <a class="back" href="index.html">← All tools</a>
  <h1>Find a Tool</h1>
  <p>Answer three quick questions and get three tools to start with, each with a board to print and a guide to run it. You can always browse all the tools instead.</p>
</div></header>
<main><div class="wrap">
<noscript><p>This page needs JavaScript. Try <a href="start-here-by-role.html">Tools by role</a> or the <a href="scenarios.html">Scenario Playbook</a> instead.</p></noscript>
<div class="step" id="q-role"><button class="edit" type="button">Change</button><div class="n">Question 1 of 3</div><h2>I'm a…<span class="chosen"></span></h2><p class="sub">Pick the closest fit.</p><div class="opts"></div></div>
<div class="step" id="q-size" hidden><button class="edit" type="button">Change</button><div class="n">Question 2 of 3</div><h2>How big is the work?<span class="chosen"></span></h2><p class="sub">Count everyone involved, not just your team.</p><div class="opts"></div></div>
<div class="step" id="q-need" hidden><button class="edit" type="button">Change</button><div class="n">Question 3 of 3</div><h2>What's going on?<span class="chosen"></span></h2><p class="sub">Pick the one that matters most right now.</p><div class="opts"></div></div>
<div id="result" hidden aria-live="polite"></div>
</div></main>
<footer>{escape(CREDIT)}</footer>
<script>
var D={data};
(function(){{
  var st={{role:null,size:null,need:null}}, order=['role','size','need'];
  function esc(s){{return String(s).replace(/[&<>"]/g,function(c){{return{{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]}})}}
  function opts(q){{
    if(q==='role') return D.roles.map(function(r){{return [r[0],r[1],'']}});
    if(q==='size') return Object.keys(D.sizes).sort().map(function(k){{return [k,D.sizes[k].label,D.sizes[k].sub]}});
    return Object.keys(D.needs).map(function(k){{return [k,D.needs[k].label,'']}}).sort(function(a,b){{return a[0]==='improve'?1:b[0]==='improve'?-1:0}});
  }}
  function label(q,v){{var o=opts(q).filter(function(x){{return x[0]===v}})[0];return o?o[1]:''}}
  function render(){{
    order.forEach(function(q,i){{
      var el=document.getElementById('q-'+q), prev=i===0||st[order[i-1]];
      el.hidden=!prev; el.classList.toggle('done',!!st[q]);
      el.querySelector('.chosen').textContent=st[q]?' '+label(q,st[q]):'';
      el.querySelector('.opts').innerHTML=opts(q).map(function(o){{
        return '<button type="button" data-v="'+o[0]+'" aria-pressed="'+(st[q]===o[0])+'">'+esc(o[1])+(o[2]?'<small>'+esc(o[2])+'</small>':'')+'</button>';
      }}).join('');
    }});
    var res=document.getElementById('result');
    if(st.role&&st.size&&st.need){{
      var r=D.results[st.role+'|'+st.size+'|'+st.need], n=D.needs[st.need];
      res.innerHTML='<h2>Start with these three</h2>'+r.map(function(p,i){{
        var t=D.tools[p[0]];
        return '<div class="rec"><h3><span class="num">'+(i+1)+'</span>'+esc(t.t)+'</h3>'+(t.d?'<p>'+esc(t.d)+'</p>':'')+
          '<p class="why">Why: '+esc(p[1])+'.</p><div class="links"><a class="primary" href="'+t.b+'">Open the board</a>'+
          (t.g?'<a href="'+t.g+'">Read the guide</a>':'')+(t.x?'<a href="'+t.x+'">See an example</a>':'')+'</div></div>';
      }}).join('')+'<div class="more"><b>Want more?</b><ul>'+
        (n.sc?'<li>The Scenario Playbook on <a href="scenarios.html#'+n.sc+'">“'+esc(n.st)+'”</a>: first moves and longer-term fixes.</li>':'')+
        (st.role!=='any'?'<li>All the tools for your role: <a href="start-here-by-role.html#'+st.role+'">Tools by role</a>.</li>':'')+
        '<li>The minimum set for this size of work: <a href="workshop-recipes.html#starter-kits">Starter kits</a>.</li>'+
        '<li>Or <a href="index.html">browse every tool</a>.</li></ul>'+
        '<button id="again" type="button">Start again</button></div>';
      res.hidden=false;
      document.getElementById('again').onclick=function(){{st={{role:null,size:null,need:null}};save();render();window.scrollTo(0,0)}};
    }} else res.hidden=true;
  }}
  function save(){{
    var h=st.role?'role='+st.role+(st.size?'&size='+st.size:'')+(st.need?'&need='+st.need:''):'';
    history.replaceState(null,'',h?'#'+h:location.pathname);
  }}
  order.forEach(function(q,i){{
    var el=document.getElementById('q-'+q);
    el.querySelector('.opts').addEventListener('click',function(e){{
      var b=e.target.closest('button'); if(!b) return;
      st[q]=b.dataset.v; save(); render();
      var nx=document.getElementById(i<2?'q-'+order[i+1]:'result'); if(nx) nx.scrollIntoView({{behavior:'smooth',block:'start'}});
    }});
    el.querySelector('.edit').addEventListener('click',function(){{
      for(var j=i;j<order.length;j++) st[order[j]]=null; save(); render();
    }});
  }});
  location.hash.slice(1).split('&').forEach(function(p){{
    var kv=p.split('='), q=kv[0], v=kv[1];
    if(q==='role'&&D.roles.some(function(r){{return r[0]===v}})) st.role=v;
    if(q==='size'&&D.sizes[v]) st.size=v;
    if(q==='need'&&D.needs[v]) st.need=v;
  }});
  if(!st.role) st.size=st.need=null; else if(!st.size) st.need=null;
  render();
}})();
</script>
</body>
</html>
"""
    paths.write_page("find-a-tool.html", page)
    print(f"wrote find-a-tool.html ({len(results)} combinations, {len(tools)} tools)")


if __name__ == "__main__":
    build()
