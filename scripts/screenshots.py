#!/usr/bin/env python3
"""Render the README images and the community directory's thumbnail and gallery.

Obsidian's own app.css is extracted at run time from the locally installed app —
it is never stored in this repository. The theme is laid over it in headless
Chrome on an Obsidian-shaped workspace, in both faces.

Needs macOS with Obsidian installed, Google Chrome, Node 22+ (`npm install` first,
for the Lucide icons) and Pillow. Writes screenshots/dark.png and light.png for the
README, screenshots/screenshot.png (512x288: left half dark, right half light) and
screenshots/gallery/ — five 1200x800 images for the directory listing, at 2x —
and screenshots/gallery-mobile/, three 900x1600 phone screens in Obsidian's mobile
layout (the one app.emulateMobile(true) shows).

Usage: python3 scripts/screenshots.py
"""
import json
import pathlib
import struct
import subprocess
import tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
ICONS = ROOT / "node_modules/lucide-static/icons"
SUPPORT = pathlib.Path.home() / "Library/Application Support/obsidian"


def obsidian_asar():
    """The newest auto-updated app bundle, else the one shipped inside Obsidian.app."""
    updates = sorted(SUPPORT.glob("obsidian-*.asar"),
                     key=lambda p: [int(x) for x in p.stem.split("-")[1].split(".")])
    return updates[-1] if updates else pathlib.Path("/Applications/Obsidian.app/Contents/Resources/obsidian.asar")


def extract(asar, names, dest):
    """Copy files out of an asar archive: a JSON table of contents, then the file bodies."""
    data = asar.read_bytes()
    header_size = struct.unpack_from("<I", data, 4)[0]
    toc = json.loads(data[16:16 + struct.unpack_from("<I", data, 12)[0]])
    base = 8 + header_size

    def walk(node, path=""):
        for name, child in node.get("files", {}).items():
            p = f"{path}/{name}" if path else name
            yield from walk(child, p) if "files" in child else [(p, child)]

    for p, meta in walk(toc):
        if p in names:
            start = base + int(meta["offset"])
            out = dest / p
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data[start:start + meta["size"]])


def icon(name, cls=""):
    svg = (ICONS / f"{name}.svg").read_text()
    body = svg[svg.index(">", svg.index("<svg")) + 1: svg.rindex("</svg>")]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'class="svg-icon lucide-{name} {cls}">{body}</svg>')


TRIANGLE = ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            'class="svg-icon right-triangle"><path d="M3 8L12 17L21 8"></path></svg>')


def folder(name, children="", collapsed=True):
    cls = " is-collapsed" if collapsed else ""
    kids = "" if collapsed else f'<div class="tree-item-children nav-folder-children">{children}</div>'
    return (f'<div class="tree-item nav-folder{cls}"><div class="tree-item-self nav-folder-title is-clickable mod-collapsible">'
            f'<div class="tree-item-icon collapse-icon{cls}">{TRIANGLE}</div>'
            f'<div class="tree-item-inner nav-folder-title-content">{name}</div></div>{kids}</div>')


def file(name, active=False):
    cls = " is-active" if active else ""
    return (f'<div class="tree-item nav-file"><div class="tree-item-self nav-file-title is-clickable{cls}">'
            f'<div class="tree-item-inner nav-file-title-content">{name}</div></div></div>')


def tab(title, ico, active=False, sidebar=False):
    cls = " is-active mod-active" if active else ""
    close = "" if sidebar else f'<div class="workspace-tab-header-inner-close-button">{icon("x")}</div>'
    return (f'<div class="workspace-tab-header tappable{cls}" aria-label="{title}"><div class="workspace-tab-header-inner">'
            f'<div class="workspace-tab-header-inner-icon">{icon(ico)}</div>'
            f'<div class="workspace-tab-header-inner-title">{title}</div>'
            f'<div class="workspace-tab-header-status-container"></div>{close}</div></div>')


def ribbon(ico):
    return f'<div class="clickable-icon side-dock-ribbon-action" aria-label="{ico}">{icon(ico)}</div>'


def tree(notes, active, folders=("Journal", "Projects", "Notes", "Archive"), loose="Manifesto"):
    """The file explorer: one expanded folder holding the open note."""
    before, parent, after = folders[:2], folders[2], folders[3:]
    kids = "".join(file(n, active=(n == active)) for n in notes)
    return ("".join(folder(f) for f in before) + folder(parent, kids, collapsed=False) +
            "".join(folder(f) for f in after) + file(loose))


def callout(kind, ico, title, text):
    return (f'<div class="el-div"><div data-callout="{kind}" class="callout"><div class="callout-title" dir="auto">'
            f'<div class="callout-icon">{icon(ico)}</div><div class="callout-title-inner">{title}</div></div>'
            f'<div class="callout-content"><p dir="auto">{text}</p></div></div></div>')


def tasks(*items):
    rows = "".join(
        f'<li data-task="{"x" if done else " "}" class="task-list-item{" is-checked" if done else ""}" dir="auto">'
        f'<span class="list-bullet"></span><input type="checkbox" class="task-list-item-checkbox"{" checked" if done else ""}>{text}</li>'
        for done, text in items)
    return f'<div class="el-ul"><ul class="contains-task-list has-list-bullet">{rows}</ul></div>'


def table(head, *rows):
    th = "".join(f'<th dir="auto">{h}</th>' for h in head)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="el-table"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def code(comment, strings):
    tok = lambda kind, text: f'<span class="token {kind}">{text}</span>'
    items = tok("punctuation", ", ").join(tok("string", f"'{x}'") for x in strings)
    return (f'<div class="el-pre"><pre class="language-ts"><code class="language-ts is-loaded">{tok("comment", "// " + comment)}\n'
            f'{tok("keyword", "const")} faces {tok("operator", "=")} {tok("punctuation", "[")}{items}'
            f'{tok("punctuation", "]")}{tok("punctuation", ";")}</code><button class="copy-code-button">{icon("copy")}</button></pre></div>')


def tags(*names):
    return '<div class="el-p"><p dir="auto">' + " ".join(f'<a href="#{n}" class="tag">#{n}</a>' for n in names) + "</p></div>"


def title(text):
    return f'<div class="mod-header mod-ui"><div class="inline-title" tabindex="-1">{text}</div></div>'


NOTE = f"""
{title("Specimen log")}
<div class="el-p"><p dir="auto">A botanist's specimen journal beside a developer's terminal. Warm linen pages, sage
annotations, one literary serif headline and crimson ink for what you act on — see
<a data-href="Field notes" href="Field notes" class="internal-link">Field notes</a>
and <a href="https://borozdov.ru" class="external-link">borozdov.ru</a>. The reading worth keeping gets an
<mark>amber pin</mark>; sample ids stay in <code>monospace</code>.</p></div>
{callout("note", "pencil", "Observation", "Leaf margins serrate; the second flush appeared after the rain. Re-check on Sunday.")}
{tasks((True, "Press the samples from plot B"), (False, "Label the trays with the new ids"))}
{code("one crimson, warm linen", ["linen", "moss"])}
{table(["Sample", "Site", "Height", "Status"], ["B-014", "North slope", "42 cm", "Pressed"], ["B-015", "Creek bank", "17 cm", "Drying"])}
{tags("specimens", "plot-b")}
"""

NOTE_CALLOUTS = f"""
{title("Callouts")}
<div class="el-p"><p dir="auto">Every callout is a specimen card: a light wash of the type's colour over bone,
a hairline edge, 10px corners and a monospace label.</p></div>
{callout("note", "pencil", "Note", "Sage for the plain note.")}
{callout("success", "check", "Done", "Green for what is finished.")}
{callout("warning", "triangle-alert", "Heads up", "Amber for what needs a look, crimson for real trouble.")}
<div class="el-blockquote"><blockquote dir="auto"><p>Press it today, name it tomorrow.</p></blockquote></div>
{table(["Face", "Role"], ["EB Garamond 400", "Title, the largest heading, quotes"], ["Sans 400", "Body text"], ["Mono", "Labels, tags and metadata"])}
"""

NOTE_RU = f"""
{title("Журнал образцов")}
<div class="el-p"><p dir="auto">Дневник ботаника рядом с терминалом разработчика. Тёплые льняные страницы, шалфейные
пометки, один литературный заголовок с засечками и малиновые чернила для того, что вы делаете,
см. <a data-href="Полевые заметки" href="Полевые заметки" class="internal-link">Полевые заметки</a>. Стоящее
наблюдение получает <mark>янтарную булавку</mark>, а номера образцов остаются <code>моноширинными</code>.</p></div>
{callout("note", "pencil", "Наблюдение", "Край листа пильчатый; вторая волна роста пошла после дождя. Проверить в воскресенье.")}
{tasks((True, "Спрессовать образцы с участка B"), (False, "Подписать лотки новыми номерами"))}
{code("один малиновый, тёплый лён", ["лён", "мох"])}
{table(["Образец", "Место", "Высота", "Статус"], ["B-014", "Северный склон", "42 см", "Спрессован"], ["B-015", "Берег ручья", "17 см", "Сушится"])}
{tags("образцы", "участок-b")}
"""


def setting(name, desc, control):
    return (f'<div class="setting-item"><div class="setting-item-info"><div class="setting-item-name">{name}</div>'
            f'<div class="setting-item-description">{desc}</div></div><div class="setting-item-control">{control}</div></div>')


def group(heading, *items):
    return (f'<div class="setting-group"><div class="setting-item setting-item-heading"><div class="setting-item-info">'
            f'<div class="setting-item-name">{heading}</div></div></div><div class="setting-items">{"".join(items)}</div></div>')


def toggle(on):
    return f'<div class="checkbox-container{" is-enabled" if on else ""}"><input type="checkbox"{" checked" if on else ""}></div>'


def nav(name, ico, active=False):
    return (f'<div class="vertical-tab-nav-item{" is-active" if active else ""}"><div class="vertical-tab-nav-item-icon">{icon(ico)}</div>'
            f'<div class="vertical-tab-nav-item-title">{name}</div></div>')


SETTINGS = f"""
<div class="modal-container mod-dim"><div class="modal-bg" style="opacity: 0.85;"></div>
 <div class="modal mod-settings mod-sidebar-layout"><div class="modal-close-button"></div>
  <div class="modal-content vertical-tabs-container">
   <div class="vertical-tab-header"><div class="vertical-tab-header-group">
    <div class="vertical-tab-header-group-title">Options</div>
    <div class="vertical-tab-header-group-items">{nav("General", "settings")}{nav("Editor", "square-pen")}{nav("Files and links", "folder-open")}{nav("Appearance", "palette", True)}{nav("Hotkeys", "keyboard")}{nav("Core plugins", "puzzle")}{nav("Community plugins", "puzzle")}</div>
   </div></div>
   <div class="vertical-tab-content-container"><div class="vertical-tab-content">
    {group("Themes",
           setting("Base color scheme", "Choose Obsidian's default color scheme.", '<select class="dropdown"><option>Light</option></select>'),
           setting("Themes", "Manage installed themes and browse community themes.", '<select class="dropdown"><option>Borozdov Herbarium</option></select><button>Manage</button>'))}
    {group("Interface",
           setting("Show inline title", "Displays the filename as an editable title inline with the file contents.", toggle(True)),
           setting("Show tab title bar", "Display the header at the top of every tab.", toggle(True)),
           setting("Show ribbon", "Display vertical toolbar on the side of the window.", toggle(False)))}
    {group("Font",
           setting("Font size", "Font size in pixels that affects reading view and editing view.", '<input class="slider" type="range" min="10" max="30" value="16" style="--slider-fill-ratio: 0.3">'),
           setting("Quick font size adjustment", "Adjust the font size using Ctrl + Scroll, or the trackpad pinch-zoom gesture.", toggle(True)))}
   </div></div>
  </div>
 </div>
</div>"""


def workspace(note, *, files, active, tabs, crumb, folders=("Journal", "Projects", "Notes", "Archive"), loose="Manifesto",
              status=("2 backlinks", "412 words", "2,640 characters"), overlay=""):
    head = "".join(tab(t, "file-text", i == 0) for i, t in enumerate(tabs))
    return f"""
<div class="app-container">
 <div class="horizontal-main-container">
  <div class="workspace is-left-sidedock-open">
   <div class="workspace-ribbon side-dock-ribbon mod-left">
    <div class="side-dock-actions">{ribbon("square-pen")}{ribbon("git-fork")}{ribbon("layout-dashboard")}{ribbon("calendar-days")}{ribbon("terminal-square")}</div>
    <div class="side-dock-settings">{ribbon("help-circle")}{ribbon("settings")}</div>
   </div>
   <div class="workspace-split mod-horizontal mod-sidedock mod-left-split" style="width: 250px;">
    <div class="workspace-tabs mod-top mod-top-left-space" style="height: 100%;">
     <div class="workspace-tab-header-container">
      <div class="workspace-tab-header-container-inner">{tab("Files", "files", True, True)}{tab("Search", "search", sidebar=True)}{tab("Bookmarks", "bookmark", sidebar=True)}</div>
      <div class="workspace-tab-header-spacer"></div>
      <div class="workspace-tab-header-tab-list"><span class="clickable-icon">{icon("chevron-down")}</span></div>
     </div>
     <div class="workspace-tab-container">
      <div class="workspace-leaf mod-active"><div class="workspace-leaf-content" data-type="file-explorer">
       <div class="nav-header"><div class="nav-buttons-container">
        <div class="clickable-icon nav-action-button">{icon("square-pen")}</div>
        <div class="clickable-icon nav-action-button">{icon("folder-plus")}</div>
        <div class="clickable-icon nav-action-button">{icon("arrow-up-narrow-wide")}</div>
        <div class="clickable-icon nav-action-button">{icon("chevrons-down-up")}</div>
       </div></div>
       <div class="nav-files-container node-insert-event"><div class="tree-item nav-folder mod-root">
        <div class="tree-item-children nav-folder-children">{tree(files, active, folders, loose)}</div></div></div>
      </div></div>
     </div>
    </div>
   </div>
   <div class="workspace-split mod-vertical mod-root">
    <div class="workspace-tabs mod-top mod-top-right-space mod-active">
     <div class="workspace-tab-header-container">
      <div class="workspace-tab-header-container-inner">{head}</div>
      <div class="workspace-tab-header-new-tab"><span class="clickable-icon">{icon("plus")}</span></div>
      <div class="workspace-tab-header-spacer"></div>
      <div class="workspace-tab-header-tab-list"><span class="clickable-icon">{icon("chevron-down")}</span></div>
     </div>
     <div class="workspace-tab-container">
      <div class="workspace-leaf mod-active"><div class="workspace-leaf-content" data-type="markdown" data-mode="preview">
       <div class="view-header">
        <div class="view-header-left"><div class="view-header-nav-buttons">
         <button class="clickable-icon">{icon("arrow-left")}</button><button class="clickable-icon">{icon("arrow-right")}</button></div></div>
        <div class="view-header-title-container mod-at-start">
         <div class="view-header-title-parent"><span class="view-header-breadcrumb">{crumb}</span><span class="view-header-breadcrumb-separator">/</span></div>
         <div class="view-header-title">{tabs[0]}</div></div>
        <div class="view-actions"><button class="clickable-icon view-action">{icon("book-open")}</button><button class="clickable-icon view-action">{icon("ellipsis-vertical")}</button></div>
       </div>
       <div class="view-content">
        <div class="markdown-reading-view" style="width: 100%; height: 100%;">
         <div class="markdown-preview-view markdown-rendered node-insert-event is-readable-line-width allow-fold-headings allow-fold-lists show-indentation-guide show-properties">
          <div class="markdown-preview-sizer markdown-preview-section">
           <div class="markdown-preview-pusher" style="width: 1px; height: 0.1px; margin-bottom: 0px;"></div>
           {note}
          </div>
         </div>
        </div>
       </div>
      </div></div>
     </div>
    </div>
   </div>
  </div>
 </div>
 <div class="status-bar">
  <div class="status-bar-item plugin-backlink mod-clickable"><span>{status[0]}</span></div>
  <div class="status-bar-item plugin-word-count"><span class="status-bar-item-segment">{status[1]}</span><span class="status-bar-item-segment">{status[2]}</span></div>
 </div>
</div>{overlay}"""


EN = dict(files=("Specimen log", "Field notes", "Reading list", "Typography"), active="Specimen log",
          tabs=("Specimen log", "Field notes"), crumb="Notes")
BODY = workspace(NOTE, **EN)
GALLERY = [  # the directory's gallery: 1200x800, rendered at 2x
    ("1-linen", "light", BODY),
    ("2-moss", "dark", BODY),
    ("3-settings", "light", workspace(NOTE, **EN, overlay=SETTINGS)),
    ("4-callouts", "dark", workspace(NOTE_CALLOUTS, files=("Callouts", "Specimen log", "Field notes", "Typography"),
                                      active="Callouts", tabs=("Callouts", "Specimen log"), crumb="Notes")),
    ("5-cyrillic", "light", workspace(NOTE_RU, files=("Журнал образцов", "Полевые заметки", "Список чтения", "Типографика"),
                                     active="Журнал образцов", tabs=("Журнал образцов", "Полевые заметки"), crumb="Заметки",
                                     folders=("Дневник", "Проекты", "Заметки", "Архив"), loose="Манифест",
                                     status=("Обратных ссылок: 2", "Слов: 412", "Символов: 2 640"))),
]


def phone(note, title):
    """Obsidian's phone layout, as app.emulateMobile(true) shows it: view header,
    reading view, the floating navigation bar — and an iOS status bar on top."""
    act = lambda ico: f'<div class="mobile-navbar-action"><button class="clickable-icon">{icon(ico)}</button></div>'
    tabs = ('<div class="mobile-navbar-action mobile-navbar-action-tabs"><button class="clickable-icon">'
            f'{icon("square")}<div class="mobile-navbar-tabs-number">2</div></button></div>')
    status = ('<div style="position: fixed; top: 0; left: 0; right: 0; height: 52px; display: flex; align-items: center; '
              'justify-content: space-between; padding: 0 30px; font: 600 16px/1 -apple-system, sans-serif; color: var(--text-normal); z-index: 99">'
              f'<span>9:41</span><span style="display: flex; gap: 6px; --icon-size: 18px">{icon("signal")}{icon("wifi")}'
              f'{icon("battery-full")}</span></div>')
    return f"""{status}
<div class="app-container">
 <div class="horizontal-main-container">
  <div class="workspace">
   <div class="workspace-split mod-vertical mod-root">
    <div class="workspace-leaf mod-active"><div class="workspace-leaf-content" data-type="markdown" data-mode="preview">
     <div class="view-header">
      <div class="view-header-left"><button class="clickable-icon view-action">{icon("panel-left")}</button></div>
      <div class="view-header-title-container mod-at-start"><div class="view-header-title">{title}</div></div>
      <div class="view-actions"><button class="clickable-icon view-action">{icon("book-open")}</button><button class="clickable-icon view-action">{icon("panel-right")}</button></div>
     </div>
     <div class="view-content">
      <div class="markdown-reading-view" style="width: 100%; height: 100%;">
       <div class="markdown-preview-view markdown-rendered node-insert-event is-readable-line-width allow-fold-headings allow-fold-lists show-indentation-guide show-properties">
        <div class="markdown-preview-sizer markdown-preview-section">
         <div class="markdown-preview-pusher" style="width: 1px; height: 0.1px; margin-bottom: 0px;"></div>
         {note}
        </div>
       </div>
      </div>
     </div>
    </div></div>
   </div>
  </div>
 </div>
 <div class="mobile-navbar mod-raised"><div class="mobile-navbar-actions">{act("chevron-left")}{act("chevron-right")}{act("plus")}{tabs}{act("menu")}</div></div>
</div>"""


MOBILE = [  # the directory's mobile gallery: 900x1600, a 450x800 phone at 2x
    ("1-linen", "light", phone(NOTE, "Specimen log")),
    ("2-moss", "dark", phone(NOTE, "Specimen log")),
    ("3-cyrillic", "light", phone(NOTE_RU, "Журнал образцов")),
]
DESKTOP = "mod-macos is-frameless is-hidden-frameless obsidian-app show-ribbon"
PHONE = "is-mobile is-phone is-ios is-floating-nav emulate-mobile"


def render(tmp, face, out, w, h, body=BODY, platform=DESKTOP):
    page = tmp / f"{out.parent.name}-{out.stem}-{face}.html"
    page.write_text(f'<!doctype html><html><head><meta charset="utf-8">'
                    f'<link rel="stylesheet" href="app.css"><link rel="stylesheet" href="theme.css"></head>'
                    f'<body class="theme-{face} {platform} show-inline-title show-view-header is-focused">{body}</body></html>')
    subprocess.run(["node", str(ROOT / "scripts/shot.mjs"), page.as_uri(), str(out), str(w), str(h), "2"],
                   check=True, timeout=120, stdout=subprocess.DEVNULL)


def main():
    out = ROOT / "screenshots"
    for sub in ("gallery", "gallery-mobile"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        tmp = pathlib.Path(t)
        # app.css plus the two external-link arrows it points at
        extract(obsidian_asar(), {"app.css", "public/images/6155340132a851f6089e.svg",
                                  "public/images/2308ab1944a6bfa5c5b8.svg"}, tmp)
        (tmp / "theme.css").write_text((ROOT / "theme.css").read_text())
        # README images: a roomy 1280x720 window at 2x.
        for face in ("dark", "light"):
            render(tmp, face, out / f"{face}.png", 1280, 720)
        # Thumbnail: a tighter 1024x576 window, so the UI still reads at 512x288.
        halves = {}
        for face in ("dark", "light"):
            render(tmp, face, tmp / f"thumb-{face}.png", 1024, 576)
            halves[face] = Image.open(tmp / f"thumb-{face}.png")
        split = halves["dark"].copy()
        w, h = split.size
        split.paste(halves["light"].crop((w // 2, 0, w, h)), (w // 2, 0))
        split.convert("RGB").resize((512, 288), Image.LANCZOS).save(out / "screenshot.png", optimize=True)
        for name, face, body in GALLERY:
            render(tmp, face, out / "gallery" / f"{name}.png", 1200, 800, body)
        for name, face, body in MOBILE:
            render(tmp, face, out / "gallery-mobile" / f"{name}.png", 450, 800, body, PHONE)
    print("wrote screenshots/: dark.png, light.png, screenshot.png, gallery/1-5, gallery-mobile/1-3")


if __name__ == "__main__":
    main()
