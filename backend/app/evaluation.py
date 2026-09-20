"""Threshold-sweep metrics for labelled face-pair cosine scores."""
import argparse
import csv
from pathlib import Path


def metrics(scores: list[float], labels: list[int], threshold: float) -> dict[str, float]:
    predicted = [score >= threshold for score in scores]
    tp = sum(p and y == 1 for p, y in zip(predicted, labels)); fp = sum(p and y == 0 for p, y in zip(predicted, labels))
    tn = sum(not p and y == 0 for p, y in zip(predicted, labels)); fn = sum(not p and y == 1 for p, y in zip(predicted, labels))
    total = max(1, len(labels))
    return {"threshold": threshold, "accuracy": (tp + tn) / total, "precision": tp / max(1, tp + fp), "recall": tp / max(1, tp + fn), "far": fp / max(1, fp + tn), "frr": fn / max(1, fn + tp), "tpr": tp / max(1, tp + fn), "fpr": fp / max(1, fp + tn)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate labelled cosine scores and print CSV metrics.")
    parser.add_argument("pairs_csv", type=Path, help="CSV containing score,label columns (label: 1=same, 0=different)")
    parser.add_argument("--start", type=float, default=0.1); parser.add_argument("--stop", type=float, default=0.8); parser.add_argument("--step", type=float, default=0.01)
    args = parser.parse_args()
    with args.pairs_csv.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    scores, labels = [float(r["score"]) for r in rows], [int(r["label"]) for r in rows]
    writer = csv.DictWriter(__import__("sys").stdout, fieldnames=list(metrics(scores, labels, args.start)))
    writer.writeheader(); value = args.start
    while value <= args.stop + 1e-9:
        writer.writerow(metrics(scores, labels, round(value, 6))); value += args.step


if __name__ == "__main__": main()
