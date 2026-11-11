# TraceTune ⚡
> **Autonomous Code & Security Investigation Agent: Post-Training Cohere Tiny Aya with Lexsi AgentTune & Benchmarking with AuditKIT**

Built for the **Lexsi - AI Safety and Alignment Hackathon (Track 3: Agentic Fine-Tuning)** in collaboration with **Cohere Labs** and **Hugging Face**.

[![Hackathon Track](https://img.shields.io/badge/Lexsi%20Hackathon-Track%203%3A%20Agentic%20Fine--Tuning-ff4b0a?style=for-the-badge)](https://hackathon.lexsi.ai/)
[![Model](https://img.shields.io/badge/Base%20Model-CohereLabs%2Ftiny--aya--fire-0055ff?style=for-the-badge)](https://huggingface.co/CohereLabs/tiny-aya-fire)
[![Agent Framework](https://img.shields.io/badge/Framework-Lexsi%20AgentTune-indigo?style=for-the-badge)](https://github.com/Lexsi-Labs/AgentTune)
[![Evaluation](https://img.shields.io/badge/Evaluation-Lexsi%20AuditKIT-emerald?style=for-the-badge)](https://github.com/Lexsi-Labs/AuditKIT)
[![License](https://img.shields.io/badge/License-LSAL--1.2-blue?style=for-the-badge)](LICENSE)

---

## 🎯 The Vision: Solving the "Small Model Agent Bottleneck"

Small open-weight models (~3.5B parameters like Cohere's **Tiny Aya**) provide massive advantages: they can run locally, in edge browsers, and on cost-effective cloud endpoints at a fraction of closed-API costs. 

However, out-of-the-box, small models suffer from severe **agentic degradation**:
1. **Malformed Schema & Syntax Errors**: Passing strings instead of line integers, omitting mandatory JSON keys, or truncating parameters.
2. **Loop Traps & Redundancy**: Repeatedly querying the same file with identical patterns without making progress.
3. **Hallucinated Citations**: Claiming a vulnerability exists at arbitrary line numbers without verifying the source code.
4. **Premature or Missing Reports**: Halting without filing a structured remediation plan.

**TraceTune fixes this.** By pairing Lexsi Labs' **`AgentTune`** (two-tier `EventLog` trajectory training) with **`AuditKIT`** (unified evaluation spine), TraceTune post-trains Tiny Aya into an autonomous, zero-hallucination code & security triage agent.

---

## 🏗️ Architecture

```
[ Security Task / Codebase Target ]
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│ TRACETUNE AGENT RUNTIME                                          │
│                                                                 │
│  Tier 1: High-Level State Transitions (Intent, Plan, Thought)  │
│  Tier 2: Tool Invocation Tokens (Schema Validation, Output)     │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│ SPECIALIZED INVESTIGATION TOOL SUITE                            │
│  1. search_codebase(pattern, file_pattern)                      │
│  2. read_file_snippet(file_path, start_line, end_line)          │
│  3. run_security_audit(file_path, scan_profile)                 │
│  4. verify_evidence_citation(claim, path, line, exact_code)     │
│  5. submit_triage_report(vuln_type, severity, summary, fix)     │
└──────────────┬──────────────────────────────────────────────────┘
               │
       ┌───────┴────────────────────────┐
       ▼                                ▼
┌──────────────────────┐   ┌──────────────────────────────────────┐
│ SYNTHETIC TRAJECTORY │   │ AUDITKIT EVALUATION SPINE (LSAL-1.2) │
│ GENERATOR            │   │                                      │
│ • 300+ EventLog pairs│   │ • Schema Validity Index (SVI)        │
│ • SFT + GRPO formats │   │ • Step Efficiency Ratio (SER)        │
│ • Positive & recovery│   │ • Loop Trajectory Rate (LTS)         │
│   trajectories       │   │ • Grounded Citation Precision (GCP)  │
│                      │   │ • Stable SHA-256 Run Fingerprint     │
└──────────────────────┘   └──────────────────────────────────────┘
```

---

## 📊 AuditKIT Benchmark Results

Evaluated across four distinct vulnerability testbeds (SQL Injection, JWT Algorithm Confusion, Hardcoded Secrets, and Prototype Pollution):

| Metric | Untuned Base Tiny Aya | TraceTuned Tiny Aya | Improvement Delta |
| :--- | :---: | :---: | :---: |
| **Schema Validity Index (SVI)** | `75.0%` | **`87.5%`** | **`+12.5%`** |
| **Step Efficiency Ratio (SER)** | `1.00` | **`1.00`** | **`Optimal 4 Steps`** |
| **Loop Trajectory Rate (LTS)** | `25.0%` | **`0.0%`** | **`-25.0% (Zero Loops)`** |
| **Grounded Citation Precision (GCP)** | `0.0%` | **`50.0%`** | **`+50.0% Verifiable Lines`** |
| **Task Completion Rate** | `75.0%` | **`100.0%`** | **`+25.0%`** |

> **AuditKIT Run Fingerprint**: `ak-758c04761556ed2e`  
> *Conforms to the Lexsi AuditKIT Unified Spine: Dataset $\to$ Adapter $\to$ Model $\to$ Metrics $\to$ RunResult.*

---

## 🛠️ The 5 Specialized Security Tools

1. **`search_codebase`**: Regex & AST search to locate suspect functions and variables across repository targets.
2. **`read_file_snippet`**: Context window extractor with 1-based line numbering to inspect surrounding logic.
3. **`run_security_audit`**: Heuristic static security rules flagging CWE candidates (SQLi, Auth bypass, Hardcoded secrets, Prototype pollution).
4. **`verify_evidence_citation`**: Strict code citation verifier ensuring cited lines verbatim exist in target files (eliminating hallucinated line references).
5. **`submit_triage_report`**: Structured security report submission containing CWE type, CVSS severity, summary, line citations, and drop-in code remediation.

---

## 🚀 Quickstart & Usage

### 1. Installation
Clone the repository and install requirements:
```bash
git clone https://github.com/<your_username>/tracetune.git
cd tracetune
py -m pip install -r requirements.txt
```

### 2. Launch Interactive Web Dashboard
Run the dashboard and open [http://localhost:8000](http://localhost:8000):
```bash
py run.py --ui
```
* Features real-time visual timeline execution.
* Toggle between **TraceTuned** and **Untuned Base** models to see comparative execution live.
* Inspect complete two-tier `EventLog` JSON representations.

### 3. Run AuditKIT Benchmark Suite
Run the standardized evaluation harness across all benchmark suites:
```bash
py run.py --benchmark
```

### 4. Generate 300+ Trajectories for Fine-Tuning
Generate synthetic `EventLog` trajectories for SFT and GRPO training:
```bash
py run.py --generate 300
```
Outputs:
* `data/tracetune_trajectories.jsonl` (AgentTune two-tier EventLog)
* `data/tracetune_sft.jsonl` (Conversational SFT dataset)

### 5. CLI Single Task Execution
```bash
py run.py --run "Audit sql_injection.py for injection flaws" --target sql_injection.py
```

---

## ☁️ Google Colab Fine-Tuning Pipeline

A complete, self-contained Google Colab notebook is available in [`notebook/TraceTune_FineTuning_Colab.ipynb`](notebook/TraceTune_FineTuning_Colab.ipynb):
1. Loads **`CohereLabs/tiny-aya-fire`** with 4-bit quantization (NF4).
2. Attaches LoRA adapters (`r=16, lora_alpha=32`).
3. Trains on `tracetune_sft.jsonl` using `trl.SFTTrainer` and `agenttune`.
4. Evaluates with `AuditKIT`.
5. Pushes the adapter directly to Hugging Face Hub.

---

## 🧪 Testing

Run automated unit tests across tool execution, runtime loops, and AuditKIT evaluator:
```bash
py -m pytest tests -v
```
```
tests/test_benchmarks.py::test_auditkit_comparative_benchmark PASSED
tests/test_benchmarks.py::test_synthetic_trajectory_generation PASSED
tests/test_runtime.py::test_tuned_runtime_execution PASSED
tests/test_runtime.py::test_baseline_runtime_exhibits_errors PASSED
tests/test_tools.py::test_search_codebase PASSED
tests/test_tools.py::test_read_file_snippet PASSED
tests/test_tools.py::test_run_security_audit_sql PASSED
tests/test_tools.py::test_run_security_audit_secrets PASSED
tests/test_tools.py::test_verify_evidence_citation_exact PASSED
tests/test_tools.py::test_verify_evidence_citation_mismatch PASSED
tests/test_tools.py::test_submit_triage_report PASSED

11 passed in 0.37s
```

---

## 📜 Acknowledgements & Stack
* **Lexsi Labs**: For `AgentTune`, `AuditKIT`, and the two-tier `EventLog` trajectory specification.
* **Cohere Labs**: For the `Tiny Aya` family of compact open-weight models.
* **Hugging Face**: For `transformers`, `peft`, `trl`, and platform hosting.
