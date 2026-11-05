---
name: herd-sprint-lot
description: Orchestrate, via herd/herdr, the implementation of BUILD tickets in the "Ready to Dev" column of the current sprint. One tab and one worktree per ticket, each with an orchestrator that runs a builder, then a reviewer, then corrections, then pushes and opens a draft MR. Use when the user runs /herd-sprint-lot or asks to launch the tickets of the sprint, optionally with explicit ticket keys as arguments.
---

# Herd sprint

You are the head agent. Load the `herd` skill first and follow its rules (spawn, watchers, report files, never close a pane without explicit confirmation). This skill only adds the sprint protocol on top.

## 1. Select the tickets

Use the Atlassian MCP (`searchJiraIssuesUsingJql`, site `nalo-fr.atlassian.net`) with:

```
project = BUILD AND assignee = currentUser() AND sprint in openSprints() AND labels = BACKEND AND status = "Ready to Dev"
```

If ticket keys are passed as arguments, restrict to those keys. Fetch each ticket in full (`getJiraIssue`: description, acceptance criteria, issue links, comments). Ignore tickets in any other column.

## 2. Build the dependency graph

Use the issue links (`is blocked by` / `blocks`, and dependencies stated in descriptions or comments). Map the link direction carefully (`inward` / `outward`) so that no edge is inverted. A blocking ticket no longer blocks once it has an open MR (draft or not), or once it is resolved. For a dependency on a ticket outside the selected set, fetch it and check its status category, then look for an open MR whose source branch or title contains its key (`glab mr list`). If it is neither resolved nor covered by an open MR, the dependent ticket (and its own dependents) stays on hold, and only the user can override that. On a dependency cycle or an ambiguous textual dependency, stop and ask the user.

Then show the user a short table before launching: ticket, title, dependencies, wave number (1 + the highest wave among its dependencies). Tickets without dependencies form wave 1 and start together. A ticket starts only when every ticket it depends on has reached its final state (build, review, corrections done, pushed, draft MR open). Never start it earlier, even if the blocker looks nearly finished.

## 3. Launch a ticket

For each ticket to start:

1. Run `git fetch --prune origin`, then check that neither the worktree path, the local or remote branch, a live herd agent named `build-XXXX`, nor an open MR from that source branch already exists. If one does, stop and report it to the user without deleting anything. Otherwise create the worktree at an absolute path under the main checkout (`git rev-parse --show-toplevel` of the main worktree, not of the current one): `git worktree add <main>/.claude/worktrees/build-XXXX -b tch/BUILD-XXXX-<short-slug> <target_ref>`.
   - Ticket with no dependency: `target_ref` is `origin/develop`.
   - Ticket with exactly one dependency still unmerged: `target_ref` is the source branch of that dependency's open MR (`origin/<source-branch>`, also for an external ticket), and the draft MR targets that same branch (stacked MR). Flag it in the final report. If the dependency is already merged, use `origin/develop`.
   - Ticket with several unmerged dependencies: no single base exists, so wait until they are merged into `develop`, then use `origin/develop` and ask the user to confirm the start.
   The same `target_ref` is given to the reviewer and to `glab mr create --target-branch` (without the `origin/` prefix).
2. Spawn the ticket orchestrator in its own tab: `herd-spawn -m tab -a "--model sonnet --permission-mode auto" build-XXXX <worktree path> "<orchestrator task>"`.
3. Start the ticket watcher as a background Bash task (`run_in_background`). It polls every 60 s and exits, printing the reason, on the first of these events: `/tmp/herd/build-XXXX.md` exists (final report); any agent of the ticket (`build-XXXX`, `bXXXX`, `rXXXX`) is `blocked`; the statuses of these agents and the mtimes of `/tmp/herd/*XXXX*` are unchanged for 10 consecutive polls (stall). Do not use a plain `herdr agent wait` on the orchestrator: it fires at spawn while the orchestrator is still idle. Only the watcher end wakes the head agent, so it must cover blocked and stall cases.

The orchestrator task text must stand alone and contain: the full ticket content, the worktree path and branch, the protocol of section 4 and the conventions of section 5.

## 4. Orchestrator protocol (one per ticket)

The orchestrator loads the `herd` skill, does no implementation itself, and spawns its workers as panes in its own tab (`herd-spawn -m pane`) with `<cwd>` set to the ticket worktree. The reviewer always runs read-only (plan mode for claude, `--sandbox read-only` for codex), whatever `choicemymodel` returns. Since `-a` replaces the default permission flag, pass the flag explicitly on every spawn.

1. **Builder** (name `bXXXX`): its model is not hardcoded. Before spawning, run `choicemymodel "<full ticket content>"` as the `herd` skill requires, and use the `kind` and `args` it returns as `-k` and `-a`. Keep auto mode: for a claude worker add `--permission-mode auto` to the returned args if they carry no permission flag, and for a codex worker keep `--sandbox workspace-write`. If the command fails, fall back to the `herd` skill defaults and say so in the report. The builder implements the ticket with tests, commits following section 5, writes its report to `/tmp/herd/bXXXX.md` (what changed, tests run, assumptions). It never pushes and never opens an MR. Every round ends with everything committed (`git status --porcelain` empty). It reads the `CLAUDE.md` files that apply to the touched code before editing.
2. **Reviewer** (name `rXXXX`): its model is not hardcoded either. Run `choicemymodel "<full ticket content and review task>"` and use the returned `kind` and `args` as `-k` and `-a`, with the read-only constraint forced on top: for a claude worker add `--permission-mode plan` if the args carry no permission flag (replace any other one), and for a codex worker use `--sandbox read-only`. Spawn it with `herd-spawn -n` so that no report file is requested. If `choicemymodel` fails, fall back to `opus` in plan mode and say so in the report. The reviewer reviews `git diff <target_ref>...HEAD` on the ticket's acceptance criteria, after a `git fetch`. It covers functional risks, technical risks, unverified assumptions, missing edge cases, test coverage, and behaviors depending on production data or configuration. It challenges the builder's conclusions like a senior reviewer. It ends with a final block `ROUND: n`, `VERDICT: OK|CORRECTIONS`, `BLOCKERS: ...`, `ADVISORIES: ...`, with blocking findings numbered first. It does not modify code. Plan mode blocks file writes, so it gives its verdict and findings directly in its final chat reply, with no report file. The orchestrator reads them with `herdr agent read rXXXX --source recent-unwrapped --lines 200` and checks that the `ROUND` number is the expected one. If the block is missing, it asks the reviewer to restate it in a compact form instead of resending the review.
3. **Corrections**: if the verdict is `CORRECTIONS`, send the findings to the builder with `herdr agent prompt bXXXX "<findings>"`, wait, then send the reviewer a new prompt to review the full diff again, with priority on the fixes, so that a regression cannot slip through. The initial review counts as round 1, with a maximum of 3 rounds in total. If blockers remain after round 3, stop and report them instead of pushing. Advisories alone never block.
4. **Final state**: once the verdict is `OK`, check that the working tree is clean, run the tests relevant to the diff on the exact commit to push, then `git push -u origin <branch>`. Look for an open MR from that source branch first. If none exists, open a **draft** MR non-interactively: `glab mr create --draft --yes --source-branch <branch> --target-branch <target> --title "<title>" --description-file <file>`, where `<target>` is `develop` or the dependency's branch (see section 3). Then re-read the MR to confirm its URL, draft status, source and target. The MR description keeps exactly the four sections from the user's global instructions (Contexte, Modifications, Points d'attention, Tests), with "Risques et validations" as a subsection of "Points d'attention", built from the reviewer's report.
5. Write the final report to `/tmp/herd/build-XXXX.md`: MR URL, number of review rounds, remaining non-blocking findings, unverified assumptions.

## 5. Conventions given to every worker

- Commit messages: `type(scope): description #BUILD-XXXX`, in the style of the repo history.
- Never add `Co-Authored-By` or "Generated with" lines to commits or MR descriptions.
- Code comments in English.
- No over-engineering: no abstractions or options beyond the ticket.
- Never merge, never push to `develop`, never mark the MR ready (draft only).
- Never close a herdr pane or tab without asking the user for explicit confirmation, even when the work is done.

## 6. Tracking and closing

- When a ticket orchestrator reports, read `/tmp/herd/build-XXXX.md`, summarize it in a few lines, then start the tickets of the next wave whose dependencies are all final.
- When a watcher ends without a final report (`blocked` or stall), run `herdr agent list` and `herdr agent read` on the orchestrator and its workers, unblock or report to the user, then start a new watcher for that ticket. Also re-check every live ticket's workers on each wake-up, whatever its cause.
- A ticket that fails (builder in error, tests still red, worker crashed, report missing, blockers after round 3) is reported to the user right away. Its dependents are not started, and the tickets of other branches keep going.
- Keep a status table (ticket, wave, state, MR URL) and update it when the user asks for a status.
- At the end, give one table with all MRs, review rounds and open points. Ask before closing any pane, and ask before removing the worktrees (`git worktree remove`).
- Do not transition the Jira tickets unless the user asks.
