---
name: herd-sprint
description: Orchestrate, via herd/herdr, the implementation of BUILD tickets in the "Ready to Dev" column of the current sprint. Similar tickets are grouped into lots (max 5 tickets), with one tab, one worktree and one MR per lot and one commit per ticket. Each ticket is built then reviewed before the next one, the lot gets a final review, then the branch is pushed and an existing MR is reused if any (never created). Use when the user runs /herd-sprint or asks to launch the tickets of the sprint, optionally with explicit ticket keys as arguments.
---

# Herd sprint

You are the head agent. Load the `herd` skill first and follow its rules (spawn, watchers, report files, never close a pane without explicit confirmation). This skill only adds the sprint protocol on top.

The goal is to keep the number of MRs to review low: similar tickets are grouped into one lot, and a lot gives one MR with one commit per ticket.

## 1. Select the tickets

Use the Atlassian MCP (`searchJiraIssuesUsingJql`, site `nalo-fr.atlassian.net`) with:

```
project = BUILD AND assignee = currentUser() AND sprint in openSprints() AND labels = BACKEND AND status = "Ready to Dev"
```

If ticket keys are passed as arguments, restrict to those keys. Fetch each ticket in full (`getJiraIssue`: description, acceptance criteria, issue links, comments). Ignore tickets in any other column.

## 2. Build the lots and the dependency graph

### Lots

Group tickets into lots. Two tickets go in the same lot when at least one of these is true:
- they share the same epic or parent;
- they touch the same module or the same files (deduced from descriptions and acceptance criteria, and from the code when needed);
- they describe the same kind of change (for example the same fix applied in several places);
- one directly blocks the other (the blocked ticket is then simply the next commit of the lot, with no stacked MR).

Guardrails:
- A lot holds at most 5 tickets.
- A lot never mixes a risky change (migration, authentication, permissions, payment) with simple changes.
- When in doubt, keep the tickets in separate lots.

### Dependencies

Use the issue links (`is blocked by` / `blocks`, and dependencies stated in descriptions or comments). Map the link direction carefully (`inward` / `outward`) so that no edge is inverted. Inside a lot, dependencies only set the order of the commits. Between lots, a blocking ticket no longer blocks once its branch is pushed to `origin` (with or without an MR), or once it is resolved. For a dependency on a ticket outside the selected set, fetch it and check its status category, then look for a remote branch or an open MR whose source branch or title contains its key (`git ls-remote --heads origin`, `glab mr list`). If it is neither resolved nor covered by a pushed branch, the dependent lot (and its own dependents) stays on hold, and only the user can override that. On a dependency cycle or an ambiguous textual dependency, stop and ask the user.

Then show the user a short table before launching: lot, tickets in commit order, titles, dependencies, wave number (1 + the highest wave among the lots it depends on). The user validates or corrects the grouping before anything starts. Lots without dependencies form wave 1. A lot starts only when every lot it depends on has reached its final state (all tickets built and reviewed, final review done, branch pushed, MR description ready or existing MR updated). Never start it earlier, even if the blocker looks nearly finished.

### Pace

At most 3 lots run at the same time. The other lots wait for a free slot, in wave order, even when their dependencies are satisfied.

## 3. Launch a lot

`XXXX` below is the number of the first ticket of the lot. For each lot to start:

1. Run `git fetch --prune origin`, then check that neither the worktree path, the local or remote branch, a live herd agent named `build-XXXX`, nor an open MR from that source branch already exists. If one does, stop and report it to the user without deleting anything. Otherwise create the worktree at an absolute path under the main checkout (`git rev-parse --show-toplevel` of the main worktree, not of the current one): `git worktree add <main>/.claude/worktrees/build-XXXX -b tch/BUILD-XXXX-<short-slug> <target_ref>`.
   - Lot with no dependency: `target_ref` is `origin/develop`.
   - Lot with exactly one dependency still unmerged: `target_ref` is the pushed branch of that dependency (`origin/<source-branch>`, also for an external ticket), and the future MR targets that same branch (stacked MR). Flag it in the final report. If the dependency is already merged, use `origin/develop`.
   - Lot with several unmerged dependencies: no single base exists, so wait until they are merged into `develop`, then use `origin/develop` and ask the user to confirm the start.
   The same `target_ref` is given to the reviewer and recorded as the MR target branch (without the `origin/` prefix) in the MR description file.
2. Spawn the lot orchestrator in its own tab: `herd-spawn -m tab -a "--model sonnet --permission-mode auto" build-XXXX <worktree path> "<orchestrator task>"`.
3. Start the lot watcher as a background Bash task (`run_in_background`). It polls every 60 s and exits, printing the reason, on the first of these events: `/tmp/herd/build-XXXX.md` exists (final report); any agent of the lot (`build-XXXX`, `bXXXX`, `rXXXX`) is `blocked`; the statuses of these agents and the mtimes of `/tmp/herd/*XXXX*` are unchanged for 10 consecutive polls (stall). Do not use a plain `herdr agent wait` on the orchestrator: it fires at spawn while the orchestrator is still idle. Only the watcher end wakes the head agent, so it must cover blocked and stall cases.

The orchestrator task text must stand alone and contain: the full content of every ticket of the lot in commit order, the worktree path and branch, the protocol of section 4 and the conventions of section 5.

## 4. Orchestrator protocol (one per lot)

The orchestrator loads the `herd` skill, does no implementation itself, and spawns its workers as panes in its own tab (`herd-spawn -m pane`) with `<cwd>` set to the lot worktree. The reviewer always runs read-only (plan mode for claude, `--sandbox read-only` for codex), whatever `choicemymodel` returns. Since `-a` replaces the default permission flag, pass the flag explicitly on every spawn.

The builder (`bXXXX`) and the reviewer (`rXXXX`) are spawned once for the lot and reused for every ticket with `herdr agent prompt`.

1. **Builder** (name `bXXXX`): its model is not hardcoded. Before spawning, run `choicemymodel "<full content of the lot tickets>"` as the `herd` skill requires, and use the `kind` and `args` it returns as `-k` and `-a`. Keep auto mode: for a claude worker add `--permission-mode auto` to the returned args if they carry no permission flag, and for a codex worker keep `--sandbox workspace-write`. If the command fails, fall back to the `herd` skill defaults and say so in the report. It reads the `CLAUDE.md` files that apply to the touched code before editing.
2. **Reviewer** (name `rXXXX`): its model is not hardcoded either. Run `choicemymodel "<full content of the lot tickets and review task>"` and use the returned `kind` and `args` as `-k` and `-a`, with the read-only constraint forced on top: for a claude worker add `--permission-mode plan` if the args carry no permission flag (replace any other one), and for a codex worker use `--sandbox read-only`. Spawn it with `herd-spawn -n` so that no report file is requested. If `choicemymodel` fails, fall back to `opus` in plan mode and say so in the report.
3. **Ticket loop**: process the tickets in commit order. A ticket starts only when the previous one has a verdict `OK`.
   1. Record `<base>` = current `HEAD`. Ask the builder to implement the ticket with tests and to commit following section 5, with a commit message carrying that ticket key. It writes its report to `/tmp/herd/bXXXX-NNNN.md` (`NNNN` is the ticket number): what changed, tests run, assumptions, and for each family of the "Test families checklist" in `tests-common.md` whether it is covered, with the test, or ruled out, with the reason. It never pushes and never opens an MR. Every round ends with everything committed (`git status --porcelain` empty).
   2. Ask the reviewer to review `git diff <base>...HEAD` after a `git fetch`, on the acceptance criteria of that ticket only. It covers functional risks, technical risks, unverified assumptions, missing edge cases, test coverage, and behaviors depending on production data or configuration. It checks the "Test families checklist" of `tests-common.md` against the diff: a family that applies and has neither a test nor a justified exclusion is a blocking finding. It challenges the builder's conclusions like a senior reviewer. It ends with a final block `ROUND: n`, `VERDICT: OK|CORRECTIONS`, `BLOCKERS: ...`, `ADVISORIES: ...`, with blocking findings numbered first. It does not modify code. Plan mode blocks file writes, so it gives its verdict and findings directly in its final chat reply, with no report file. The orchestrator reads them with `herdr agent read rXXXX --source recent-unwrapped --lines 200` and checks that the `ROUND` number is the expected one. If the block is missing, it asks the reviewer to restate it in a compact form instead of resending the review.
   3. If the verdict is `CORRECTIONS`, send the findings to the builder with `herdr agent prompt bXXXX "<findings>"`. Corrections go in a separate commit carrying the same ticket key, never in an amended or rebased commit. Wait, then send the reviewer a new prompt to review `git diff <base>...HEAD` again in full, with priority on the fixes. The initial review counts as round 1, with a maximum of 3 rounds per ticket. If blockers remain after round 3, stop the whole lot and report them instead of pushing. The following tickets of the lot are not started. Advisories alone never block.
4. **Final lot review**: when the lot has two tickets or more, once every ticket has a verdict `OK`, ask the reviewer to review `git diff <target_ref>...HEAD` in full, on the acceptance criteria of all tickets. It focuses on interactions between commits, regressions, tests of an earlier ticket broken by a later one, and overall consistency. Same final block format, with a maximum of 2 rounds, corrections following the same rule as above. For a lot of one ticket, the ticket review is the final review.
5. **Final state**: once the final verdict is `OK`, check that the working tree is clean, run the tests relevant to the diff on the exact commit to push, then `git push -u origin <branch>` once. Then look for an open MR from that source branch (`glab mr list --source-branch <branch>`).
   - If one exists, the push updates it. Re-read it to confirm its URL, draft status, source and target, and report them.
   - If none exists, **never create one** (no `glab mr create`, no equivalent). Write the title, the target branch (`develop` or the dependency's branch, see section 3) and the description to `/tmp/herd/build-XXXX-mr.md`. The description follows the `pr` skill (`~/.agents/skills/pr/SKILL.md`) and its template (Résumé, Preuve, Danger de la fusion), built from the reviewer's reports. It lists every ticket of the lot with its own proof. Read that skill before writing it. The final report states "MR to be created by the user".
6. Write the final report to `/tmp/herd/build-XXXX.md`: tickets of the lot, MR URL or "MR to create" with source branch, target branch and path of the description file, review rounds per ticket and for the final review, remaining non-blocking findings, unverified assumptions.

## 5. Conventions given to every worker

- One commit per ticket at least, never a commit mixing two tickets. Commit messages: `type(scope): description #BUILD-XXXX` with the key of the ticket concerned, in the style of the repo history.
- Never add `Co-Authored-By` or "Generated with" lines to commits or MR descriptions.
- Code comments in English.
- No over-engineering: no abstractions or options beyond the tickets.
- Never merge, never push to `develop`, never mark an existing MR ready.
- Never create an MR/PR (`glab mr create` or any equivalent). Only push the branch and reuse an MR that already exists.
- Never close a herdr pane or tab without asking the user for explicit confirmation, even when the work is done.

## 6. Tracking and closing

- When a lot orchestrator reports, read `/tmp/herd/build-XXXX.md`, summarize it in a few lines, then start the next waiting lot whose dependencies are all final, within the limit of 3 running lots.
- When a watcher ends without a final report (`blocked` or stall), run `herdr agent list` and `herdr agent read` on the orchestrator and its workers, unblock or report to the user, then start a new watcher for that lot. Also re-check every live lot's workers on each wake-up, whatever its cause.
- A lot that fails (builder in error, tests still red, worker crashed, report missing, blockers after the last round) is reported to the user right away. Its dependents are not started, and the other lots keep going.
- Keep a status table (lot, tickets, wave, current ticket, state, MR URL or "MR to create") and update it when the user asks for a status.
- At the end, give one table with all lots, review rounds and open points, and list the MRs the user still has to create with their source and target branches and description file. Ask before closing any pane, and ask before removing the worktrees (`git worktree remove`).
- Do not transition the Jira tickets unless the user asks.
