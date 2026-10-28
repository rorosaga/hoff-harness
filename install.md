# Installing hoff-harness

## Claude Code (plugin: skill and hooks)

```bash
claude plugin marketplace add rorosaga/hoff-harness
claude plugin install hoff-harness@hoff-harness
```

Inside Claude Code the same is `/plugin marketplace add rorosaga/hoff-harness`
then `/plugin install hoff-harness@hoff-harness`. The plugin brings two hooks:
- **SessionStart** starts the overlay, so the ⌃⌥ mark keys work.
- **UserPromptSubmit** attaches your marks to your next message. When nothing is
  marked it costs one file check.

## Claude Code (skill only)

```bash
git clone https://github.com/rorosaga/hoff-harness ~/code/hoff-harness
ln -sfn ~/code/hoff-harness/skills/hoff-harness ~/.claude/skills/hoff-harness
```

Pointing, walkthroughs and "do it for me" work as they are. For marks, add the
two hooks from [hooks/hooks.json](hooks/hooks.json) to `~/.claude/settings.json`,
replacing `${CLAUDE_PLUGIN_ROOT}/skills/hoff-harness` with
`$HOME/.claude/skills/hoff-harness`. Do not install the plugin as well, or the
hooks run twice.

## Other agents (Codex, OpenCode, Cursor's agent, Pi)

The tool is a command any agent with a shell can run:

```bash
git clone https://github.com/rorosaga/hoff-harness ~/code/hoff-harness
ln -sf ~/code/hoff-harness/skills/hoff-harness/scripts/hoff-harness ~/.local/bin/hoff-harness
```

Give the agent [SKILL.md](skills/hoff-harness/SKILL.md) as instructions, the way
it takes skills or rules. Marks are not attached for it automatically: it runs
`hoff-harness context` when you say "this".

**Cursor** also finds the skill by itself in `~/.claude/skills`, so the symlink
from the section above is enough. Its agent runs commands in a sandbox that can't
use Accessibility; it asks to run hoff-harness outside the sandbox, and that's
the run to allow.

## Claude desktop app and other MCP apps

`hoff-harness mcp` serves the same commands as MCP tools (`find`, `point`, `say`,
`marks`, `shot`, `hide`). In `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hoff-harness": {
      "command": "/opt/homebrew/bin/uv",
      "args": ["run", "--script", "--quiet", "/Users/YOU/.claude/skills/hoff-harness/scripts/hoff-harness", "mcp"]
    }
  }
}
```

Use the full paths (`which uv`), then restart the app. macOS asks once whether
**uv** may control the Mac: the desktop app starts the server through uv, so uv
is what needs Accessibility and Screen Recording. Keep in mind that this covers
anything else you run with uv.

ChatGPT connects only to remote MCP servers, not to one on your Mac, so it can't
use hoff-harness yet.

## Requirements

- macOS 14 or later, and [uv](https://docs.astral.sh/uv). The first run installs
  PyObjC into uv's cache, which takes a few seconds.
- **Accessibility** and **Screen Recording** permission (System Settings >
  Privacy & Security) for the app your agent runs in: your terminal, Cursor, or
  the Claude desktop app.
- Optional: [browser-harness](https://github.com/browser-use/browser-harness)
  for web pages in Chrome. Run `hoff-harness browser` once to connect; Chrome may
  ask you to allow it.

## The clip counter (Claude Code)

```bash
hoff-harness statusline install     # 📎 2 screen clips ready · ⌃⌥ add · ⌃⌥ esc clear
hoff-harness statusline uninstall
```

The counter shows only while clips wait. If you already have a status line, it
won't replace it: it prints the script to call from yours.

## Check it

```bash
hoff-harness doctor
```

Every line says what works, and for what doesn't, exactly what to do.

## Keys

In `~/.config/hoff-harness/config.json` (only what you change; the defaults ship in `skills/hoff-harness/config.json`):

```json
{ "dismiss": "ctrl+alt+escape", "mark": "ctrl+alt", "marks": true, "show_key_hint": false }
```

`hoff-harness keys` checks the file. Or ask your agent: "use cmd+shift for marking".
