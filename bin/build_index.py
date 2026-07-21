#!/usr/bin/env python3
"""
build_index.py — regenerate ontology/INDEX.md from file frontmatter.

Reference implementation for parallel mode (Phase 3), where multiple agents
must not hand-edit INDEX.md concurrently (SCHEMA.md sections 7 and 9.4), and for
big ontologies (section 7.1 growth rule). Stdlib only.

Usage:
    python bin/build_index.py                      # rewrite <root>/ontology/INDEX.md
    python bin/build_index.py --check              # verify only; exit 1 on mismatch (CI hook)
    python bin/build_index.py --root PATH          # operate on another template copy
    python bin/build_index.py --split-threshold N  # split Objects by type above N entries (default 200)

Conventions:
- Scans ontology/{types,objects,links,actions,roles}/*.md.
- Skips files starting with '_' (templates). Never scans staging/ (not canonical).
- Object summary = first bullet of the '## Facts' section (SCHEMA.md section 7).
- Objects with `status: archived` keep their line, marked [archived].
- Above the split threshold, writes ontology/INDEX-objects-<type>.md sub-indexes
  and the main Objects section becomes pointers (SCHEMA.md section 7.1).
- Parses only the frontmatter subset this template uses ("key: value" and "- list").
"""
import sys
import os
import re

GENERATED_NOTE = ("<!-- Derived by bin/build_index.py — do not hand-edit in parallel mode. "
                  "Format: SCHEMA.md section 7. -->")
SUBINDEX_RE = re.compile(r"^INDEX-objects-.+\.md$")


def parse_frontmatter(text):
    """Return (dict, body). Handles only top-level 'key: value' and '- item' lists."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_raw = text[3:end].strip("\n")
    body = text[end + 4:]
    data = {}
    cur_key = None
    for line in fm_raw.splitlines():
        if not line.strip():
            continue
        top = re.match(r'^(\w[\w-]*):\s*(.*)$', line)
        if top and not line[0].isspace():
            key, val = top.group(1), top.group(2).strip()
            if val == "":
                data[key] = []
                cur_key = key
            else:
                data[key] = val.strip('"').strip("'")
                cur_key = None
        else:
            item = re.match(r'^\s*-\s+(.*)$', line)
            if item and cur_key is not None:
                data[cur_key].append(item.group(1).strip().strip('"').strip("'"))
    return data, body


def first_fact(body):
    """First bullet of the '## Facts' section."""
    in_facts = False
    for line in body.splitlines():
        if line.strip().startswith("## Facts"):
            in_facts = True
            continue
        if in_facts:
            if line.strip().startswith("##"):
                break
            m = re.match(r'^\s*-\s+(.*)$', line)
            if m:
                return m.group(1).strip()
    return ""


def read_dir(ont, sub):
    d = os.path.join(ont, sub)
    out = []
    if not os.path.isdir(d):
        return out
    for name in sorted(os.listdir(d)):
        if not name.endswith(".md") or name.startswith("_"):
            continue
        with open(os.path.join(d, name), encoding="utf-8") as f:
            text = f.read()
        fm, body = parse_frontmatter(text)
        fm["_file"] = name
        fm["_body"] = body
        out.append(fm)
    return out


def section(title, items, render):
    lines = ["## " + title]
    if items:
        lines.extend(render(it) for it in items)
    else:
        lines.append("(none yet)")
    lines.append("")
    return lines


def obj_line(o):
    summ = first_fact(o["_body"])
    tail = " — " + summ if summ else ""
    archived = " [archived]" if o.get("status") == "archived" else ""
    return "- [%s](objects/%s) (%s)%s — %s%s" % (
        o.get("id", "?"), o["_file"], o.get("type", "?"), archived, o.get("title", ""), tail)


def build(ont, threshold):
    types = read_dir(ont, "types")
    objects = read_dir(ont, "objects")
    links = read_dir(ont, "links")
    actions = read_dir(ont, "actions")
    roles = read_dir(ont, "roles")
    counts = {"types": len(types), "objects": len(objects), "links": len(links),
              "actions": len(actions), "roles": len(roles)}

    subindexes = {}
    lines = ["# INDEX", "", GENERATED_NOTE, ""]
    lines += section("Types", types,
                     lambda t: "- [%s](types/%s) — %s" % (t.get("id", "?"), t["_file"], t.get("description", "")))

    if len(objects) > threshold:
        by_type = {}
        for o in objects:
            by_type.setdefault(o.get("type", "?"), []).append(o)
        lines.append("## Objects")
        lines.append("Split by type (%d objects) — SCHEMA.md section 7.1:" % len(objects))
        for t in sorted(by_type):
            fname = "INDEX-objects-%s.md" % t
            lines.append("- [%s](%s) — %d objects" % (t, fname, len(by_type[t])))
            sub = ["# INDEX — objects: %s" % t, "", GENERATED_NOTE, ""]
            sub += [obj_line(o) for o in by_type[t]]
            subindexes[fname] = "\n".join(sub).rstrip() + "\n"
        lines.append("")
    else:
        lines += section("Objects", objects, obj_line)

    lines += section("Link Types", links,
                     lambda l: "- [%s](links/%s) — %s → %s" % (l.get("id", "?"), l["_file"], l.get("from", "?"), l.get("to", "?")))
    lines += section("Actions", actions,
                     lambda a: "- [%s](actions/%s) [%s] — %s" % (a.get("id", "?"), a["_file"], a.get("tier", "?"), a.get("title", "")))
    lines += section("Roles", roles,
                     lambda r: "- [%s](roles/%s) [max %s] — %s" % (r.get("id", "?"), r["_file"], r.get("max-tier", "?"), r.get("description", "")))
    return "\n".join(lines).rstrip() + "\n", subindexes, counts


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # safe output on Windows consoles (cp949)
    except Exception:
        pass
    argv = sys.argv[1:]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    threshold = 200
    if "--root" in argv:
        root = os.path.abspath(argv[argv.index("--root") + 1])
    if "--split-threshold" in argv:
        threshold = int(argv[argv.index("--split-threshold") + 1])
    ont = os.path.join(root, "ontology")
    if not os.path.isdir(ont):
        print("error: %s not found" % ont)
        sys.exit(2)

    content, subindexes, counts = build(ont, threshold)
    index_path = os.path.join(ont, "INDEX.md")
    existing_subs = [n for n in os.listdir(ont) if SUBINDEX_RE.match(n)]

    if "--check" in argv:
        ok = True

        def same(path, want):
            cur = ""
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    cur = f.read()
            return cur.rstrip() == want.rstrip()

        if not same(index_path, content):
            ok = False
            print("INDEX.md is out of date")
        for name, want in subindexes.items():
            if not same(os.path.join(ont, name), want):
                ok = False
                print("%s is out of date" % name)
        for name in existing_subs:
            if name not in subindexes:
                ok = False
                print("%s is stale (no longer generated)" % name)
        if not ok:
            print("→ regenerate with: python bin/build_index.py")
            sys.exit(1)
        print("INDEX.md matches")
        return

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)
    for name, want in subindexes.items():
        with open(os.path.join(ont, name), "w", encoding="utf-8") as f:
            f.write(want)
    for name in existing_subs:
        if name not in subindexes:
            os.remove(os.path.join(ont, name))
    print("INDEX.md regenerated: types %(types)d, objects %(objects)d, links %(links)d, "
          "actions %(actions)d, roles %(roles)d" % counts
          + (" (split into %d sub-indexes)" % len(subindexes) if subindexes else ""))


if __name__ == "__main__":
    main()
