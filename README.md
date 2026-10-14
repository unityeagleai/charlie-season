# Charlie: Season 1 · Unity's Room

Live: https://unityeagleai.github.io/charlie-season/

An 80s pixel bedroom where Unity sits with her joystick in front of the CRT. Every episode of the 8-bit series is a cartridge on the shelf: tap one, it slides into the console and the episode plays on the TV (scanlines included). Play/pause, previous/next and fullscreen are in the bar under the room. Made to hang on the wall in the Meta Quest 3 browser, and it works on a phone too.

## Add a new episode

1. Put the video in the `videos/` folder (MP4, H.264 + AAC; keep it under about 30 MB so it streams well on the Quest).
2. Open `episodes.json` and add one line to the list, after the last episode (mind the comma after the previous line):

```json
{ "number": 5, "title": "Your New Episode", "video": "videos/ep05-your-new-episode.mp4", "color": "#ffe14a" }
```

3. Commit and push. A new cartridge appears on the shelf by itself, in episode-number order.

- `number`: the episode number printed on the cartridge (also sets the order).
- `title`: printed on the cartridge label and shown while it plays.
- `video`: path to the file inside this repo.
- `color`: the cartridge colour, any CSS colour (`#ff3fd1`, `orange`, …).

The shelf scrolls once there are more than four cartridges.

Tip: for faster start-up, move the MP4 index to the front before adding it:
`ffmpeg -i in.mp4 -c copy -movflags +faststart videos/ep05-your-new-episode.mp4`

## How it stays light on the Quest

- Only the episode you pick is loaded. The video tag uses `preload="none"` and the previous episode is unloaded when you switch.
- Nothing heavy plays on its own. The only motion is CSS (lava lamp, scanline roll) and one small Roomba sprite.
- Big tap targets for controllers and hand tracking: cartridges, the TV screen (tap to play/pause), and 60 px buttons in the bar.

## Files

- `index.html`, `style.css`, `app.js`: the page.
- `episodes.json`: the episode list.
- `img/room.png`: the bedroom, drawn by `tools/draw_room.py` (Python + Pillow; run `python3 tools/draw_room.py` from the repo root to redraw it). The page places the TV screen, shelf, lava lamp and Roomba over it in the same 400×225 pixel grid.
- `fonts/`: Press Start 2P and Silkscreen, both under the SIL Open Font License 1.1.

All posters are original pixel art made for this page.
