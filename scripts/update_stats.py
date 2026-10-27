"""Generate local GitHub statistics SVGs; uses only the Python standard library."""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

USER = 'luanmenglei'
ASSETS = Path(__file__).resolve().parents[1] / 'assets'


def get_json(endpoint):
    headers = {'User-Agent': 'luanmenglei-profile', 'Accept': 'application/vnd.github+json'}
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    request = urllib.request.Request('https://api.github.com/' + endpoint, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def text(x, y, label, size, color, weight='400'):
    return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(str(label))}</text>'


def main():
    user = get_json(f'users/{USER}')
    repos = []
    page = 1
    while True:
        batch = get_json(f'users/{USER}/repos?per_page=100&page={page}')
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    own = [r for r in repos if not r['fork']]
    values = [len(repos), len(own), sum(r['stargazers_count'] for r in own), user['followers']]
    labels = ['Public repositories', 'Non-fork repositories', 'Stars on non-fork repositories', 'Followers']
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d')
    icons = [
        '<path d="M3 2h11v13H3V2Zm0 10h11M6 5h5"/>',
        '<path d="M4 2v5c0 4 8 1 8 5v3M12 2v5"/><circle cx="4" cy="2" r="1.5"/><circle cx="12" cy="2" r="1.5"/><circle cx="12" cy="15" r="1.5"/>',
        '<path d="m8 1 2.2 4.5 5 .7-3.6 3.5.8 5-4.4-2.3-4.4 2.3.8-5L.8 6.2l5-.7Z"/>',
        '<circle cx="8" cy="5" r="3"/><path d="M2 16v-2c0-5 12-5 12 0v2"/>',
    ]
    ASSETS.mkdir(exist_ok=True)
    for theme in ['light', 'dark']:
        dark = theme == 'dark'
        bg, border = ('#0d1117', '#30363d') if dark else ('#ffffff', '#d8dee4')
        ink, muted = ('#c9d1d9', '#759abe') if dark else ('#434d58', '#6585a6')
        accent = '#73baff' if dark else '#2f80ed'
        content = f'<rect x="1" y="1" width="478" height="224" rx="5" fill="{bg}" stroke="{border}"/>'
        content += text(24, 36, "luanmenglei's GitHub Stats", 19, accent, '700')
        for i, (label, value, icon) in enumerate(zip(labels, values, icons)):
            y = 73 + i * 33
            content += f'<g transform="translate(25 {y-13})" stroke="{accent}" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round">{icon}</g>'
            content += text(53, y, label, 14, ink, '600')
            content += text(420, y, value, 15, ink, '700')
        content += text(25, 205, f'Public data · Updated {stamp} (UTC+8)', 10, muted)
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="226" viewBox="0 0 480 226" role="img"><title>GitHub public statistics for {USER}</title>{content}</svg>\n'
        (ASSETS / f'stats-{theme}.svg').write_text(svg, encoding='utf-8')
    print(dict(zip(labels, values)), stamp)


if __name__ == '__main__':
    main()
