"""Generate the Pages landing page from deployed game folders."""
from html import escape
from pathlib import Path

site = Path('site')
links = []
for game in sorted(site.iterdir()):
    if game.is_dir() and (game / 'index.html').is_file():
        name = game.name.replace('-', ' ').title()
        links.append(f'<li><a href="./{escape(game.name)}/">{escape(name)}</a></li>')
page = '''<!doctype html>
<html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TKA Student Games</title>
<style>body{font:18px system-ui;max-width:760px;margin:60px auto;padding:0 24px}li{margin:16px 0}a{color:#174ab0}</style>
<h1>TKA Student Games</h1>
<p>Choose a game. Click inside the game to use your keyboard. Sound may require a click to start.</p>
<ul>''' + '\n'.join(links) + '</ul></html>\n'
(site / 'index.html').write_text(page, encoding='utf-8')
