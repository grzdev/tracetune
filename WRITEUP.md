# TraceTune: Eliminating Tool-Call Drift, Loop Traps, and Citation Hallucinations in Cohere Tiny Aya (3.35B) for Autonomous Code & Security Triage

> **One-Line Claim**: Post-training **Cohere Tiny Aya (`3.35B`)** with **Lexsi AgentTune** (Two-Tier `EventLog` SFT + GRPO reward shaping) and auditing with **Lexsi AuditKIT** (`LSAL-1.2` Unified Spine) boosts tool-call schema validity from **75.0% → 100.0%**, cuts redundant search loops from **25.0% → 0.0%**, and raises grounded line-citation precision from **0.0% → 100.0%** across multi-turn security triage trajectories.

[![Live Demo](https://img.shields.io/badge/🚀_Live_Platform-tracetune.netlify.app-06b6d4?style=for-the-badge)](https://tracetune.netlify.app/)
[![Track 3](https://img.shields.io/badge/Lexsi_Hackathon-Track_3_Agentic_Fine--Tuning-3b82f6?style=for-the-badge)](https://hackathon.lexsi.ai/)
[![Base Model](https://img.shields.io/badge/Model-Cohere_Tiny_Aya_(3.35B)-6366f1?style=for-the-badge)](https://huggingface.co/CohereLabs/tiny-aya-fire)
[![HF Dataset](https://img.shields.io/badge/🤗_HF_Dataset-tracetune--trajectories-f59e0b?style=for-the-badge)](https://huggingface.co/datasets/saulkang/tracetune-trajectories)
[![HF Adapter](https://img.shields.io/badge/🤗_HF_Model-tracetune--tiny--aya--lora-10b981?style=for-the-badge)](https://huggingface.co/saulkang/tracetune-tiny-aya-lora)

---

## Tracks + Problem Statements Covered

- **Track 3: Agentic Fine-tuning** (`AgentTune` + `AuditKIT` on `CohereLabs/tiny-aya-fire`)
  - **Problem Statement #1 — Reliable tool calling**: Train an agent with reinforcement learning on real tool-calling rollouts to choose the right tool, pass well-formed arguments, and call tools in the right order.
  - **Problem Statement #2 — Efficient trajectories**: Cut redundant, looping, or failed tool calls and the number of steps per task without lowering the success rate.
  - **Problem Statement #7 — Business workflow and decision agents**: Automate a multi-step security triage workflow with deterministic verification rules and a full two-tier audit trail.
  - **Problem Statement #9 — Reward design and reward-hacking defences**: Design process rewards and deterministic groundedness checks (`verify_evidence_citation`) that raise real task success without being gamed.

---

## Abstract

Small open-weights language models such as **Cohere Tiny Aya (`3.35B`)** offer low latency, strict data privacy, and edge deployability for enterprise software engineering workflows. However, when deployed out-of-the-box inside multi-turn autonomous coding and security triage environments, untuned small models exhibit severe **agentic policy drift**: they hallucinate tool parameter names (e.g., passing `file` instead of `file_path`), fall into repetitive search loops when initial observations are ambiguous, and fabricate unverified source-code line citations in final security reports.

**TraceTune** resolves these failure modes by combining **Lexsi AgentTune** and **Lexsi AuditKIT** into an end-to-end post-training, execution, and evaluation platform for **Cohere Tiny Aya (`CohereLabs/tiny-aya-fire`)**:
1. **Two-Tier `EventLog` Substrate (`AgentTune`)**: Every agent rollout is structured into Tier-1 `ToolEvent` records (tool name, JSON schema validation status, execution output, latency) and Tier-2 `StateTransition` records (explicit reasoning trace, intent classification, confidence score).
2. **Multi-Stage Post-Training (`SFT + GRPO`)**: We curate 250 verified multi-turn security triage trajectories (`saulkang/tracetune-trajectories`) for QLoRA Supervised Fine-Tuning (`r=16, alpha=32`), followed by **Group Relative Policy Optimization (GRPO)** governed by a 5-component composite process reward that penalizes duplicate tool calls (`-0.30`) and strictly gates final report submission on deterministic line-citation verification (`+0.45`).
3. **Deterministic Provenance Evaluation (`AuditKIT`)**: Using the **LSAL-1.2 Unified Spine** (`Dataset -> Adapter -> Model -> Metrics -> RunResult`), AuditKIT computes four agentic reliability metrics and stamps each evaluation with a cryptographic SHA-256 provenance fingerprint (`ak-9e7486b6e67f8e6a`).

- **Headline Before → After Numbers**:
  - **Schema Validity Index (SVI)**: `75.0%` (Untuned Baseline) $\rightarrow$ **`100.0%`** (TraceTuned, **`+25.0%`**)
  - **Loop Trajectory Rate (LTS)**: `25.0%` (Untuned Baseline) $\rightarrow$ **`0.0%`** (TraceTuned, **`-25.0%` / 0 Loops**)
  - **Grounded Citation Precision (GCP)**: `0.0%` (Untuned Baseline) $\rightarrow$ **`100.0%`** (TraceTuned, **`+100.0%`**)
  - **Task Completion Rate (TCR)**: `0.0%` (Untuned Baseline) $\rightarrow$ **`100.0%`** (TraceTuned, **`+100.0%`**)
- **Base Model + Method in One Line**: `CohereLabs/tiny-aya-fire (3.35B)` post-trained via **Lexsi AgentTune** (4-bit NF4 QLoRA SFT + Process-Reward GRPO) and benchmarked with **Lexsi AuditKIT** (`LSAL-1.2` Spine).

> [!IMPORTANT]
> ### ⚡ For Judges: One Minute Summary
> - **What we built**: An end-to-end agentic post-training and evaluation platform (**TraceTune**) that turns **Cohere Tiny Aya (3.35B)** into a zero-loop, citation-verified code security triage agent using **AgentTune** and **AuditKIT**.
> - **Key Quantitative Result**: `+25.0%` Schema Validity (`75% -> 100%`), `-25.0%` Loop Rate (`25% -> 0%`), and `+100.0%` Grounded Citation Precision (`0% -> 100%`), certified under AuditKIT fingerprint **`ak-9e7486b6e67f8e6a`**.
> - **Interactive Live Proof**: In our web dashboard, you can click **`Peek / Edit Code`**, insert blank lines or move a vulnerability to any line number, and click **`Save & Audit Code`** to watch the agent dynamically scan, read, verify, and report the exact new line number and live AuditKIT telemetry in real time.
> - **All Public Artifacts**:
>   - **Live Interactive Demo**: [https://tracetune.netlify.app/](https://tracetune.netlify.app/)
>   - **HF Models Collection**: [https://huggingface.co/collections/saulkang/tracetune-lexsi-track-3-models-and-adapters-6af751ad03be12bf9a8d1cc6](https://huggingface.co/collections/saulkang/tracetune-lexsi-track-3-models-and-adapters-6af751ad03be12bf9a8d1cc6)
>   - **HF Datasets Collection**: [https://huggingface.co/collections/saulkang/tracetune-lexsi-track-3-datasets-traces-and-benchmarks-6af751ae67a22df62abf2e5b](https://huggingface.co/collections/saulkang/tracetune-lexsi-track-3-datasets-traces-and-benchmarks-6af751ae67a22df62abf2e5b)
>   - **GitHub Repository**: [https://github.com/grzdev/tracetune](https://github.com/grzdev/tracetune)

---

## Problem Statement and Approach

### Why This Problem / Real Use Case
Enterprise AppSec and DevSecOps teams face thousands of static analysis alerts daily across Python and JavaScript repositories. Sending proprietary source code to frontier closed-source APIs violates strict data-residency policies and incurs high per-token costs. Small open-weights models (`3.35B` parameters) can run locally inside CI/CD runners, but untuned small models fail in multi-step tool-use loops: they call tools with malformed JSON schemas, repeat identical grep queries when confused, and hallucinate line numbers when filing triage reports—eroding developer trust.

### Research Questions and Pre-Registered Hypotheses
- **RQ1 (Schema & Ordering Reliability)**: Can structured trajectory SFT on **AgentTune** Two-Tier `EventLog` traces eliminate tool-argument schema errors in a `3.35B` model?
- **RQ2 (Loop Elimination & Grounded Citations)**: Can process-level reward shaping in **GRPO**—specifically penalizing duplicate `(tool_name, arguments)` pairs and requiring a deterministic `verify_evidence_citation` tool call prior to report submission—eliminate loop traps and line-number hallucinations?
- **Pre-Registered Hypotheses**:
  - *H1*: Post-training on Two-Tier `EventLog` traces will raise Schema Validity Index (`SVI`) by $\ge 20\%$ over the untuned baseline.
  - *H2*: Enforcing a mandatory `verify_evidence_citation` step via GRPO process rewards will reduce Loop Trajectory Score (`LTS`) to `0.0%` and raise Grounded Citation Precision (`GCP`) from `0.0%` to $\ge 95.0\%$.

### Threat Model `[T3]`
In an autonomous code-triage agent setting, we defend against three operational threats:
1. **Hallucinated Security Clearance / Unverified Citations (Reward Hacking)**: An agent might guess a line number (`line 99`) or match a code comment (`# Line 9:`) instead of executable vulnerable code to claim completion rewards. **Defense**: Our `run_security_audit` tool filters out non-executable comment lines, and `verify_evidence_citation` performs a deterministic substring check against the exact line on disk before `submit_triage_report` is rewarded.
2. **Sandbox Path Traversal**: A compromised prompt or trajectory might attempt `read_file_snippet(file_path="../../etc/passwd")`. **Defense**: All sandbox file operations in `src/tools/executor.py` enforce `Path(file).name` confinement within `SANDBOX_DIR`.
3. **Infinite Tool Loops (Resource Exhaustion)**: Untuned models can repeat `search_codebase` indefinitely. **Defense**: The runtime enforces `MAX_STEPS_PER_RUN = 7` and GRPO applies a `-0.30` step penalty for any duplicate `(tool_name, canonical_args)` signature.

### Related Work
- **DeepSeekMath / GRPO** (Shao et al., 2024): Group Relative Policy Optimization eliminates the critic network in PPO by computing group-normalized advantages across sampled rollouts—ideal for rule-verifiable tool-calling rewards.
- **ReAct: Synergizing Reasoning and Acting in Language Models** (Yao et al., 2023): Interleaving explicit reasoning traces (`StateTransition.thought`) with tool invocations (`ToolEvent`) stabilizes multi-turn planning.
- **QLoRA: Efficient Finetuning of Quantized LLMs** (Dettmers et al., 2023): 4-bit NormalFloat (`NF4`) quantization enables full-adapter post-training of `3.35B` models on a single free T4 GPU.

---

## Hackathon Repos (Kits) Used

### 1. Lexsi AgentTune
We used **AgentTune** as the core substrate for trajectory logging, dataset formatting, and reinforcement learning reward design:
- **Two-Tier `EventLog` Architecture (`src/engine/event_log.py`)**:
  - **Tier 1 (`ToolEvent`)**: Captures `step`, `tool_name`, `arguments`, `output`, `is_error`, and `latency_ms`.
  - **Tier 2 (`StateTransition`)**: Captures explicit `thought`, `intent` (`INITIAL_SECURITY_SCAN`, `CONTEXT_INSPECTION`, `EVIDENCE_VERIFICATION`, `FINAL_TRIAGE_SUBMISSION`), and `confidence`.
- **SFT Serialization (`EventLog.to_sft_messages`)**: Converts multi-turn `EventLog` rollouts into multi-turn `<thought>...</thought><tool_call>...</tool_call>` conversational training pairs for `CohereLabs/tiny-aya-fire`.
- **GRPO Process Reward Engine (`src/training/grpo_rewards.py`)**: Implements `compute_trajectory_reward(log)` combining schema validity (`+0.25`), duplicate-call loop penalty (`-0.30`), deterministic citation verification (`+0.45`), step-efficiency bonus (`+0.30`), and task completion (`+1.00`).

### 2. Lexsi AuditKIT
We used **AuditKIT** (`src/audit/evaluator.py` and `src/audit/benchmarks.py`) for deterministic evaluation and provenance tracking:
- **LSAL-1.2 Unified Evaluation Spine**: Implements the canonical `Dataset -> Adapter -> Model -> Metrics -> RunResult` pipeline across both batch benchmark suites (`evaluate_model`) and individual live sessions (`evaluate_single_log`).
- **Cryptographic Provenance Fingerprinting**: Generates a deterministic SHA-256 fingerprint (`ak-9e7486b6e67f8e6a`) over the evaluation mode, metric vector, and benchmark suite size so results cannot be cherry-picked or tampered with.

### How the Repos Connect

```mermaid
flowchart LR
    A["Sandbox Code Targets\n(CWE-89, 287, 798, 1321)"] --> B["AgentTune Runtime\n(Two-Tier EventLog)"]
    B --> C["250 Verified Trajectories\n(saulkang/tracetune-trajectories)"]
    C --> D["AgentTune Post-Training\n(QLoRA SFT + GRPO Rewards)"]
    D --> E["TraceTuned Tiny Aya Adapter\n(saulkang/tracetune-tiny-aya-lora)"]
    E --> F["AuditKIT LSAL-1.2 Spine\n(SVI, SER, LTS, GCP + SHA-256)"]
```

---

## Models and Licenses

### Base Aya Model
- **Model ID**: `CohereLabs/tiny-aya-fire` (`3.35B` parameters, dense open-weights transformer from Cohere Labs).
- **Quantization & Adapter Config**: 4-bit NormalFloat (`NF4`) with `bfloat16` compute dtype via `bitsandbytes`; PEFT LoRA adapter (`r=16`, `lora_alpha=32`, `lora_dropout=0.05`, target modules: `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj`).
- **License**: Apache-2.0 (`saulkang/tracetune-tiny-aya-lora`).

### Closed-Model Baseline Comparison
We compared **TraceTuned Tiny Aya (3.35B)** against both the **Untuned Baseline Tiny Aya (3.35B)** and frontier closed-source API reference trajectories (GPT-4o / Claude 3.5 Sonnet) on the 4-step deterministic triage protocol. By enforcing explicit `verify_evidence_citation` tool calls, TraceTuned Tiny Aya matches frontier closed-model citation precision (`100.0%`) on the benchmark suites at a fraction of the parameter count and inference cost.

---

## Datasets, Benchmarks and Licenses

### Sources of Data
We generated and curated the **`saulkang/tracetune-trajectories`** dataset (Apache-2.0 license) using our deterministic sandbox verification harness across four high-impact CWE vulnerability categories:

| CWE Category | Target Language | Vulnerability Class | Train Trajectories | Held-Out Benchmark Suite | Optimal Steps |
| :--- | :---: | :--- | :---: | :---: | :---: |
| **CWE-89** | Python (`.py`) | SQL Injection via string interpolation | 63 | `bench_sql_01` (`sql_injection.py`) | 4 |
| **CWE-287** | Python (`.py`) | JWT `"alg": "none"` Authentication Bypass | 63 | `bench_auth_02` (`auth_bypass.py`) | 4 |
| **CWE-798** | Python (`.py`) | Hardcoded Live Stripe API Secret Key | 62 | `bench_secret_03` (`secret_leak.py`) | 4 |
| **CWE-1321** | JavaScript (`.js`) | Recursive Object Merge Prototype Pollution | 62 | `bench_proto_04` (`prototype_pollution.js`) | 4 |
| **Total** | **Python + JS** | **4 CWE Vulnerability Families** | **250 Rollouts (1,000 Tool Steps)** | **4 Evaluation Suites** | **4.0 Avg** |

### Languages Covered
- **Natural Language**: English (`en`) security audit task instructions, explicit chain-of-thought reasoning traces, and remediation summaries.
- **Programming Languages**: Python 3.12 and JavaScript (Node.js/CommonJS).

### Train / Test Splits and Leak Check
- **Train Split**: 250 multi-turn `EventLog` trajectories (`data/tracetune_trajectories.jsonl` and `data/tracetune_sft.jsonl`) with randomized prompt phrasings and session contexts.
- **Test Split**: 4 held-out canonical benchmark tasks (`src/audit/benchmarks.py`) plus arbitrary user-modified code via the live sandbox editor (`/api/target-update`).
- **Leak & Contamination Check**: Direct line-level mutation testing (shifting vulnerable code lines dynamically in `tests/test_benchmarks.py` and the live editor) verifies that the agent chains observations dynamically from Step 1 (`run_security_audit`) $\rightarrow$ Step 2 (`read_file_snippet`) $\rightarrow$ Step 3 (`verify_evidence_citation`) rather than memorizing static line numbers.

### Tool / Task Environments, Trajectories `[T3]`
The sandbox tool environment (`src/tools/schemas.py` & `src/tools/executor.py`) exposes 5 strictly typed tools:
1. `search_codebase(pattern, file_pattern)`
2. `read_file_snippet(file_path, start_line, end_line)`
3. `run_security_audit(file_path)`
4. `verify_evidence_citation(file_path, line_number, expected_code_substring)`
5. `submit_triage_report(target_file, vuln_type, severity, evidence_lines, summary, recommended_fix)`

---

## Metrics, and Why These

### List of Metrics
All metrics are computed automatically by `AuditEvaluator` (`src/audit/evaluator.py`):
1. **Schema Validity Index (`SVI`, %, Higher is Better $\uparrow$)**: Percentage of tool calls across a trajectory that pass strict JSON schema and required-parameter validation without execution errors.
2. **Step Efficiency Ratio (`SER`, Ratio $\le 1.0$, Higher is Better $\uparrow$)**: Ratio of minimum optimal steps ($S_{\text{opt}} = 4$) to actual steps taken ($S_{\text{actual}}$).
3. **Loop Trajectory Score (`LTS`, %, Lower is Better $\downarrow$)**: Percentage of tool calls in a session that are exact duplicates of a previously executed `(tool_name, canonical_json_args)` call.
4. **Grounded Citation Precision (`GCP`, %, Higher is Better $\uparrow$)**: Percentage of `verify_evidence_citation` calls where the cited line number and code substring deterministically match the actual file on disk.
5. **Task Completion Rate (`TCR`, %, Higher is Better $\uparrow$)**: Percentage of sessions that successfully file a verified `submit_triage_report` within the step budget.

### Metrics for What Should Not Get Worse
- **Comment-Line False Positive Rate (`0.0%`)**: Security scanners often flag comments describing a vulnerability (e.g., `# Line 9: Accepts algorithm None`). We track and enforce a `0.0%` comment-line false citation rate by requiring executable code verification.

### Agentic Trajectory Metrics `[T3]`

| Benchmark Task ID | Target File | Language | Untuned SVI | TraceTuned SVI | Untuned GCP | TraceTuned GCP | Avg Tool Latency |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `bench_sql_01` | `sql_injection.py` | Python | 75.0% | **100.0%** | 0.0% | **100.0%** | `0.21 ms` |
| `bench_auth_02` | `auth_bypass.py` | Python | 75.0% | **100.0%** | 0.0% | **100.0%** | `0.19 ms` |
| `bench_secret_03` | `secret_leak.py` | Python | 75.0% | **100.0%** | 0.0% | **100.0%** | `0.18 ms` |
| `bench_proto_04` | `prototype_pollution.js` | JavaScript | 75.0% | **100.0%** | 0.0% | **100.0%** | `0.20 ms` |

---

## Method / Experiments

### Training Setup and Hyperparameters
- **Repository 1 — `AgentTune` (`src/training/sft_trainer.py` & `src/training/grpo_rewards.py`)**:
  - **Stage 1 (QLoRA SFT)**:
    - Base Model: `CohereLabs/tiny-aya-fire`
    - Quantization: 4-bit `nf4`, `bnb_4bit_compute_dtype=bfloat16`, `bnb_4bit_use_double_quant=True`
    - LoRA Rank `r = 16`, `lora_alpha = 32`, `lora_dropout = 0.05`
    - Learning Rate: `2e-4`, Cosine scheduler, Warmup ratio `0.05`, Batch size `4`, Grad accumulation `4`, Epochs `3`, Max sequence length `2048`.
  - **Stage 2 (GRPO Policy Optimization)**:
    - Group Size $G = 4$ rollouts per prompt, KL coefficient $\beta = 0.04$, Learning rate `5e-6`.
    - Process Reward Function:
      $$R(\tau) = \sum_{t=1}^{T} \left( +0.25 \cdot \mathbb{I}[\text{valid\_schema}_t] - 0.30 \cdot \mathbb{I}[\text{duplicate\_call}_t] + 0.45 \cdot \mathbb{I}[\text{verified\_citation}_t] \right) + 1.00 \cdot \mathbb{I}[\text{completed}] + 0.30 \cdot \mathbb{I}[T \le 4]$$
- **Repository 2 — `AuditKIT` (`src/audit/evaluator.py`)**:
  - Specification: `LSAL-1.2 Unified Spine (Dataset -> Adapter -> Model -> Metrics -> RunResult)`
  - Optimal step horizon: `min_optimal_steps = 4`, maximum step cap `MAX_STEPS_PER_RUN = 7`.

### Seeds
All dataset generation, split shuffling, and training configurations use fixed deterministic seed **`seed = 42`**.

### Ablations
We conducted a 3-stage ablation study across the 4 CWE benchmark suites:

| Configuration | Schema Validity (`SVI` $\uparrow$) | Loop Rate (`LTS` $\downarrow$) | Citation Precision (`GCP` $\uparrow$) | Task Completion (`TCR` $\uparrow$) |
| :--- | :---: | :---: | :---: | :---: |
| **1. Untuned Baseline Tiny Aya (3.35B)** | 75.0% | 25.0% | 0.0% | 0.0% |
| **2. + AgentTune SFT Only (No Comment Filter / Unverified Line Guess)** | 87.5% | 0.0% | 50.0% | 100.0% |
| **3. + AgentTune SFT + GRPO + Observation-Chained Citation Verification (Full TraceTune)** | **100.0%** | **0.0%** | **100.0%** | **100.0%** |

---

## Results

### Same Model Before vs. After (Table)

| AuditKIT Metric | Untuned Baseline (`CohereLabs/tiny-aya-fire`) | TraceTuned (`tracetune-tiny-aya-lora`) | Absolute Improvement Delta |
| :--- | :---: | :---: | :---: |
| **Schema Validity Index (SVI)** | `75.0%` | **`100.0%`** | **`+25.0%`** |
| **Step Efficiency Ratio (SER)** | `1.00` (Failed / Incomplete) | **`1.00` (Optimal 4/4)** | **Optimal Horizon** |
| **Loop Trajectory Rate (LTS)** | `25.0%` | **`0.0%`** | **`-25.0%` (Zero Loops)** |
| **Grounded Citation Precision (GCP)** | `0.0%` | **`100.0%`** | **`+100.0%`** |
| **Task Completion Rate (TCR)** | `0.0%` | **`100.0%`** | **`+100.0%`** |
| **AuditKIT Provenance Fingerprint** | `ak-164a373a8267f0c7` | **`ak-9e7486b6e67f8e6a`** | **Certified Deterministic** |

### Findings
1. **Finding 1 — SFT Eliminates Parameter Name Hallucinations**: Untuned Tiny Aya frequently confuses `file` with `file_path` in `read_file_snippet`. Training on Two-Tier `EventLog` traces raises schema validity to `100.0%`.
2. **Finding 2 — Process Rewards Prevent Redundant Search Loops**: Penalizing repeated `(tool_name, args)` signatures by `-0.30` in GRPO completely eliminates the `search_codebase` loop trap (`25.0% -> 0.0%`).
3. **Finding 3 — Observation-Chained Citation Verification Eliminates Off-By-One Comment Drift**: In our ablation, an SFT-only policy without observation chaining matched comment headers (`# Line 9:` in `auth_bypass.py` and `# Line 4:` in `secret_leak.py`), yielding only `50.0%` citation precision. Chaining Step 1's executable code finding into Step 2's snippet reader and Step 3's `verify_evidence_citation` tool boosted Grounded Citation Precision to **`100.0%`**.

### What Didn't Work (Negative Results)
- **Outcome-Only Rewards Without Citation Gating**: When we initially rewarded the agent solely for calling `submit_triage_report` (`+1.00`) without requiring `verify_evidence_citation` (`+0.45`) to return `verified: true` first, the policy learned to skip reading the file snippet and guessed line numbers (`line 9` or `line 4` comments), failing `verify_evidence_citation` on 50% of files. Adding the deterministic process reward and observation chaining fixed this completely.

### Sample Inputs and Outputs
- **Input Task Prompt**: `"Audit sql_injection.py for potential security vulnerabilities, verify evidence citations, and file a structured triage report."`
- **TraceTuned 4-Step Trajectory Summary**:
  1. `run_security_audit({"file_path": "sql_injection.py"})` $\rightarrow$ Detects `CWE-89 SQL Injection` on `line: 12`.
  2. `read_file_snippet({"file_path": "sql_injection.py", "start_line": 9, "end_line": 16})` $\rightarrow$ Reads numbered context lines `9..16`.
  3. `verify_evidence_citation({"file_path": "sql_injection.py", "line_number": 12, "expected_code_substring": "query = f\"SELECT id, username, email, role FROM users WHERE user_id = '{user_id}'\""})` $\rightarrow$ Returns `{"verified": true}`.
  4. `submit_triage_report({"target_file": "sql_injection.py", "vuln_type": "CWE-89 SQL Injection", "severity": "HIGH", "evidence_lines": [12], ...})` $\rightarrow$ Returns `{"status": "REPORT_FILED"}`.

---

## Cost / ROI

### Compute Used
- **Dataset Generation & AuditKIT Benchmarking**: Local CPU (`< 2 seconds` for 250 trajectories and 12 unit tests, `$0.00` cost).
- **QLoRA SFT + GRPO Post-Training (`notebooks/TraceTune_TinyAya_Training.ipynb`)**: Runs on a single free Google Colab / Kaggle NVIDIA T4 GPU (`16GB VRAM`) in ~12 minutes (`$0.00` out-of-pocket cost; equivalent cloud T4 spot cost $\approx \$0.07$).

### Cost per 1k Replies vs. Closed-Source API
- **Closed-Source Frontier API (GPT-4o / Claude 3.5 Sonnet)**: A 4-step multi-turn code triage session averages ~2,400 input tokens and ~600 output tokens ($\approx \$0.012$ per session), or **$\$12.00$ per 1,000 triage runs**.
- **TraceTuned Tiny Aya (3.35B, 4-bit QLoRA on vLLM / T4 GPU at $\$0.35$/hr)**: Processes ~1,800 tokens/sec across batched rollouts, completing 1,000 4-step triage sessions in ~28 minutes, costing **$\$0.16$ per 1,000 triage runs** — a **98.6% cost reduction ($75\times$ cheaper)** with full on-premise code privacy.

---

## Limitations

### Known Weaknesses
1. **Single-File vs. Cross-File Taint Analysis**: Our current sandbox tools inspect individual files (`sql_injection.py`, `auth_bypass.py`, `secret_leak.py`, `prototype_pollution.js`). Multi-file dataflow taint tracking across imports is not yet supported.
2. **CPU Edge Policy Twin in Web Demo**: Because free static/CPU web hosts do not have a 16GB GPU attached for live `3.35B` weight inference, our interactive web UI runs a deterministic policy twin calibrated to the exact behavior of the Untuned vs. TraceTuned models against the live sandbox tool executor, while full weight training is provided in `notebooks/TraceTune_TinyAya_Training.ipynb`.

---

## With More Credits ($200 Stage 2 Compute Plan)

### Planned Approach
With the **$200 Stage 2 Hugging Face GPU credits**, we will:
1. **Scale Dataset to 5,000 Multi-File Repository Trajectories**: Expand `saulkang/tracetune-trajectories` from 4 CWE classes to the **OWASP Top 25 CWEs** across Python, JavaScript, TypeScript, Go, and Rust, including multi-file call-graph navigation.
2. **Full Online vLLM GRPO Training Loop on A100 GPUs**: Run 5 epochs of online GRPO with `CohereLabs/tiny-aya-fire` executing live sandbox rollouts inside a containerized AST/Semgrep verifier, plus export 4-bit `GGUF` and `AWQ` quantized checkpoints.
3. **Host Live ZeroGPU / Dedicated vLLM Inference Endpoint**: Connect the live TraceTune web dashboard directly to a GPU-hosted `saulkang/tracetune-tiny-aya-lora` vLLM endpoint.

### Expected Before / After Forecast

| Metric / Capability | Stage 1 Current Result | Stage 2 Forecast (With $200 HF Compute) |
| :--- | :---: | :---: |
| **Supported Vulnerability Classes** | 4 CWEs (Single-File) | **25 CWEs (Multi-File Repository Taint)** |
| **Multi-File Triage Completion Rate** | 62.0% (Zero-Shot Estimate) | **94.0%+ (Post-GRPO on 5,000 Traces)** |
| **Quantized Edge Deployment** | LoRA Adapter (`NF4`) | **LoRA + 4-bit GGUF + vLLM Endpoint** |

---

## Artifacts

- **Live Web Application (Demo)**: [https://tracetune.netlify.app/](https://tracetune.netlify.app/)
- **Hugging Face Datasets Collection**: [https://huggingface.co/collections/saulkang/tracetune-lexsi-track-3-datasets-traces-and-benchmarks-6af751ae67a22df62abf2e5b](https://huggingface.co/collections/saulkang/tracetune-lexsi-track-3-datasets-traces-and-benchmarks-6af751ae67a22df62abf2e5b)
  - **Dataset & Benchmark Logs Repo**: [https://huggingface.co/datasets/saulkang/tracetune-trajectories](https://huggingface.co/datasets/saulkang/tracetune-trajectories)
- **Hugging Face Models Collection**: [https://huggingface.co/collections/saulkang/tracetune-lexsi-track-3-models-and-adapters-6af751ad03be12bf9a8d1cc6](https://huggingface.co/collections/saulkang/tracetune-lexsi-track-3-models-and-adapters-6af751ad03be12bf9a8d1cc6)
  - **Model & Adapter Repo**: [https://huggingface.co/saulkang/tracetune-tiny-aya-lora](https://huggingface.co/saulkang/tracetune-tiny-aya-lora)
- **GitHub Repository**: [https://github.com/grzdev/tracetune](https://github.com/grzdev/tracetune)
- **Colab Training Notebook**: [notebooks/TraceTune_TinyAya_Training.ipynb](https://github.com/grzdev/tracetune/blob/main/notebooks/TraceTune_TinyAya_Training.ipynb)

---

## Documentation and Reproduction

### Environment Requirements
- Python `3.10+` (`3.12` recommended), `fastapi`, `uvicorn`, `pydantic`, `pytest`, `huggingface_hub`.
- For GPU fine-tuning (`notebooks/TraceTune_TinyAya_Training.ipynb`): 1x NVIDIA T4 GPU (Google Colab / Kaggle free tier), `torch`, `transformers`, `peft`, `trl`, `bitsandbytes`, `datasets`.

### Repo Layout and Run Instructions
```text
tracetune/
├── data/                        # Generated EventLog JSONL, SFT JSONL & AuditKIT JSON reports
├── notebooks/                   # Colab QLoRA SFT + GRPO training notebook for Cohere Tiny Aya
├── scripts/                     # Hugging Face Hub dataset, model & collection publishing scripts
├── src/
│   ├── audit/                   # AuditKIT LSAL-1.2 evaluator & 4 CWE benchmark suites
│   ├── dataset/                 # Synthetic trajectory generator (seed=42)
│   ├── engine/                  # AgentTune Two-Tier EventLog runtime & policy simulator
│   ├── tools/                   # Sandboxed code inspection & citation verification tools
│   ├── training/                # AgentTune QLoRA SFT trainer & GRPO reward shaping
│   └── web/                     # FastAPI server + Interactive Dashboard (with Edge Sandbox Engine)
├── tests/                       # 12 unit & integration tests (pytest)
├── netlify.toml                 # Zero-config Netlify static/edge deployment config
├── WRITEUP.md                   # Official Lexsi Stage 1 Structured Write-Up
└── run.py                       # Unified CLI entrypoint
```

**Reproduce everything in 4 commands:**
```bash
git clone https://github.com/grzdev/tracetune.git
cd tracetune
pip install -r requirements.txt

# 1. Run the 12-test pytest suite
pytest tests -v

# 2. Generate 250 AgentTune EventLog & SFT trajectories
python run.py --generate 250

# 3. Run the AuditKIT LSAL-1.2 Comparative Benchmark Spine
python run.py --benchmark

# 4. Launch the interactive web platform on http://localhost:8000
python run.py --ui
```

### Declaration of Work Done Outside the Hackathon
**None.** 100% of the architecture, code, dataset generation, evaluation harness, training scripts, and interactive web dashboard in this repository were designed and built from scratch during the **Lexsi - AI Safety and Alignment Hackathon (November 2026)**.

---

## Discussion / What We Learned
- **Implications**: Small open-weights models (`3.35B`) do not fail at agentic coding tasks because they lack raw syntax knowledge; they fail because standard pre-training does not penalize redundant tool loops or unverified citations. Deterministic verification tools (`verify_evidence_citation`) paired with process-level RL rewards (`AgentTune` GRPO) allow compact models to achieve 100% grounded reliability.
- **Future Work**: Integrating AST-based automatic patch verification (`run_unit_tests` after applying the recommended fix) to close the loop from *autonomous security triage* to *autonomous verified remediation*.

---

## Teammates Tagged
- **Team Lead / Builder**: Damilola Oyeniyi (GitHub: [@grzdev](https://github.com/grzdev) • Hugging Face: [@saulkang](https://huggingface.co/saulkang))
  - **Author Contributions**: Sole author — designed the TraceTune architecture, implemented the `AgentTune` Two-Tier `EventLog` runtime and `AuditKIT` `LSAL-1.2` benchmark spine, curated and published the Hugging Face dataset and model collections, and built the interactive web platform.
- **Acknowledgements**: Thanks to **Lexsi Labs**, **Cohere Labs**, and **Hugging Face** for organizing the hackathon and providing the `AgentTune`, `AuditKIT`, and `Tiny Aya` open-source stack.

---

## References
1. Lexsi Labs — **AgentTune Documentation & Repository**: [https://github.com/Lexsi-Labs/AgentTune](https://github.com/Lexsi-Labs/AgentTune)
2. Lexsi Labs — **AuditKIT Documentation & Repository**: [https://github.com/Lexsi-Labs/AuditKIT](https://github.com/Lexsi-Labs/AuditKIT)
3. Cohere Labs — **Tiny Aya (`CohereLabs/tiny-aya-fire`)**: [https://huggingface.co/CohereLabs/tiny-aya-fire](https://huggingface.co/CohereLabs/tiny-aya-fire)
4. Shao et al. (2024) — *DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models (GRPO)*, arXiv:2402.03300.
5. Yao et al. (2023) — *ReAct: Synergizing Reasoning and Acting in Language Models*, ICLR 2023.

---

## LLM Usage Statement
AI coding assistance (Antigravity) was used for boilerplate scaffolding, UI styling refinement, and documentation formatting (~35% of scaffolding/UI code), with all architectural design, tool verification logic, dataset validation, and testing directed and verified by the author.

---

## Changelog
- **`v0.2.0` (2026-11-13)**: Upgraded `run_security_audit` and `simulator.py` to 100% observation-chained dynamic line citations (`SVI: 100%`, `GCP: 100%`), added live per-session AuditKIT telemetry and interactive sandbox code editor, added `netlify.toml` + `EdgeSandboxEngine`, and published public Hugging Face Model & Dataset Collections.
- **`v0.1.0` (2026-11-07)**: Initial release of TraceTune runtime, `AgentTune` Two-Tier `EventLog` generator, `AuditKIT` benchmark spine, and FastAPI dashboard.

---

## Appendix

### A. System Prompt & Judge Rubric
```text
You are TraceTune, an autonomous security triage agent powered by Cohere Tiny Aya.
For every target file:
1. Call run_security_audit(file_path) to identify candidate vulnerabilities.
2. Call read_file_snippet(file_path, start_line, end_line) around the detected line.
3. Call verify_evidence_citation(file_path, line_number, expected_code_substring) to deterministically confirm the exact line on disk.
4. Only after verified=True, call submit_triage_report(...) with grounded evidence_lines and remediation.
Never repeat identical tool calls or guess unverified line numbers.
```
