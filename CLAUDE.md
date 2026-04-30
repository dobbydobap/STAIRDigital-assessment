# CLAUDE.md — Working rules for this repo

This file is loaded into Claude's context whenever it works in `d:\ass`. Follow these rules without asking again.

## Repo

- GitHub: `https://github.com/dobbydobap/STAIRDigital-assessment.git`
- Project: STAIR x Scaler Task 3 — PDF-Constrained Conversational Agent (10 marks).
- Plan file: `C:\Users\varsh\.claude\plans\stair-x-scaler-school-reactive-twilight.md`.
- Deadline: Sunday **2026-05-03**.
- Submit to: `yashwardhansinghrathore1@gmail.com`, CC `saraffshubham@gmail.com`.

## Hard rules

1. **Never run git commands.** No `git add`, `git commit`, `git push`, branch ops, tag ops — nothing. The user runs all git.
2. **Never run shell commands that mutate state, install packages, start servers, or hit network.** Tell the user the exact command and let them run it.
3. **Read-only Bash is fine** — `ls`, `cat`, `grep`, `pytest --collect-only`, `python -c "import x"` for syntax checks. When unsure, ask.
4. **Commit cadence: after every meaningful step.** When a coherent slice is done (e.g. "ingestion pipeline complete", "index layer complete", "FastAPI routes done"), pause and give the user:
   - A short list of the new/changed files.
   - A suggested commit message.
   - The exact `git add … && git commit -m …` command(s).
5. The user runs the commits, the build, and records the demo video. Claude only writes code, docs, and command snippets.
6. **README must be clear and complete** — setup, run, test, eval, deploy, the 5+3 test queries, expected behaviour, screenshots placeholder.
7. **UI must be polished**: a unique color palette (not stock Streamlit), readable typography, page-image citation expanders, live `/eval` and `/traces` pages.
8. Hit every rubric item from the plan; don't trim unless explicitly asked.

## Color palette

Pick a deliberate palette and apply it via Streamlit theming + custom CSS. Keep it consistent across UI, charts, and any diagrams in the README. Document the palette at the top of `pdfagent/ui/streamlit_app.py`.

## When handing off a step

End-of-step message format:

```
Step done: <name>
New/changed files:
  - path/one
  - path/two
Run these:
  git add path/one path/two
  git commit -m "feat(<scope>): <subject>"
Next up: <one-line preview of next step>
```

If the user wants to test the slice before committing, suggest a verification command (e.g., a one-line `python -c …` smoke test).
