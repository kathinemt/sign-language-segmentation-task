# written with help from Claude
import argparse
import pympi
from sklearn.metrics import f1_score, jaccard_score
import numpy as np

# Label ids
O, B, I = 0, 1, 2


def parse_eaf_segments(eaf_path: str, tier_id: str):
    """Extract (start_ms, end_ms) segments from a given tier in an .eaf file, via pympi."""
    eaf_file = pympi.Eaf(eaf_path)

    # Returns a list of (start_ms, end_ms, value) for time-alignable annotations on this tier.
    annotations = eaf_file.get_annotation_data_for_tier(tier_id)
    segments = [(start, end) for start, end, _value in annotations]
    segments.sort()
    return segments


def ms_to_frame(ms: float, fps: float) -> int:
    return int(round(ms / 1000.0 * fps))


def segments_to_bio(segments, n_frames: int, fps: float) -> np.ndarray:
    """Convert (start_ms, end_ms) segments into a per-frame BIO label array."""
    labels = np.full(n_frames, O, dtype=int)
    for start_ms, end_ms in segments:
        start_f = ms_to_frame(start_ms, fps)
        end_f = min(ms_to_frame(end_ms, fps), n_frames - 1)
        if start_f >= n_frames or start_f > end_f:
            continue
        labels[start_f] = B
        if end_f > start_f:
            labels[start_f + 1: end_f + 1] = I
    return labels


def macro_f1(gold: np.ndarray, pred: np.ndarray) -> float:
    """Macro-averaged per-class F1 over {B, I, O} to match paper F1 calc."""
    return f1_score(gold, pred, labels=[O, B, I], average="macro", zero_division=0)


def total_iou(gold_labels: np.ndarray, pred_labels: np.ndarray) -> float:
    """Binary 'inside vs outside' IoU calculated with scikit's Jaccard score."""
    gold_binary = (gold_labels != O).astype(int)
    pred_binary = (pred_labels != O).astype(int)
    return float(jaccard_score(gold_binary, pred_binary, labels=[1], average="binary", zero_division=0))


def evaluate(gold_eaf: str, pred_eaf: str, gold_tier: str, pred_tier: str, fps: float):
    gold_segments = parse_eaf_segments(gold_eaf, gold_tier)
    pred_segments = parse_eaf_segments(pred_eaf, pred_tier)

    total_ms = max(
        max((e for _, e in gold_segments), default=0),
        max((e for _, e in pred_segments), default=0),
    )
    n_frames = ms_to_frame(total_ms, fps) + 1

    gold_labels = segments_to_bio(gold_segments, n_frames, fps)
    pred_labels = segments_to_bio(pred_segments, n_frames, fps)

    return {
        "gold_tier": gold_tier,
        "pred_tier": pred_tier,
        "n_gold_segments": len(gold_segments),
        "n_pred_segments": len(pred_segments),
        "frame_f1": macro_f1(gold_labels, pred_labels),
        "iou": total_iou(gold_labels, pred_labels),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold_eaf", required=True, help="Path to the gold-standard .eaf file")
    parser.add_argument("--pred_eaf", required=True, help="Path to your model's predicted .eaf file")
    parser.add_argument(
        "--gold-tier",
        required=True,
        help="Tier ID to read from the gold .eaf (e.g. 'Lexem_Gebärde_r_B' for signs, "
        "'Deutsche_Übersetzung_B' for phrases in the Public DGS Corpus format).",
    )
    parser.add_argument(
        "--pred-tier",
        required=True,
        help="Tier ID to read from the predicted .eaf (e.g. 'SIGN' or 'SENTENCE').",
    )
    args = parser.parse_args()

    results = evaluate(args.gold_eaf, args.pred_eaf, args.gold_tier, args.pred_tier, fps=25.0)

    print(f"Gold tier: {results['gold_tier']}  |  Pred tier: {results['pred_tier']}")
    print(f"  Gold segments: {results['n_gold_segments']}")
    print(f"  Pred segments: {results['n_pred_segments']}")
    print(f"  Frame-level macro F1 (B/I/O): {results['frame_f1']:.4f}")
    print(f"  IoU: {results['iou']:.4f}")


if __name__ == "__main__":
    main()
