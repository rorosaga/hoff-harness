# hoff-harness

A second cursor with a speech bubble that Claude Code (or any agent with a
shell) drives on your Mac. It points at real controls, explains them, and can
walk you through a task step by step, waiting for your click at each step. Or it
does the task for you while you watch: it points, says what it is doing, then
presses or types. It never takes focus, and only moves your real pointer
for the rare real-click fallback, putting it back right after.

This file is for us, the people working on it. `SKILL.md` is what the agent reads.

## Install (our machine)

The repo is the plugin; the skill folder inside it is also a plain skill. On our
Mac we run the skill from the working copy, with the hooks in user settings:

```bash
ln -sfn ~/code/hoff-harness/skills/hoff-harness ~/.claude/skills/hoff-harness   # the skill
ln -sf  ~/code/hoff-harness/skills/hoff-harness/scripts/hoff-harness ~/.local/bin/   # the CLI on PATH
```

The two hooks in `~/.claude/settings.json` point at
`~/.claude/skills/hoff-harness/scripts/hoff-harness`. Do not also install the
plugin here, or every hook runs twice. Others install it per `install.md`.

Permissions belong to the app the agent runs in. The overlay is started from the
agent's shell, so it inherits that app's Accessibility and Screen Recording
grants. `hoff-harness doctor` checks them all.

## Layout

| Path | What |
|---|---|
| `.claude-plugin/plugin.json`, `marketplace.json` | The plugin, and a marketplace of one: `/plugin marketplace add rorosaga/hoff-harness`. Checked with `claude plugin validate .` |
| `hooks/hooks.json` | SessionStart (`start`) and UserPromptSubmit (`context`), through `${CLAUDE_PLUGIN_ROOT}`. |
| `skills/hoff-harness/SKILL.md` | What the agent reads. Runs the script as `${CLAUDE_SKILL_DIR}/scripts/hoff-harness`. |
| `skills/hoff-harness/scripts/hoff-harness` | Everything: the CLI and, with `_serve`, the overlay. A uv script with inline dependencies. |
| `skills/hoff-harness/scripts/pointer.py` | The pointer's shape and motion, vendored unchanged from macos-harness. |
| `skills/hoff-harness/scripts/statusline.sh` | Claude Code's status line: the waiting clip count, in plain shell (it runs every second). Reads `keys-hint`, written by the overlay from config.json. |
| `static/banner.svg` | The README banner: an SMIL animation (cursor glide, bubble, loop drawn, status line). |
| `.github/` | Issue templates and a `check` workflow (compile, `sh -n`, JSON). |
| `skills/hoff-harness/config.json` | Keys (`dismiss`, `mark`), `marks`, `show_key_hint`. Read again whenever it changes. |
| `README.md`, `install.md` | For people: the pitch, and installing for each agent. |
| `THIRD_PARTY.md` | What was copied, adapted or called, from where, under which licence. |
| `docs/DEVELOPMENT.md` | This file. |

Runtime state lives in `~/Library/Caches/hoff-harness/`: `overlay.sock`,
`overlay.lock`, `overlay.log` (crashes land here), `place.json` (where the
cursor last pointed), `marks/` and screenshots from `shot`.

## How it works

```
Claude Code ──Bash──> hoff-harness point/say/hide ──JSON over unix socket──> overlay process
                      (finds elements via AX,                               (AppKit run loop:
                       waits for your click)                                 pointer, ring, bubble)
```

**Two processes.** The CLI exits after each call. The overlay stays up so
animations keep running between calls. The first drawing command starts it
(`spawn` → `hoff-harness _serve`, detached). A lock file makes sure only one
runs, and it exits after 10 minutes hidden.

**Protocol.** One JSON object per connection, one JSON reply
(`{"ok", "cursor", "arrive_in", "shown"}`; `arrive_in` is the seconds until the
current move lands, so `--press` acts only once the person has seen it arrive):

| `cmd` | Fields | Effect |
|---|---|---|
| `show` | `x`,`y` (optional), `rect` (ring or `null`), `text`, `title`, `for` | Fade in, glide, ring, bubble. Any subset. |
| `ok` | | The target was clicked (by the person, or by us with `--press`): press pulse, ring goes green and fades. |
| `status` | | Nothing; the reply tells whether the guide is shown (the person may have dismissed it). |
| `hide` | | Fade everything out. |
| `quit` | | Exit the overlay. |

**Drawing.** One click-through, non-activating panel per display at the
assistive-tech window level holds the ring and the bubble (`GuideView`). The
pointer has its own 112×112 panel on top: frosted glass masked to the arrow,
with the picture over it, moved every frame (macos-harness's approach). A timer
runs at 60 fps while anything moves and at 2 fps otherwise, and only the area
around what is drawn gets repainted.

**Motion.** `Scene.go` asks `pointer.plan(start, end, bounds)` for a move:
- under 196 pt, a spring hop that stretches and tilts;
- further, a spring along the best of 20 candidate cubic paths.

`pointer.pose(move, t)` gives position, rotation and stretch for every frame.
Bubble and ring follow the pose. When "Reduce motion" is on, it jumps instead.

**Finding things.** `elements()` walks the app's accessibility tree breadth
first:
- It starts from the focused window and the menu bar.
- It keeps a CFEqual-checked visited set, because some apps reach an element
  twice or loop.
- It drops subtrees that are off every screen.
- It gives up after 3 s.

`score()` ranks matches: exact, prefix, word, substring, plus a bonus for
interactive roles.

**Coordinates.** Screen points, origin at the top-left of the main display
(AX and Quartz window bounds use the same space). AppKit's bottom-left origin
appears in two places, `screens()` and `mouse()`. `shot` resizes screenshots to
one pixel per point and prints the origin to add.

## Config

The person's settings are `~/.config/hoff-harness/config.json`, over the defaults in
`skills/hoff-harness/config.json`: a plugin update replaces the versioned plugin folder,
so nothing the person changes may live there. For the same reason `statusline install`
points Claude Code at a copy in `~/.config/hoff-harness/`, refreshed on every `start`.

`config.json`:

```json
{ "dismiss": "ctrl+alt+escape", "show_key_hint": false }
```

- Keys are modifiers then one key: `cmd`, `ctrl`, `alt`/`option`, `shift`, and
  `escape`, `return`, `space`, `tab`, `delete`, arrows, `a`–`z`, `0`–`9`,
  `f1`–`f12`, punctuation by name. See `KEYS` in the script.
- `hoff-harness keys` prints and checks the bindings.
- A broken file falls back to the defaults, so dismiss always works.
- Plain Escape is avoided on purpose: it is Claude Code's interrupt key.

## Testing

- **Live:** `hoff-harness point --app Finder --find "Share" --say "hi" --hold 2`,
  then `hoff-harness shot` and look at the image.
- **Following a target:** `tests/follow_test.py` opens `tests/scroll-dialog.html`
  in a Chrome guest window, scrolls the dialog, moves the window, scrolls the
  target away and back, clicks it, and closes the dialog without a click,
  checking the overlay's `status` (`ring`, `shown`) at each step. It needs Chrome
  connected through browser-harness, and the demo recorder's helpers from the
  website repo (the guest window and the hand); the command is at its top.
- **Off-screen:** load the script with `SourceFileLoader` and call
  `draw_pointer` / `Overlay.draw_bubble` inside `NSImage.lockFocusFlipped_`.
  Useful when the Mac is locked.
- **Crashes:** check `~/Library/Caches/hoff-harness/overlay.log`. When the
  overlay dies, the next command restarts it, and the cursor resumes from
  `place.json`.

## Lessons so far

- **Blocks must return `None`.** PyObjC blocks that AppKit calls
  (`addOperationWithBlock_`, event monitors) must return nothing. A lambda that
  returned a dict crashed the overlay on the first Escape.
- **The AX tree is not a tree.** It can reach an element twice and can loop.
  Without the visited set, search ran into its time limit.
- **Check the target is visible before pointing.** An element can be found and
  still be covered by another app's window, so `point` hit-tests its centre
  (exit 4).
- **A locked Mac is its own case.** AX returns nonsense and screenshots are
  blank, so the CLI exits 5 at the start.

- **Visible beats "focused".** Finder's focused window reaches other windows'
  elements, so "in the focused window" said nothing. Ranking now hit-tests the
  best 25 matches and puts what the person can see first (`(covered)` marks the
  rest). Internal identifiers (`_NS:122`, `_SC_SEARCH_FIELD`) are dropped: they
  made hidden fields match words like "search".

- **Ask Chrome which tab, never every tab.** Evaluating JS in each of dozens of tabs
  timed out at 12 s: background and frozen tabs do not answer. The address
  comes from Chrome's own accessibility tree, and page calls get a 1.5 s limit.
- **Hidden text wins text search.** Tooltips and screen-reader spans (0×0)
  matched "Notifications" first and the cursor flew to a corner. `FIND_JS`
  keeps rendered elements only.
- **A selector must be unique to be useful.** The first paths
  (`div > div > div:nth-of-type(1)`) matched many elements; `hoffSel` now climbs
  until `querySelectorAll` finds exactly one.

## Marking (point or circle, then ask)

Hold the mark modifiers (⌃⌥ by default) and the overlay windows take the mouse;
let go and clicks pass through again.
- **A click** is a point mark. **A drag** is a stroke (circle, underline, arrow).
- Marks stay drawn in blue until a prompt uses them; the dismiss keys clear them.

How a mark is saved:
1. **When marking starts,** `capture_displays()` screenshots every display in a
   thread, before anything is drawn. Crops are therefore clean of the new mark,
   though not of the guide cursor if it is on screen.
2. **On mouse-up,** `Marking.save` runs off the main thread, one save at a time
   (`SAVING` lock: PyObjC loads functions lazily and not thread-safely).
   - It hit-tests the accessibility tree: the centre first, then a 3×3 grid and
     points along the stroke. That gives the app, the window title, the
     `AXWebArea`'s `AXURL`, and up to 12 described elements.
   - It writes `marks/<time>/crop.png`, `marked.png` (the display at one pixel
     per point with the stroke drawn on) and `mark.json`.
   - It touches `marks/pending`.
3. **After all saves finish,** the full-screen captures are deleted.

Hooks in `~/.claude/settings.json` (added by hand for now; a plugin will carry them):

```json
"SessionStart":     [{"hooks": [{"type": "command", "command": "\"$HOME/.claude/skills/hoff-harness/scripts/hoff-harness\" start >/dev/null 2>&1 || true", "timeout": 30}]}],
"UserPromptSubmit": [{"hooks": [{"type": "command", "command": "test -e \"$HOME/Library/Caches/hoff-harness/marks/pending\" && \"$HOME/.claude/skills/hoff-harness/scripts/hoff-harness\" context || true", "timeout": 15}]}]
```

How the hooks behave:
- **The prompt hook costs one `test -e`** (about 1 ms) unless marks are waiting.
- **`context` prints marks younger than 15 minutes,** then marks each folder
  `used` and tells the overlay `marks_used`, which fades them. Its stdout
  becomes context for the prompt.
- **Cleanup:** mark folders older than a day are deleted, and so are stray
  captures older than a minute.
- **The overlay must be running for the keys to work,** so with `marks: true` it
  never idle-exits. It runs with the Accessory activation policy, because a
  Prohibited app's windows cannot take the mouse.

- **Hook output must be JSON.** A UserPromptSubmit hook whose plain-text output
  started with `[hoff]` never reached the model: it looks like JSON, fails to
  parse, and is dropped. `context` now prints
  `{"systemMessage", "hookSpecificOutput": {"additionalContext"}}`. The person
  also sees "📎 N screen marks attached".
- **Hit-test the app, not the system.** While marking, our windows take the
  mouse, so system-wide AX hit tests found the overlay (`python3`). Other apps
  leave invisible full-screen layers too (Screenshot at layer 24, a dictation
  app's status pill at 1000). `app_at` finds the topmost app window of layer 0–8 under the
  point, treats the menu bar as the front app's, and hit-tests inside that app.

## Web pages (Chrome through browser-harness)

hoff-harness does not open its own CDP connection: browser-harness's daemon holds
it, along with the person's approval of it in Chrome. We run browser-harness in
two ways (`bh()`):
- **Explicit commands** (`find --web`, `point --web/--css`, `--press`/`--type`
  on a page, `browser`) run the `browser-harness` command. It makes sure the
  daemon is up and can ask Chrome to allow the connection.
- **Mark saves** run browser-harness's Python with `browser_harness.helpers`
  only. They never set a connection up, so they can never pop Chrome's approval;
  without a connection, a mark falls back to the accessibility tree.

The generated Python ends by printing `HOFF <json>`. Values go into that Python
with `repr()`, and into page JavaScript with `json.dumps()`.

**Which tab.** `chrome_url()` reads the `AXWebArea`'s `AXURL` in the Chrome
window under the point (or the main window), after setting
`AXManualAccessibility`. That costs nothing per tab. `TAB_PY` matches that
address among `list_tabs()`. Without one, it keeps the tabs whose window
(`Browser.getWindowForTarget`, a browser-level call) holds the point. Each
candidate page is then asked for its geometry with a 1.5 s limit and must answer
`visibilityState == "visible"`.

**Screen to page.** `page_origin()`: zoom = `devicePixelRatio` / the display's
backing scale. The page's left edge is `screenX + (outerWidth - innerWidth·zoom)/2`
and its top is `screenY + outerHeight - innerHeight·zoom` (Chrome on macOS has
no side or bottom frame). A CSS pixel is then `(screen - origin) / zoom`.

**In the page** (`DESCRIBE_JS`):
- `hoffSel` climbs until a path matches exactly one element. It prefers ids
  without generated-looking runs, `data-testid`/`data-test`/`name`, then
  `:nth-of-type`.
- `hoffMeaningful` climbs from a hit to the nearest link, button, field or
  labelled node.
- `MARK_JS` returns those for the mark's probes, plus the text of the text nodes
  inside the box.
- `FIND_JS` scores by text (exact, prefix, contains), adds a bonus for
  interactive elements, and drops what is not rendered (under 2 px, hidden,
  transparent).

**Acting.** `web_act()` attaches to the tab, sends `Input.dispatchMouseEvent`
press and release at the element's centre, then `Input.insertText` and an Enter
key event, and detaches. It works in background windows and never touches the
real pointer.

## Do it for me

`point ... --press` and `--type TEXT [--enter]`. The CLI sends `show`, sleeps
`arrive_in + BEAT` (0.35 s) so the person sees where it is about to act, asks
`status` (a dismissed guide exits 8: the person is taking over), sends `ok` for
the press pulse, then acts:

- **press:** `AXPress`, then `AXPick`, then `AXConfirm` on the element. If the
  element has none of those, or the target was given as `--rect`/`--at`, it
  does a real click: a CGEvent at the point, then the person's pointer is warped
  back.
- **type:** `AXFocused = true` on the field (or press it), then unicode key
  events posted to that app's pid only (`CGEventPostToPid`, 16 characters per
  event).

Gestures (drag, scroll, shortcuts) stay with macos-harness, run with
`MACOS_HARNESS_POINTER=0` so its own pointer does not show next to ours.

## Packaging: skill vs plugin

What is here works as a plain skill. Circling needs hooks, so it needs more:
- A `SessionStart` hook keeps the overlay running, so the draw hotkey works.
- A `UserPromptSubmit` hook hands your marks to the next prompt.

Hooks can be added to settings by hand, but the way to give someone one install
is a **Claude Code plugin**. A plugin is this folder with:
- `.claude-plugin/plugin.json`;
- the skill under `skills/hoff-harness/`;
- `hooks/hooks.json` using `${CLAUDE_PLUGIN_ROOT}`.

It is installed with `/plugin marketplace add owner/repo` then
`/plugin install hoff-harness@<marketplace>`. A skill's frontmatter can declare
hooks too, but they only register once the skill is invoked, which is too late
for `SessionStart` and `UserPromptSubmit`.
(Docs: code.claude.com/docs/en/skills, /hooks, /plugins.)

## Ideas / next

- **Record mode:** clicks pass through to the app while each one is logged with
  its element and a screenshot. The result is a step list, Hoff's workflow
  format, that the agent can replay as a walkthrough or turn into automation. It
  is not the same as marking, where clicks must not reach the app ("what does
  Delete do?" must not delete).
- **Remote MCP** for ChatGPT, which only connects to servers on the internet.
  `hoff-harness mcp` (stdio) covers the Claude desktop app and Cursor.
- **Rectangle clips:** shift-drag for a box instead of a freehand stroke.

- **Circle to give context:**
  - Hold a hotkey and draw on screen. The overlay takes the mouse while you hold it.
  - On release, it saves a crop, a full screenshot with the stroke drawn on it,
    and the AX elements under the lasso.
  - A Claude Code `UserPromptSubmit` hook attaches recent marks to the next
    prompt.
  - The overlay has to be running for the hotkey to work, for example started
    by a `SessionStart` hook.
- **Voice out:** `--speak` reads the bubble aloud with macOS `say`, or a TTS API.
- **Voice in:** already works with any dictation app typing into the agent's prompt.
