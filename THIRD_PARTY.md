# Third-party code and credits

What in this repo came from somewhere else, what we changed, and how to update it.

## Code we ship

### macos-harness: the pointer (MIT)

- **Upstream:** <https://github.com/browser-use/macos-harness>
- **Version taken:** 0.2.1, commit `43d9edf8286153482348b15f7d8c22d9e38f6c6b`
- **Licence:** MIT, Copyright (c) 2026 Browser Use (full text below)

| Our file | Upstream file | How |
|---|---|---|
| `skills/hoff-harness/scripts/pointer.py` | `macos_harness/pointer.py` | **Copied unchanged** apart from a two-line header saying where it is from. It holds the arrow's outline, glass and fog constants, the spring, and the choice of a curved path from 20 candidates (`plan`, `pose`, `press_scale`). |
| `skills/hoff-harness/scripts/hoff-harness`: `draw_pointer`, `pointer_image`, `click_through_panel`, `pointer_panel` | `macos_harness/overlay.py`: `draw_pointer`, `pointer_image`, `panel`, `pointer_panel` | **Adapted.** Same drawing (black fog tint, white fill and rim, kept only where the cover is; frosted `NSVisualEffectView` masked to the arrow; blur while fading in). Our changes: `panel` takes a frame so the full-screen ring and bubble windows use it too; window level is assistive-tech high instead of 102; no window title. Each function is marked `# Adapted from macos-harness overlay.py` in the source. |

Not taken: the driver side (`LivePointerOverlay`), the window stacking that keeps
the pointer just above the driven app's window, the halo, the "loading" rocking.
Our overlay stays above everything instead.

**To update:** install or clone the new macos-harness, diff its `pointer.py`
against ours (ignoring our two header lines), copy it over, update the commit
above. Then compare its `overlay.py` drawing functions with the four marked
ones. The constants (`FILL`, `RIM`, `TINT`, `FOG`, ...) are only in `pointer.py`,
so a new look usually comes with that file alone.

```
MIT License

Copyright (c) 2026 Browser Use

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Dependencies (installed by `uv`, not vendored)

| Package | Licence | Used for |
|---|---|---|
| `pyobjc-framework-Cocoa` | MIT | AppKit windows, drawing, events; CoreFoundation |
| `pyobjc-framework-Quartz` | MIT | window list, display bounds, CoreImage blur, CG context |
| `pyobjc-framework-ApplicationServices` | MIT | the accessibility API (finding elements) |

## Tools we call (not shipped)

| Tool | Licence | Used for |
|---|---|---|
| [browser-harness](https://github.com/browser-use/browser-harness) | MIT | Chrome pages over CDP: the visible tab, elements under a mark, finding by text or selector, clicks and typing. Optional: hoff-harness runs its installed `browser-harness` command or its Python with `browser_harness.helpers`; nothing of it is copied. Without it, Chrome falls back to the accessibility tree. |
| `screencapture`, `sips` | macOS | screenshots and resizing |

## Ideas, no code

- **Clicky** (<https://github.com/farzaa/clicky>, MIT): the idea of a buddy
  cursor that points while an LLM talks. Clicky has the model put
  `[POINT:x,y:label:screenN]` tags in its replies; we use the accessibility tree
  first and screenshots only as a fallback. No Clicky code is used.
- **HeyClicky** (<https://www.heyclicky.com>, closed source): step-by-step
  walkthroughs that wait for the person's click, highlights, and circling things
  on screen as context. Product ideas only.
- **Hoff**, the hackathon project by rorosaga and Ricky (ramcav),
  `hoff-onboard/extension`: the step format (target, title, description) and
  the glass bubble look. The name: hoff = hands-off.
- **browser-harness** (<https://github.com/browser-use/browser-harness>): the
  shape of the whole thing, a CLI an agent calls from Bash plus a SKILL.md.
