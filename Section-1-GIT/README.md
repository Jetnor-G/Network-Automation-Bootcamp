# Section 1 — Git for Network Automation

## Objective

Learn how to use **Git** as the single source of truth for network configurations. By the end of this section you will track device configs in a repository, use branches for change management, and roll back a bad config in seconds.

---

## Why Git for Network Configs?

| Traditional Approach | Git-Based Approach |
|----------------------|-------------------|
| Configs saved on a single engineer's laptop | Every config stored in a shared repository |
| No change history | Full audit trail with author, date, and reason |
| Rollback = manual copy-paste from backup | `git revert` or `git checkout` restores instantly |
| No review process | Pull Requests enforce peer review before push |

---

## Lab Exercises

### Exercise 1 — Initialize a Config Repository

```bash
# 1. Create a new repo for your network configs
mkdir net-configs && cd net-configs
git init
git config user.name  "Network Engineer"
git config user.email "neteng@example.com"

# 2. Add a baseline router config
cp ../configs/router1_baseline.cfg .
git add router1_baseline.cfg
git commit -m "feat: add Router-1 baseline config"

# 3. View the commit log
git log --oneline
```

**Expected output:**
```
a1b2c3d feat: add Router-1 baseline config
```

---

### Exercise 2 — Branching Strategy for Change Management

```bash
# Always branch off main before making changes
git checkout -b change/CR-1042-add-loopback

# Edit the config
echo "interface Loopback0
 ip address 10.255.255.1 255.255.255.255
 no shutdown" >> router1_baseline.cfg

git add router1_baseline.cfg
git commit -m "feat(CR-1042): add Loopback0 to Router-1"

# Peer-review the diff before merging
git diff main change/CR-1042-add-loopback

# Merge after approval
git checkout main
git merge --no-ff change/CR-1042-add-loopback -m "merge: CR-1042 approved and applied"
```

**Branching model:**
```
main ──────●──────────────────────────●── (production)
            \                        /
             change/CR-1042 ────────●
```

---

### Exercise 3 — Configuration Rollback

```bash
# Simulate a bad config being committed
echo "no ip routing" >> router1_baseline.cfg
git add router1_baseline.cfg
git commit -m "ERROR: accidentally removed ip routing"

# View history to identify the good commit
git log --oneline

# Option A: Revert (safe — creates a new undo commit)
git revert HEAD

# Option B: Reset to a specific commit (destructive — use with care)
git reset --hard <good-commit-hash>

# Push the rollback
git push origin main
```

---

## Key Git Commands Cheat Sheet

| Command | Purpose |
|---------|---------|
| `git init` | Initialise a new repository |
| `git clone <url>` | Clone a remote repository |
| `git status` | Show working tree status |
| `git add <file>` | Stage changes |
| `git commit -m "msg"` | Commit staged changes |
| `git log --oneline` | Compact commit history |
| `git diff` | Show unstaged changes |
| `git checkout -b <branch>` | Create and switch to a new branch |
| `git merge --no-ff <branch>` | Merge with a merge commit |
| `git revert HEAD` | Undo last commit (safe) |
| `git reset --hard <hash>` | Discard commits (destructive) |
| `git tag v1.0` | Tag a release / golden config |

---

## Recommended Git Workflow for Network Teams

```
┌─────────────┐    ┌──────────────┐    ┌───────────┐    ┌──────────┐
│  Engineer   │───▶│ Feature      │───▶│ Pull      │───▶│  main    │
│  edits cfg  │    │ Branch       │    │ Request   │    │ (deploy) │
└─────────────┘    └──────────────┘    └───────────┘    └──────────┘
                        ↑                   ↑
                   git checkout -b     Peer review
                                       + CI tests
```

---

## Completion Criteria

- [ ] Repository initialised with at least one config file
- [ ] At least two commits visible in `git log`
- [ ] Successfully created and merged a feature branch
- [ ] Demonstrated a config rollback using `git revert`
