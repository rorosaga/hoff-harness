# Contributing

hoff-harness is small on purpose: one script, one page of skill, and an overlay
that only draws. Prefer a general primitive (point, say, mark) over an
app-specific helper.

## Setup

```bash
git clone https://github.com/rorosaga/hoff-harness ~/code/hoff-harness
ln -sfn ~/code/hoff-harness/skills/hoff-harness ~/.claude/skills/hoff-harness
ln -sf  ~/code/hoff-harness/skills/hoff-harness/scripts/hoff-harness ~/.local/bin/
hoff-harness doctor
```

After changing the overlay, restart it with `hoff-harness quit && hoff-harness start`.
Crashes go to `~/Library/Caches/hoff-harness/overlay.log`.
[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) explains how it works, and the
lessons behind the odd-looking parts.

## Checks

```bash
python3 -c "compile(open('skills/hoff-harness/scripts/hoff-harness').read(), 'hoff-harness', 'exec')"
sh -n skills/hoff-harness/scripts/statusline.sh
claude plugin validate .
```

## Invariants

Pull requests should keep these true:

- **Never take focus.** The overlay's windows ignore the mouse except while the
  mark keys are held.
- **Never move the real pointer,** except the documented real-click fallback,
  which puts it back.
- **Never send screen content anywhere** except to the person's own agent, with
  their message. No telemetry.
- **Never set up a browser connection from a background path.** Mark saves must
  not trigger Chrome's approval prompt.
- **Keep the skill to one page** of what an agent needs.

## Third-party code

Anything copied or adapted needs a compatible licence (MIT, BSD, Apache-2.0)
and an entry in [THIRD_PARTY.md](THIRD_PARTY.md): source, version, what changed.
