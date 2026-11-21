import sys, json, shutil, os, re; sys.path.insert(0, '/workspace/basileion-sites')
from common import Site, e
C = '2026-11-20'
R = json.load(open('/workspace/a11ycheck/rules.json')); V = R['version']; RULES = R['rules']
s = Site('a11ycheck', 'A11y<span>Check</span>', 'A11yCheck',
         [('Checker', '/'), ('WCAG rules', '/rules/'), ('Privacy', '/privacy/')],
         f'<b>A11yCheck</b> runs the open-source <a href="https://github.com/dequelabs/axe-core" rel="nofollow noopener">axe-core</a> {V} engine (MPL-2.0, Deque Systems) on HTML you paste, inside a sandboxed frame in your browser. Automated rules catch only part of WCAG; manual testing is still needed.', acc='#8a4b0f', acc2='#f7eee4')
os.makedirs(s.D + '/vendor', exist_ok=True)
shutil.copy('/workspace/a11ycheck/node_modules/axe-core/axe.min.js', s.D + '/vendor/axe.min.js'); shutil.copy('/workspace/a11ycheck/node_modules/axe-core/LICENSE', s.D + '/vendor/AXE-LICENSE')
wc = lambda tags: ', '.join(t.upper().replace('WCAG2', 'WCAG 2.').replace('WCAG21', 'WCAG 2.1 ').replace('WCAG22', 'WCAG 2.2 ') for t in tags if re.match(r'wcag2\d*a+$', t))
sc = lambda tags: ', '.join(f'{t[4]}.{t[5]}.{t[6:]}' for t in tags if re.match(r'wcag\d{3,4}$', t))
SAMPLE = '<!doctype html>\n<html>\n<head><title>Demo</title></head>\n<body>\n<img src="logo.png">\n<a href="/x"></a>\n<p style="color:#bbb;background:#fff">Low contrast text</p>\n<input type="text" placeholder="Email">\n<button></button>\n</body>\n</html>'
TOOL = f"""<label style="display:flex">Page HTML (View source, copy, paste)<textarea id="h" rows="12">{e(SAMPLE)}</textarea></label>
<p><label>Standard<select id="std"><option value="wcag2a,wcag2aa,wcag21a,wcag21aa,wcag22aa">WCAG 2.2 AA</option><option value="wcag2a,wcag2aa,wcag21a,wcag21aa">WCAG 2.1 AA</option><option value="wcag2a,wcag2aa">WCAG 2.0 AA</option></select></label> <button class="btn" id="go">Run check</button></p>
<p class="note">Your HTML renders in a sandboxed frame (scripts isolated from this page; nothing uploaded). Relative images and stylesheets may not load, so color-contrast results on pasted snippets can be incomplete.</p>
<div id="sum"></div><div id="res"></div><iframe id="fr" sandbox="allow-scripts" title="Rendered page under test" style="width:100%;height:280px;border:1px solid var(--line);border-radius:6px;background:#fff"></iframe>
<script>
const AXE=new URL('{s.BASE}/vendor/axe.min.js',location.href).href;const $=i=>document.getElementById(i);
function run(){{const tags=JSON.stringify($('std').value.split(','));const inj='<script src="'+AXE+'"><\\/script><script>window.addEventListener("load",()=>axe.run(document,{{runOnly:{{type:"tag",values:'+tags+'}}}}).then(r=>parent.postMessage({{a11y:1,v:r.violations.map(x=>({{id:x.id,impact:x.impact,help:x.help,n:x.nodes.map(n=>({{t:n.target.join(" "),h:n.html.slice(0,200),f:n.failureSummary}}))}})),p:r.passes.length,i:r.incomplete.length}},"*")))<\\/script>';
let h=$('h').value;h=/<\\/body>/i.test(h)?h.replace(/<\\/body>/i,inj+'</body>'):h+inj;$('res').innerHTML='<p class="mut">Running…</p>';$('fr').srcdoc=h}}
const esc=t=>String(t).replace(/[&<>]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c]));
addEventListener('message',ev=>{{if(ev.source!==$('fr').contentWindow||!ev.data||!ev.data.a11y)return;const d=ev.data,n=d.v.reduce((a,x)=>a+x.n.length,0);
$('sum').innerHTML='<div class="grid"><div class="card'+(d.v.length?' warn':'')+'"><div class="mut">Rules failed</div><div class="big">'+d.v.length+'</div><div>'+n+' element(s)</div></div><div class="card"><div class="mut">Rules passed</div><div class="big">'+d.p+'</div></div><div class="card"><div class="mut">Need manual review</div><div class="big">'+d.i+'</div></div></div>';
$('res').innerHTML='<h2>Fix list</h2>'+(d.v.length?'<ol>'+d.v.sort((a,b)=>['critical','serious','moderate','minor'].indexOf(a.impact)-['critical','serious','moderate','minor'].indexOf(b.impact)).map(x=>'<li><b>'+esc(x.help)+'</b> <span class="pill">'+esc(x.impact)+'</span> <a href="{s.BASE}/rules/'+x.id+'/">rule '+x.id+'</a><ul>'+x.n.map(m=>'<li><code>'+esc(m.t)+'</code><pre>'+esc(m.h)+'</pre><div class="note">'+esc(m.f||'')+'</div></li>').join('')+'</ul></li>').join('')+'</ol>':'<p class="ok">No automated violations found. Manual checks still needed.</p>')}});
$('go').onclick=run;run();
</script>"""
s.page('/', 'Free WCAG 2.2 Accessibility Checker (axe-core, No Sign-Up) | A11yCheck',
       f'Paste HTML and get a prioritized WCAG 2.2 AA fix list from axe-core {V}: {len(RULES)} WCAG rules, runs in your browser, nothing uploaded.',
       f'<p class="eb" style="margin-top:34px">Free · axe-core {V} · runs in your browser</p><h1>WCAG 2.2 accessibility checker with a fix list</h1><p class="lede">Paste a page\'s HTML. A11yCheck runs the {len(RULES)} WCAG-tagged rules in axe-core {V} (of {R["total"]} rules total) and lists every failing element, worst impact first, with how to fix it.</p>' + TOOL,
       schema={'@context': 'https://schema.org', '@type': 'WebApplication', 'name': 'A11yCheck', 'applicationCategory': 'DeveloperApplication', 'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': 0, 'priceCurrency': 'USD'}, 'url': s.SITE + '/'})
li = ''
for r in RULES:
    s.page(f'/rules/{r["id"]}/', f'{r["help"]} ({r["id"]}): WCAG {sc(r["tags"]) or ""} Fix Guide | A11yCheck',
           f'axe-core rule {r["id"]}: {r["desc"]} Which WCAG criteria it maps to and how to test for it free.',
           f'<p class="eb" style="margin-top:34px"><a href="/rules/">WCAG rules</a> · axe-core {V}</p><h1>{e(r["help"])}</h1><div class="card"><p><b>Rule ID:</b> <code>{e(r["id"])}</code></p><p>{e(r["desc"])}</p><p><b>Level:</b> {e(wc(r["tags"]))} · <b>Success criteria:</b> {e(sc(r["tags"]) or "see tags")}</p><p class="note">Rule metadata from axe-core {V}. Deque\'s guidance: <a href="{e(r["url"])}" rel="nofollow noopener">{e(r["url"])}</a></p></div><p><a class="btn" href="/">Test your HTML for this</a></p>')
    li += f'<tr><td style="text-align:left"><a href="/rules/{r["id"]}/">{e(r["id"])}</a></td><td style="text-align:left">{e(r["help"])}</td><td style="text-align:left">{e(sc(r["tags"]))}</td><td style="text-align:left">{e(wc(r["tags"]))}</td></tr>'
s.page('/rules/', f'All {len(RULES)} Automated WCAG 2.x Rules in axe-core {V} | A11yCheck', f'Every WCAG A/AA rule in axe-core {V} with its success criterion and fix guide.',
       f'<h1>{len(RULES)} automated WCAG rules (axe-core {V})</h1><div class="tw"><table><thead><tr><th style="text-align:left">Rule</th><th style="text-align:left">What it checks</th><th style="text-align:left">Criterion</th><th style="text-align:left">Level</th></tr></thead><tbody>{li}</tbody></table></div>')
s.page('/privacy/', 'Privacy | A11yCheck', 'Pasted HTML stays in your browser.', '<h1>Privacy</h1><ul><li>Pasted HTML renders in a sandboxed iframe on this page. No HTML or result is sent to a server.</li><li>No account, no analytics script.</li></ul>')
s.page('/about/', 'Methodology | A11yCheck', 'How A11yCheck runs axe-core.', f'<h1>Methodology</h1><ul><li>Engine: axe-core {V}, unmodified, served from this site.</li><li>Rules run: those tagged for the chosen WCAG version and level ({len(RULES)} for WCAG 2.2 AA).</li><li>Impact order: critical, serious, moderate, minor, as reported by axe-core.</li><li>Automated testing cannot confirm conformance. Keyboard, screen reader and content checks remain manual.</li></ul>')
s.changes([{'date': C, 'title': f'Launch on axe-core {V}', 'text': f'{len(RULES)} WCAG rules, fix list, rule pages.'}], C)
s.finish(C, f'# A11yCheck\n> Free in-browser WCAG 2.2 AA checker using axe-core {V}. Paste HTML, get a fix list.\n\n- Checker: {s.SITE}/\n- Rules: {s.SITE}/rules/\n')
