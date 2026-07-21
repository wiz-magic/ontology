#!/usr/bin/env python3
"""
search.py — hybrid retriever over the canon (and optionally staging). Locator only.

Output is a POINTER list, never a source: read the canonical file a pointer
names and cite that ([[id]]); anything surfaced from staging/ keeps its grade
(candidate / opinion — not fact). Wired into operations/QUERY.md steps 1 and 4
and operations/INGEST.md step 3.

Usage:
    python bin/search.py "<query>"              # search ontology/ (canon)
    python bin/search.py "<query>" --staging    # + open candidates/edges + synthesis
    python bin/search.py "<query>" --top 15     # number of results (default 10)
    python bin/search.py "<query>" --root PATH  # operate on another template copy

Design (stdlib only; scans files at query time — no index files, so never stale):
- Distill-then-index: indexes the ontology's already-normalized units
  (objects/definitions), not raw sources. Retrieval quality comes from the
  normalization the template already enforces.
- Two granularities ("bursting"): whole files AND individual `## Facts` /
  `## Proposed Facts` bullets, each bullet prefixed with its parent's
  title/type so a single fact inside a big object is findable on its own.
- Two retrievers fused by Reciprocal Rank Fusion (RRF, k=60):
    * BM25 over word tokens — exact tokens win (IDs, error strings, flags)
    * character trigram TF-IDF cosine — fuzzy/partial match (morphology, typos)
  Consensus across retrievers beats a single strong vote.
- Per-file cap: fact-level and file-level hits of the same file merge into one
  result line (best-matching snippet shown), keeping the top-N diverse.
- No age decay / recency-wins ranking: freshness and contradiction handling
  belong to INGEST/LINT, never to a ranker. Staging hits are labeled with
  their grade + created date instead.
- Embedding hook: a real vector retriever can be added as a third ranking and
  fused by the same RRF; the interface is rank(query) -> [(doc_index, score)].
"""
import sys
import os
import re
import math
from collections import Counter

RRF_K = 60          # RRF smoothing constant (consensus over single strong vote)
PER_RANKING_CAP = 200
SNIPPET_LEN = 160

CANON_DIRS = [("types", "type"), ("objects", "object"), ("links", "link-type"),
              ("actions", "action"), ("roles", "role")]
STAGING_DIRS = [("candidates", "candidate", "Proposed Facts"),
                ("edges", "edge-candidate", "Evidence"),
                ("synthesis", "opinion", "Synthesized Answer")]


# ---------- parsing (same conventions as build_index.py) ----------

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


def section_bullets(body, header):
    """All bullets of the '## <header>' section."""
    in_sec = False
    out = []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("## "):
            in_sec = (s[3:].strip().lower() == header.lower())
            continue
        if in_sec:
            m = re.match(r'^\s*-\s+(.*)$', line)
            if m:
                out.append(m.group(1).strip())
    return out


# ---------- corpus ----------

def load(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def collect(root, include_staging):
    """One record per file + one per Facts bullet ("burst"). Pointer data only."""
    records = []

    def add(oid, label, rel, text, snippet, date):
        records.append({"id": oid, "label": label, "rel": rel,
                        "text": text, "snippet": snippet, "date": date})

    ont = os.path.join(root, "ontology")
    for sub, label in CANON_DIRS:
        d = os.path.join(ont, sub)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".md") or name.startswith("_"):
                continue
            raw = load(os.path.join(d, name))
            fm, body = parse_frontmatter(raw)
            rel = "ontology/%s/%s" % (sub, name)
            oid = fm.get("id") or name[:-3]
            title = fm.get("title") or oid
            lab = label + " archived" if fm.get("status") == "archived" else label
            facts = section_bullets(body, "Facts") if label == "object" else []
            snippet = facts[0] if facts else (fm.get("description") or title)
            date = fm.get("updated", "")
            add(oid, lab, rel, title + "\n" + raw, snippet, date)
            ctx = "%s (%s)" % (title, fm.get("type") or label)
            for fact in facts:
                add(oid, lab, rel, "%s: %s" % (ctx, fact), fact, date)

    if include_staging:
        stg = os.path.join(root, "staging")
        for sub, label, bullets_header in STAGING_DIRS:
            d = os.path.join(stg, sub)
            if not os.path.isdir(d):
                continue
            for dirpath, _dirs, files in os.walk(d):
                for name in sorted(files):
                    if not name.endswith(".md") or name.startswith("_"):
                        continue
                    path = os.path.join(dirpath, name)
                    raw = load(path)
                    fm, body = parse_frontmatter(raw)
                    # only OPEN candidates/edges: promoted live in canon, rejected are noise
                    if label != "opinion" and fm.get("status") != "candidate":
                        continue
                    rel = os.path.relpath(path, root).replace(os.sep, "/")
                    oid = fm.get("id") or name.split(".")[0]
                    title = fm.get("title") or fm.get("question") or oid
                    bullets = section_bullets(body, bullets_header)
                    snippet = bullets[0] if bullets else title
                    date = fm.get("created", "")
                    add(oid, label, rel, title + "\n" + raw, snippet, date)
                    ctx = "%s (%s)" % (title, label)
                    for b in bullets:
                        add(oid, label, rel, "%s: %s" % (ctx, b), b, date)
    return records


# ---------- retrievers ----------

ASCII_WORD = re.compile(r"[a-z0-9]+")
HANGUL_RUN = re.compile(r"[가-힣]+")
CJK_RUN = re.compile(r"[一-鿿぀-ヿ]+")


def word_tokens(text):
    """ascii words + Hangul/CJK runs + their character bigrams (agglutinative morphology)."""
    text = text.lower()
    toks = ASCII_WORD.findall(text)
    for run in HANGUL_RUN.findall(text) + CJK_RUN.findall(text):
        toks.append(run)
        toks.extend(run[i:i + 2] for i in range(len(run) - 1))
    return toks


def char_ngrams(text, n=3):
    text = re.sub(r"\s+", " ", text.lower()).strip()
    if not text:
        return []
    if len(text) <= n:
        return [text]
    return [text[i:i + n] for i in range(len(text) - n + 1)]


def bm25_rank(doc_tokens, q_tokens, k1=1.5, b=0.75):
    N = len(doc_tokens)
    if N == 0 or not q_tokens:
        return []
    df = Counter()
    for toks in doc_tokens:
        df.update(set(toks))
    avgdl = (sum(len(t) for t in doc_tokens) / float(N)) or 1.0
    q = set(q_tokens)
    scores = []
    for i, toks in enumerate(doc_tokens):
        if not toks:
            continue
        tf = Counter(toks)
        dl = len(toks)
        s = 0.0
        for t in q:
            if t not in tf:
                continue
            idf = math.log((N - df[t] + 0.5) / (df[t] + 0.5) + 1.0)
            s += idf * (tf[t] * (k1 + 1)) / (tf[t] + k1 * (1 - b + b * dl / avgdl))
        if s > 0:
            scores.append((i, s))
    scores.sort(key=lambda x: -x[1])
    return scores


def tfidf_rank(doc_grams, q_grams):
    N = len(doc_grams)
    if N == 0 or not q_grams:
        return []
    df = Counter()
    for grams in doc_grams:
        df.update(set(grams))

    def vec(grams):
        tf = Counter(grams)
        v = {}
        for t, c in tf.items():
            d = df.get(t)
            if not d:
                continue
            v[t] = (1.0 + math.log(c)) * (math.log(N / float(d)) + 1.0)
        norm = math.sqrt(sum(w * w for w in v.values())) or 1.0
        return v, norm

    qv, qn = vec(q_grams)
    scores = []
    for i, grams in enumerate(doc_grams):
        dv, dn = vec(grams)
        small, big = (qv, dv) if len(qv) < len(dv) else (dv, qv)
        s = sum(w * big[t] for t, w in small.items() if t in big)
        s /= (qn * dn)
        if s > 0:
            scores.append((i, s))
    scores.sort(key=lambda x: -x[1])
    return scores


def rrf_fuse(rankings, k=RRF_K):
    """weight/(k+rank) summed per doc across all rankings it appears in."""
    scores = {}
    for ranking in rankings:
        for rank, (i, _s) in enumerate(ranking[:PER_RANKING_CAP]):
            scores[i] = scores.get(i, 0.0) + 1.0 / (k + rank + 1)
    return scores


# ---------- CLI ----------

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # safe output on Windows consoles (cp949)
    except Exception:
        pass
    argv = sys.argv[1:]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    top, staging, positional = 10, False, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--top":
            top = int(argv[i + 1]); i += 2
        elif a == "--root":
            root = os.path.abspath(argv[i + 1]); i += 2
        elif a == "--staging":
            staging = True; i += 1
        else:
            positional.append(a); i += 1
    query = " ".join(positional).strip()
    if not query:
        print('usage: python bin/search.py "<query>" [--staging] [--top N] [--root PATH]')
        sys.exit(2)
    if not os.path.isdir(os.path.join(root, "ontology")):
        print("error: %s/ontology not found" % root)
        sys.exit(2)

    records = collect(root, staging)
    if not records:
        print("corpus empty — no canonical files%s yet." % (" or open staging entries" if staging else ""))
        return

    fused = rrf_fuse([
        bm25_rank([word_tokens(r["text"]) for r in records], word_tokens(query)),
        tfidf_rank([char_ngrams(r["text"]) for r in records], char_ngrams(query)),
    ])
    if not fused:
        print('no match for "%s" (corpus: %d units).' % (query, len(records)))
        return

    groups = {}  # rel path -> (best score, best record index)
    for i, s in fused.items():
        rel = records[i]["rel"]
        if rel not in groups or s > groups[rel][0]:
            groups[rel] = (s, i)
    ranked = sorted(groups.items(), key=lambda kv: -kv[1][0])[:top]

    nfiles = len(set(r["rel"] for r in records))
    print('query: %s   (corpus: %d units / %d files%s)'
          % (query, len(records), nfiles, ", staging included" if staging else ""))
    for n, (rel, (_s, i)) in enumerate(ranked, 1):
        r = records[i]
        tag = r["label"]
        if r["label"] in ("candidate", "edge-candidate", "opinion") and r["date"]:
            tag += " " + r["date"]
        snippet = r["snippet"]
        if len(snippet) > SNIPPET_LEN:
            snippet = snippet[:SNIPPET_LEN - 3] + "..."
        print("%2d. [%s] %s — %s" % (n, tag, r["id"], rel))
        print("    > %s" % snippet)
    print()
    print("pointers only — read the file and cite [[id]]; candidate/opinion results are not facts (SCHEMA.md §9).")


if __name__ == "__main__":
    main()
