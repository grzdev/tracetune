#!/usr/bin/env python
"""
TraceTune: One-click upload to Hugging Face Hub.
Uploads the curated AgentTune EventLog and SFT dataset directly to your Hugging Face account.
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Upload TraceTune datasets to Hugging Face Hub")
    parser.add_argument("--repo-id", type=str, required=True, help="HF Repo ID in format: 'username/dataset-name'")
    parser.add_argument("--token", type=str, default=None, help="Hugging Face User Access Token (Write access)")
    parser.add_argument("--private", action="store_true", help="Make repository private (default: public)")

    args = parser.parse_args()

    try:
        from huggingface_hub import HfApi, login
    except ImportError:
        print("[ERROR] huggingface_hub is not installed. Run: py -m pip install huggingface_hub")
        sys.exit(1)

    if args.token:
        login(token=args.token)

    api = HfApi()

    # Verify who is logged in
    try:
        user_info = api.whoami()
        username = user_info.get("name")
        print(f"\n[AUTH] Authenticated with Hugging Face as: @{username}")
    except Exception as e:
        print("\n[AUTH ERROR] Could not verify Hugging Face credentials.")
        print("Please provide a valid write token via --token <your_token> or run 'huggingface-cli login'.")
        print("Get your token here: https://huggingface.co/settings/tokens")
        sys.exit(1)

    repo_id = args.repo_id
    if "/" not in repo_id:
        repo_id = f"{username}/{repo_id}"

    print(f"\n[HUB] Creating dataset repository: https://huggingface.co/datasets/{repo_id} ...")
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            private=args.private,
            exist_ok=True
        )
        print(f"[SUCCESS] Repository ready!")
    except Exception as e:
        print(f"[ERROR] Failed to create repo: {e}")
        sys.exit(1)

    # Files to upload
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"

    files_to_upload = [
        ("data/tracetune_sft.jsonl", data_dir / "tracetune_sft.jsonl"),
        ("data/tracetune_trajectories.jsonl", data_dir / "tracetune_trajectories.jsonl"),
    ]

    print("\n[UPLOADING] Uploading dataset files...")
    for path_in_repo, local_path in files_to_upload:
        if local_path.exists():
            print(f"- Uploading {local_path.name} ({local_path.stat().st_size / 1024:.1f} KB)...")
            api.upload_file(
                path_or_fileobj=str(local_path),
                path_in_repo=path_in_repo,
                repo_id=repo_id,
                repo_type="dataset",
                commit_message=f"Add {local_path.name}"
            )
        else:
            print(f"- [WARNING] File {local_path} not found.")

    # Upload Dataset Card
    card_content = f"""---
language:
- en
license: apache-2.0
tags:
- agenttune
- auditkit
- cohere
- tiny-aya
- ai-safety
- agentic-fine-tuning
size_categories:
- n<1K
---

# TraceTune: Agentic Fine-Tuning Trajectories (Lexsi Track 3)

Curated dataset of 300+ multi-step code and security investigation trajectories formatted for **Lexsi Labs' AgentTune** and **AuditKIT**, designed to post-train **Cohere Tiny Aya (~3.5B)**.

## Dataset Structure
* `data/tracetune_sft.jsonl`: Conversational Supervised Fine-Tuning format containing system, user, thought, tool calls, and observations.
* `data/tracetune_trajectories.jsonl`: Full Lexsi two-tier `EventLog` substrate (Tier 1 semantic transitions + Tier 2 granular tool tokens).

## Target Tasks
* CWE-89: SQL Injection
* CWE-287: JWT Algorithm 'none' Bypass
* CWE-798: Hardcoded Credentials
* CWE-1321: Prototype Pollution

## Citation & Hackathon
Built for the **Lexsi - AI Safety and Alignment Hackathon (Track 3: Agentic Fine-Tuning)** with Cohere Labs and Hugging Face.
GitHub: https://github.com/grzdev/tracetune
"""

    print("- Uploading README.md (Dataset Card)...")
    api.upload_file(
        path_or_fileobj=card_content.encode("utf-8"),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="dataset",
        commit_message="Add Dataset Card"
    )

    print("\n" + "=" * 60)
    print(f"🎉 DATASET PUBLISHED SUCCESSFULLY!")
    print(f"🔗 Public URL: https://huggingface.co/datasets/{repo_id}")
    print("=" * 60)
    print("Use this URL in your hackathon submission form!")

if __name__ == "__main__":
    main()
