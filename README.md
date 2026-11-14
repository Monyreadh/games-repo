# TKA Student Games

Pygame student projects packaged with Pygbag and hosted on GitHub Pages.

## Publish

1. Under repository **Settings → Pages**, set **Source** to **GitHub Actions**.
2. If fork workflows are disabled, enable them in the **Actions** tab.
3. Commit/push changes to `main`, or run **Build and Deploy Games to GitHub Pages** manually.
4. Wait for both build and deploy jobs to succeed. The deployment output shows the live base URL.

Default base URL: https://monyreadh.github.io/games-repo/

| Student | Game | URL path |
| --- | --- | --- |
| Bung Samvichara | Bok-Bok | `/bok-bok/` |
| Ilyas Akinola Owolabi-Ayi | Tank Shooters | `/tank-shooters/` |
| Lim Kay | Potato and the Chef | `/potato-chef-tag/` |
| Samnang Serey Oudom | Collector Pong | `/collector-pong/` |
| Yun Sreng hong | Space Shooter | `/space-shooter-sreng-hong/` |

Append the path to the base URL (without doubling the slash). These links become available after a successful deployment.

## Add another game

Create a folder with a lowercase, hyphenated name containing `main.py` and its assets. The workflow discovers all top-level folders containing `main.py` automatically. Make the main loop asynchronous and yield with `await asyncio.sleep(0)` every frame. Preserve exact filename capitalization in asset paths. Dependencies must support Pygbag's browser runtime.

## Local preview

Install `pygbag==0.9.3` and `pygame-ce` in a Python environment, then run:

```powershell
python -m pygbag collector-pong
```

Open the localhost URL printed by Pygbag. Test start, controls, restart, images, and sound in the browser before showcasing.

## Embed on the TKA website

```html
<iframe
    src="https://monyreadh.github.io/games-repo/collector-pong/"
    title="Collector Pong student project"
    width="100%"
    height="700"
    style="border: 0;"
    allow="autoplay; fullscreen"
    allowfullscreen>
</iframe>
```

These games use keyboard controls; touch controls are not included. The player may need to click to start audio. Bok-Bok stores its browser high score in localStorage when available; restricted storage falls back to the current session. Its GIF animations have been converted to PNG frames to remove the browser Pillow dependency. Existing upstream games remain available.
