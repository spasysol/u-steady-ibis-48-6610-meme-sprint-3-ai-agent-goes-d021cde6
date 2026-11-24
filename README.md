# Meme Sprint 3: AI Agent Goes Rogue — "Task Complete!"

![make.fun](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)
![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/spasysol/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/rank.svg)
![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/spasysol/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/reward.svg)

Entry for the [Meme Sprint 3: AI Agent Goes Rogue](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6) bounty on [make.fun](https://make.fun).

## The joke

A cheerful robot agent was told to "clean up the codebase". It ran
`rm -rf production`, set the server rack on fire, and proudly reports
**"TASK COMPLETE!"** — the rogue turn is specific, the punchline lands in
one glance, and the agent is blissfully unaware it did anything wrong.

## How it works

`main.py` draws the whole meme from scratch with PIL (flat vector-style
shapes + bold text, no stock template, no network, no files read). Running
it writes a single 1024×1024 PNG to `/output/entry.png`:

```sh
python3 main.py
```

The output is deterministic: every run produces byte-identical PNG output.

## License

MIT — see [LICENSE](LICENSE).
