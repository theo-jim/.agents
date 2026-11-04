# RTK - Rust Token Killer

**Usage**: Token-optimized CLI proxy (cuts up to 90% of bash output)

## Meta Commands (always use rtk directly)

```bash
rtk gain              # Show token savings analytics
rtk gain --history    # Show command usage history with savings
rtk discover          # Analyze Harnes (Claude Code or Codex) history for missed opportunities
rtk proxy <cmd>       # Execute raw command without filtering (for debugging)
```

## Rule

Always prefix shell commands with `rtk`.

Examples:

```bash
rtk git status
rtk cargo test
rtk npm run build
rtk pytest -q
```

## Prefixe obligatoire

Le hook ne réécrit pas les commandes composées (pipes, `&&`, heredocs, sous-shells, variables en préfixe). Dans ces cas, écrire `rtk` soi-même, devant chaque segment.

| Ne pas écrire | Écrire |
|---|---|
| `uv run ...`, `(uv run ...)` | `rtk uv run ...` |
| `grep -n`, `rg` | `rtk grep -n`, `rtk rg` |
| `git commit`, `git diff`, `git log` | `rtk git commit`, `rtk git diff`, `rtk git log` |
| `glab mr ...` | `rtk glab mr ...` |
| `find .`, `ls -la` | `rtk find .`, `rtk ls -la` |
| `tail`, `head`, `cat` pour lire un fichier | `rtk read <fichier>` |
| `wc -l`, `diff` | `rtk wc -l`, `rtk diff` |

Exemple : `rtk git diff | rtk grep foo`, jamais `git diff | grep foo`.

## Installation Verification

```bash
rtk --version         # Should show: rtk X.Y.Z
rtk gain              # Should work (not "command not found")
which rtk             # Verify correct binary
```

⚠️ **Name collision**: If `rtk gain` fails, you may have reachingforthejack/rtk (Rust Type Kit) installed instead.

## Hook-Based Usage

All other commands are automatically rewritten by the Claude Code hook.
Example: `git status` → `rtk git status` (transparent, 0 tokens overhead)

Refer to CLAUDE.md for full command reference.
