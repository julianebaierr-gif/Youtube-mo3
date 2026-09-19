import os

with open('static/css/tailwind.min.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

target = '<link rel="stylesheet" href="/static/css/tailwind.min.css">'
replacement = f"<style>{css_content}</style>"

for path in ['templates/index.html', 'templates/page.html']:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    if target in html:
        html = html.replace(target, replacement, 1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Successfully inlined CSS in {path}")
    else:
        print(f"Target not found in {path}")
