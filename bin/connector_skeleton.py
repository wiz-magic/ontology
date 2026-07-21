#!/usr/bin/env python3
"""
connector_skeleton.py — reference connector (SCHEMA.md §9.5). Copy one per channel.

A connector feeds ONE external channel (chat threads, a notes inbox, a ticket
system, a team database) into the memory layer as §9.1 object candidates.
This skeleton implements the contract *mechanics* and leaves the two
channel-specific functions for you to replace:

    extract_units(source_dir) -> [unit]   # what "one coherent unit" is in your channel
    distill(unit) -> (title, facts)       # normalize a unit (rules or an LLM)

The built-in implementations treat each *.md/*.txt file as one unit and use its
first heading as the title / its top-level bullets as Proposed Facts. That is a
placeholder good enough for structured notes — for real channels, replace
distill() with proper normalization (§9.5 rule 2: distill, don't dump; the
title should be the one line a person would actually search for).

Contract guarantees the skeleton keeps (do not remove when customizing):
- writes only staging/candidates/ + appends [GEN] to STAGING-LOG.md   (rule 1)
- sources = the real source path/URL, never the connector itself      (rule 3)
- one candidate per coherent unit                                     (rule 4)
- never edits an existing candidate, whatever its status              (rule 5)
- reproducible IDs per unit → re-runs skip instead of duplicating     (rule 6)

Usage:
    python bin/connector_skeleton.py --source PATH        # scan a source folder
        [--root PATH]           # template copy to write into (default: this repo)
        [--connector-id NAME]   # ID prefix + log label (default: source dir name)
        [--date YYYY-MM-DD]     # created date (default: today)
        [--dry-run]             # show what would be emitted; write nothing
"""
import sys
import os
import re
import datetime

CONFIDENCE = 0.5  # generator confidence — reference only, never a promotion criterion (§9.1)


# ---------- channel-specific part: REPLACE these two functions per channel ----------

def extract_units(source_dir):
    """One unit = one coherent source item (§9.5 rule 4). Placeholder: one file = one unit."""
    units = []
    for dirpath, _dirs, files in os.walk(source_dir):
        for name in sorted(files):
            if not name.endswith((".md", ".txt")) or name.startswith("_"):
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8") as f:
                units.append({"path": path, "stem": os.path.splitext(name)[0], "text": f.read()})
    return units


def distill(unit):
    """Normalize a unit into (title, [facts]) — §9.5 rule 2: distill, don't dump.
    Placeholder: first '# ' heading (else first line) as title; top-level bullets as facts."""
    title, facts = "", []
    for line in unit["text"].splitlines():
        s = line.strip()
        if not title and s.startswith("# "):
            title = s[2:].strip()
        m = re.match(r'^-\s+(.*)$', s)
        if m:
            facts.append(m.group(1).strip())
    if not title:
        title = next((l.strip() for l in unit["text"].splitlines() if l.strip()), unit["stem"])[:80]
    if not facts:
        facts = [title]
    return title, facts


# ---------- contract mechanics: keep as-is ----------

def slugify(name):
    name = name.strip().lower()
    name = re.sub(r"[\s_]+", "-", name)
    name = re.sub(r"[^a-z0-9가-힣-]", "", name)
    return re.sub(r"-{2,}", "-", name).strip("-") or "unit"


def candidate_text(cid, title, facts, source_rel, date, connector_id):
    lines = ["---",
             "kind: candidate",
             "id: %s" % cid,
             "type: undecided",
             "title: %s" % title,
             "status: candidate",
             "confidence: %s" % CONFIDENCE,
             "created: %s" % date,
             "sources:",
             "  - %s" % source_rel,
             "---",
             "",
             "## Proposed Facts"]
    lines += ["- %s" % f for f in facts]
    lines += ["",
              "## Notes",
              '- Emitted by connector "%s" (connector_skeleton distill = naive heading/bullet '
              "extraction) — verify every fact against the source at INGEST." % connector_id,
              ""]
    return "\n".join(lines)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # safe output on Windows consoles (cp949)
    except Exception:
        pass
    argv = sys.argv[1:]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source, connector_id, date, dry = None, None, None, False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--source":
            source = os.path.abspath(argv[i + 1]); i += 2
        elif a == "--root":
            root = os.path.abspath(argv[i + 1]); i += 2
        elif a == "--connector-id":
            connector_id = argv[i + 1]; i += 2
        elif a == "--date":
            date = argv[i + 1]; i += 2
        elif a == "--dry-run":
            dry = True; i += 1
        else:
            print("unknown argument: %s" % a)
            sys.exit(2)
    if not source or not os.path.isdir(source):
        print("usage: python bin/connector_skeleton.py --source PATH [--root PATH] "
              "[--connector-id NAME] [--date YYYY-MM-DD] [--dry-run]")
        sys.exit(2)
    staging = os.path.join(root, "staging")
    if not os.path.isdir(staging):
        print("error: %s not found (is --root a template copy?)" % staging)
        sys.exit(2)
    cand_dir = os.path.join(staging, "candidates")
    if not os.path.isdir(cand_dir) and not dry:
        os.makedirs(cand_dir)  # inside the connector's write scope (§9.5 rule 1)
    connector_id = slugify(connector_id or os.path.basename(source.rstrip(os.sep)))
    date = date or datetime.date.today().isoformat()

    emitted, skipped = 0, 0
    for unit in extract_units(source):
        cid = "%s-%s" % (connector_id, slugify(unit["stem"]))          # reproducible (rule 6)
        out_path = os.path.join(cand_dir, cid + ".candidate.md")
        if os.path.exists(out_path):                                    # never edit in place (rule 5)
            skipped += 1
            print("skip (exists): %s" % cid)
            continue
        try:
            source_rel = os.path.relpath(unit["path"], root).replace(os.sep, "/")
        except ValueError:  # different drive — keep the absolute path as the real source
            source_rel = unit["path"].replace(os.sep, "/")
        title, facts = distill(unit)
        text = candidate_text(cid, title, facts, source_rel, date, connector_id)
        if dry:
            print("would emit: %s  (%d facts) <- %s" % (cid, len(facts), source_rel))
        else:
            with open(out_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            print("emitted: staging/candidates/%s.candidate.md  (%d facts)" % (cid, len(facts)))
        emitted += 1

    src_label = os.path.relpath(source, root).replace(os.sep, "/") if source.startswith(root) else source
    log_line = "%s [GEN] %s: scanned %s (%d units, %d skipped as existing) → candidates %d / edges 0 / synthesis 0" % (
        date, connector_id, src_label, emitted + skipped, skipped, 0 if dry else emitted)
    if dry:
        print("dry-run — nothing written. Would log: %s" % log_line)
        return
    log_path = os.path.join(staging, "STAGING-LOG.md")
    prefix = ""
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            existing = f.read()
        prefix = existing if existing.endswith("\n") else existing + "\n"
    else:
        prefix = "# STAGING LOG\n\n<!-- append-only. Generator/connector activity only. Format: SCHEMA.md §9.3. -->\n"
    with open(log_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(prefix + log_line + "\n")
    print("logged: %s" % log_line)


if __name__ == "__main__":
    main()
