#!/usr/bin/env python3
"""Prepare AISHELL manifests and an optional digit-command subset.

This script reads AISHELL transcripts and wav files, then exports:
1) a full manifest (JSONL)
2) an optional digit-command manifest filtered by keywords

Example:
    python scripts/prepare_aishell_digits.py \
      --aishell-root /data/aishell \
      --output-dir data/manifests \
      --build-digit-subset
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List


DEFAULT_KEYWORDS = [
    "零",
    "一",
    "二",
    "两",
    "三",
    "四",
    "五",
    "六",
    "七",
    "八",
    "九",
    "十",
    "百",
    "千",
    "万",
    "点",
    "拨号",
    "呼叫",
    "打开",
    "关闭",
    "上一首",
    "下一首",
    "音量",
]


@dataclass
class Utterance:
    utt_id: str
    audio_path: str
    split: str
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare AISHELL full/digit manifests")
    parser.add_argument(
        "--aishell-root",
        type=Path,
        required=True,
        help="AISHELL root path (expects wav/ and transcript/aishell_transcript_v0.8.txt)",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Output manifest dir")
    parser.add_argument(
        "--build-digit-subset",
        action="store_true",
        help="Also export manifest filtered by digit-command keywords",
    )
    parser.add_argument(
        "--keywords",
        type=str,
        default=",".join(DEFAULT_KEYWORDS),
        help="Comma-separated keywords used for subset filtering",
    )
    return parser.parse_args()


def read_transcripts(transcript_file: Path) -> Dict[str, str]:
    transcript_map: Dict[str, str] = {}
    with transcript_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                continue
            utt_id, text = parts
            transcript_map[utt_id] = text
    return transcript_map


def detect_split(audio_path: Path) -> str:
    parts = [p.lower() for p in audio_path.parts]
    for split in ("train", "dev", "test"):
        if split in parts:
            return split
    return "unknown"


def collect_utterances(aishell_root: Path, transcript_map: Dict[str, str]) -> List[Utterance]:
    wav_root = aishell_root / "wav"
    utterances: List[Utterance] = []
    for wav in wav_root.rglob("*.wav"):
        utt_id = wav.stem
        text = transcript_map.get(utt_id)
        if text is None:
            continue
        utterances.append(
            Utterance(
                utt_id=utt_id,
                audio_path=str(wav.resolve()),
                split=detect_split(wav),
                text=text,
            )
        )
    return utterances


def contains_keywords(text: str, keywords: Iterable[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def normalize_keywords(raw_keywords: str) -> List[str]:
    keywords = [item.strip() for item in raw_keywords.split(",") if item.strip()]
    # Remove duplicates and sort by length to prefer longer phrase matches for debug/search usage.
    return sorted(set(keywords), key=len, reverse=True)


def write_jsonl(path: Path, utterances: Iterable[Utterance]) -> int:
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for item in utterances:
            f.write(
                json.dumps(
                    {
                        "utt_id": item.utt_id,
                        "audio_path": item.audio_path,
                        "split": item.split,
                        "text": item.text,
                    },
                    ensure_ascii=False,
                )
            )
            f.write("\n")
            count += 1
    return count


def main() -> None:
    args = parse_args()
    aishell_root = args.aishell_root
    transcript_file = aishell_root / "transcript" / "aishell_transcript_v0.8.txt"

    if not transcript_file.exists():
        raise FileNotFoundError(f"Transcript file not found: {transcript_file}")

    transcripts = read_transcripts(transcript_file)
    utterances = collect_utterances(aishell_root, transcripts)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    full_manifest = args.output_dir / "aishell_full.jsonl"
    full_count = write_jsonl(full_manifest, utterances)
    print(f"[OK] Full manifest: {full_manifest} ({full_count} utterances)")

    if args.build_digit_subset:
        keywords = normalize_keywords(args.keywords)
        subset = [u for u in utterances if contains_keywords(u.text, keywords)]
        subset_manifest = args.output_dir / "aishell_digit_commands.jsonl"
        subset_count = write_jsonl(subset_manifest, subset)
        print(
            "[OK] Digit subset manifest: "
            f"{subset_manifest} ({subset_count} utterances, {len(keywords)} keywords)"
        )


if __name__ == "__main__":
    main()
