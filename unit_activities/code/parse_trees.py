"""Constituency parse trees for the Unit 8 activity, drawn with matplotlib.

Each tree is written in bracketed form and rendered to PNG. The third sentence
is drawn twice because "with the telescope" can attach to the verb phrase
(the man used the telescope) or to the noun phrase (the dog had it).
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "images"
OUT.mkdir(exist_ok=True)
plt.rcParams["font.family"] = "Arial"


def parse(bracketed: str):
    """Turn '(S (NP (Det The) (N government)) ...)' into nested lists."""
    tokens = bracketed.replace("(", " ( ").replace(")", " ) ").split()
    pos = 0

    def node():
        nonlocal pos
        assert tokens[pos] == "("; pos += 1
        label = tokens[pos]; pos += 1
        children = []
        while tokens[pos] != ")":
            if tokens[pos] == "(":
                children.append(node())
            else:
                children.append(tokens[pos]); pos += 1
        pos += 1
        return (label, children)
    return node()


def width(tree):
    if isinstance(tree, str):
        return 1
    return max(1, sum(width(c) for c in tree[1]))


def depth(tree):
    if isinstance(tree, str):
        return 1
    return 1 + max(depth(c) for c in tree[1])


def draw(tree, title, filename):
    leaves = width(tree); levels = depth(tree)
    fig, ax = plt.subplots(figsize=(max(5, leaves * 1.25), levels * 0.95 + 0.6), dpi=200)
    ax.set_xlim(0, leaves); ax.set_ylim(-levels - 0.2, 0.6); ax.axis("off")
    ax.set_title(title, fontsize=11, loc="left", pad=8)

    def place(node, x0, level):
        if isinstance(node, str):
            ax.text(x0 + 0.5, -level, node, ha="center", va="center", fontsize=11, style="italic",
                    bbox=dict(fc="#eef0fb", ec="#4b3f8f", boxstyle="round,pad=0.3"))
            return x0 + 0.5
        label, children = node
        xs, cursor = [], x0
        for child in children:
            cx = place(child, cursor, level + 1)
            xs.append(cx); cursor += width(child)
        centre = sum(xs) / len(xs)
        ax.text(centre, -level, label, ha="center", va="center", fontsize=11, weight="bold",
                bbox=dict(fc="white", ec="none", pad=1.5))
        for cx in xs:
            ax.plot([centre, cx], [-level - 0.18, -level - 0.82], color="#4b3f8f", lw=1.2)
        return centre

    place(tree, 0, 0)
    fig.savefig(OUT / filename, bbox_inches="tight", facecolor="white")
    plt.close(fig)


TREES = [
    ("Sentence 1: The government raised interest rates.",
     "(S (NP (Det The) (N government)) (VP (V raised) (NP (N interest) (N rates))))",
     "parse_1_government.png"),
    ("Sentence 2: The internet gives everyone a voice.",
     "(S (NP (Det The) (N internet)) (VP (V gives) (NP (Pron everyone)) (NP (Det a) (N voice))))",
     "parse_2_internet.png"),
    ("Sentence 3a: The man saw the dog with the telescope. (PP attached to VP: the man used the telescope)",
     "(S (NP (Det The) (N man)) (VP (V saw) (NP (Det the) (N dog)) (PP (P with) (NP (Det the) (N telescope)))))",
     "parse_3a_telescope_vp.png"),
    ("Sentence 3b: The man saw the dog with the telescope. (PP attached to NP: the dog has the telescope)",
     "(S (NP (Det The) (N man)) (VP (V saw) (NP (NP (Det the) (N dog)) (PP (P with) (NP (Det the) (N telescope))))))",
     "parse_3b_telescope_np.png"),
]

if __name__ == "__main__":
    for title, bracketed, filename in TREES:
        draw(parse(bracketed), title, filename)
        print("wrote", filename)
