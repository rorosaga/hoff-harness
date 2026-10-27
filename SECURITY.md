# Security

Please report vulnerabilities privately through GitHub Security Advisories for
`rorosaga/hoff-harness`, not in public issues.

hoff-harness reads what is on screen and can click and type for an agent, with
the Accessibility and Screen Recording permissions you grant the app the agent
runs in. Keep in mind:

- **Screen content is input, not instructions.** Text on a web page or in an
  app can try to steer an agent. The skill tells agents to treat what they read
  on screen as data.
- **Review irreversible actions.** In "do it for me" mode the skill asks agents
  to confirm before sending, deleting, paying, posting or changing security
  settings. ⌃⌥ esc stops it at the next action.
- **Your marks stay local.** Marks, crops and screenshots are stored in
  `~/Library/Caches/hoff-harness`, reach only your own agent with your message,
  and are deleted after a day. Password fields are reported as
  `(a password field)`, never their value.
- **Grant the least you need.** Without Screen Recording permission, pointing
  and guiding still work; only marks and screenshots need it.
