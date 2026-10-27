<img src="static/banner.jpg" alt="A sunlit, empty lecture hall with a blackboard" width="100%" />

# hoff-harness

A second cursor for your coding agent. It glides to things on your Mac, explains
them in a speech bubble, walks you through tasks step by step, or does them while
you watch. And you can point back: hold **⌃⌥**, circle something, and ask
*"what is this?"*. Your agent gets exactly what you marked.

**[hoff.rorosaga.com](https://hoff.rorosaga.com)**: see it in action.

**macOS only.** Works with Claude Code, Codex, Cursor, OpenCode, Pi, Hermes and
other agents that can run shell commands.

## What it can do

| | You say | What happens |
|---|---|---|
| **Show me** | *"Where's the export button in Figma?"* | The cursor glides to it, rings it, and a bubble explains it. |
| **Walk me through** | *"Walk me through adding a GitHub Action."* | One step at a time; each step waits for your click on the right thing. |
| **Do it for me** | *"Turn on dark mode, and show me as you go."* | The bubble says what it's about to do, the cursor points, then it clicks or types while you watch. |
| **Explain my screen** | *"What are all these Xcode panels?"* | A short cursor tour of the parts, with the full answer in chat. |
| **Point back** | Hold ⌃⌥, circle an error: *"why is this failing?"* | Your agent gets the app, the window, the text and elements under your mark, and a crop. |
| **Many clips** | Mark three things: *"compare these."* | Each mark is numbered; Claude Code's status line shows `📎 3 screen clips ready`. |
| **Web pages** | Circle part of a page: *"summarize this"*, *"fill this in for me"* | In Chrome it works with the page itself: exact elements, links, text. It clicks and types through Chrome without taking your mouse. |

## Keys

| Keys | What they do |
|---|---|
| hold **⌃⌥** and click | Point at something. A pulse shows where. |
| hold **⌃⌥** and drag | Circle, underline or arrow something. |
| **⌃⌥ esc** | Clear your marks and put the cursor away. During "do it for me", it also tells the agent to stop. |

Send your message and the marks go with it. Marks fade from the screen after a
few seconds, but stay attached for 15 minutes. To change the keys, ask your
agent (*"use cmd+shift for marking"*); they live in
[`config.json`](skills/hoff-harness/config.json).

## Install

Paste this into Claude Code:

```text
Install hoff-harness from https://github.com/rorosaga/hoff-harness: run `claude plugin marketplace add rorosaga/hoff-harness` and `claude plugin install hoff-harness@hoff-harness`. Make sure `uv` is installed. Then run the plugin's `skills/hoff-harness/scripts/hoff-harness doctor`, explain any missing macOS permission and ask before requesting it. Offer to add the clip counter to my status line with `hoff-harness statusline install`. If browser-harness is installed, run `hoff-harness browser` to connect Chrome. Finally point at something in Finder: `hoff-harness point --app Finder --find "Go" --say "Hi, I'm your guide cursor."`
```

Other agents and manual setup: [install.md](install.md).

### Works with

| Agent | Point, guide, do | Marks attach to your message | Tested |
|---|---|---|---|
| **Claude Code** (terminal, desktop app, IDEs) | ✓ | ✓ automatically (plugin hooks) | ✓ |
| **Codex**, **Cursor**, **OpenCode**, **Pi**, **Hermes**, **Gemini CLI** | ✓ through [SKILL.md](skills/hoff-harness/SKILL.md) | the agent runs `hoff-harness context` | not yet |
| Chat apps without a shell (Claude desktop chat, ChatGPT) | needs an MCP server | | planned |

## Requirements

- **macOS 14 or later.** It uses the macOS accessibility API and AppKit
  windows, so it doesn't run on Linux or Windows.
- **[uv](https://docs.astral.sh/uv).** The first run installs PyObjC into uv's
  cache, which takes a few seconds.
- **Accessibility** and **Screen Recording** permission for the app your agent
  runs in (System Settings > Privacy & Security). `hoff-harness doctor` checks
  both.
- Optional: **[browser-harness](https://github.com/browser-use/browser-harness)**
  for web pages in Chrome and other Chromium browsers.

## How it works

```text
  agent's shell                          overlay (starts with your agent session)
       │                                          │
  hoff-harness point ...  ── local socket ──▶  glass cursor, bubble, rings, your marks
       │                                          │  click-through windows above everything
  macOS accessibility tree, screenshots           │
  browser-harness for Chrome pages         hold ⌃⌥: it takes the mouse and saves
                                           each mark with what is under it
  Claude Code hooks: start the overlay with a session, attach marks to your next message
```

- It never takes focus. Clicks pass through it, except while you hold ⌃⌥.
- Your real pointer moves only for a click on something that has no
  accessibility action, and it goes straight back.
- Everything stays on your Mac. Marks and screenshots live in
  `~/Library/Caches/hoff-harness`, are only sent to your agent with your message,
  and are deleted after a day.

## Why "hoff"

**hoff** is short for **hands-off**. The idea mainly came from Hoff, a hackathon
project [Ricky](https://github.com/ramcav) and [I](https://github.com/rorosaga)
built together and demoed at YC at the Browser Use hackathon.

## Credits

- The pointer's shape and spring motion are from
  [macos-harness](https://github.com/browser-use/macos-harness) (MIT).
- Web pages go through
  [browser-harness](https://github.com/browser-use/browser-harness) (MIT).
- Inspired by [Clicky](https://github.com/farzaa/clicky) and HeyClicky.

Details and licences: [THIRD_PARTY.md](THIRD_PARTY.md). Contributing:
[CONTRIBUTING.md](CONTRIBUTING.md).

[MIT](LICENSE)
