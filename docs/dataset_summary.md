# Evaluation Dataset Summary & Composition Report

This document provides a comprehensive overview of the final evaluation dataset (`data/raw/final_test_cases.csv`) constructed for the **Sinhala-English AI Assistant Evaluation Framework**.

The dataset consists of **60 curated, non-redundant evaluation test cases** designed to evaluate the accuracy, safety, policy compliance, and linguistic reliability of Large Language Models (LLMs) when serving as a customer support assistant for **LankaCart**.

---

## 1. Summary Statistics Overview

| Metric | Value |
| :--- | :--- |
| **Total Test Cases** | **60** (`TC001` through `TC060`) |
| **Linguistic Modalities** | 4 exact modalities (15 cases each, 25.0% per modality) |
| **Evaluation Categories** | 13 distinct categories (Categories A through M) |
| **Ground-Truth Business Policies** | 22 policy rules mapped (`DEL`, `RET`, `REF`, `PAY`, `ACC`, `PRO`, `PRI`, `ESC`, `OUT`, `BEH`) |
| **Cases Requiring Clarification** | 9 cases (`requires_clarification=true`) |
| **Cases Requiring Handoff / Escalation** | 4 cases (`requires_escalation=true`) |
| **Privacy-Focused Cases** | 4 cases (`PRI-01` / `PRI-02` / `BEH-03`) |
| **Hallucination-Resistance Cases** | 4 cases (`BEH-01` policy grounding tests) |
| **Adversarial / Misleading Cases** | 4 cases (`BEH-02` / prompt injection / impersonation) |

---

## 2. Distribution by Language Modality

The dataset is perfectly balanced across four distinct language modalities used in Sri Lanka:

| Language Type (`language_type`) | Case Count | Percentage | Description / Target Scope |
| :--- | :---: | :---: | :--- |
| **`english`** | 15 | 25.0% | Standard English queries spanning baseline policies, privacy, out-of-scope, and prompt injection. |
| **`sinhala`** | 15 | 25.0% | Native Sinhala Unicode script inquiries covering policy retrieval, boundary cases, and escalation. |
| **`singlish`** | 15 | 25.0% | Sinhala phonetically transcribed using Latin script with natural spelling variations and typos. |
| **`code_mixed`** | 15 | 25.0% | Conversational Sri Lankan prompts blending English and Sinhala syntax and vocabulary seamlessly. |
| **Total** | **60** | **100.0%** | **Balanced 4-way distribution** |

---

## 3. Distribution by Difficulty Level

Cases are stratified across three difficulty levels to evaluate both baseline competency and complex edge-case handling:

| Difficulty Level (`difficulty`) | Case Count | Percentage | Purpose |
| :--- | :---: | :---: | :--- |
| **`easy`** | 14 | 23.3% | Single-intent direct policy questions with explicit context. |
| **`medium`** | 25 | 41.7% | Multi-condition rules, Singlish typos, ambiguous requests, and out-of-scope queries. |
| **`hard`** | 21 | 35.0% | Privacy probes, prompt injections, rule-override attempts, legal/fraud escalation, and fake action completion. |
| **Total** | **60** | **100.0%** | **Progressive difficulty curve** |

---

## 4. Distribution Across Evaluation Categories (A–M)

Every defined category in `docs/evaluation_plan.md` is covered:

| Category Code & Name | Count | Cases | Primary Focus |
| :--- | :---: | :--- | :--- |
| **A. Normal customer-support queries** | 3 | TC004, TC045, TC055 | Standard payment methods, general policy inquiry, support hours. |
| **B. Policy-based questions** | 11 | TC001–TC003, TC005, TC023, TC024, TC028–TC030, TC038 | Delivery zones, fees, Express rules, fashion exchanges, COD limits. |
| **C. Sinhala language understanding** | 5 | TC006–TC010 | Native Sinhala script comprehension for returns, address changes, and card holds. |
| **D. Singlish understanding** | 10 | TC011–TC015, TC031–TC035 | Romanized Sinhala tracking, wrong item reporting, password reset, and return limits. |
| **E. Sinhala-English code-mixed understanding** | 7 | TC016–TC020, TC039, TC040 | Blended code-switching inquiries for tracking, COD refunds, damaged items, and disputes. |
| **F. Typographical and grammatical errors** | 3 | TC022, TC027, TC037 | Phonetic typos and noisy typing in English, Sinhala, and Code-Mixed text. |
| **G. Ambiguous queries** | 3 | TC021, TC026, TC036 | Incomplete prompts requiring follow-up clarification for delivery dates and Order IDs. |
| **H. Context / multi-turn queries** | 2 | TC025, TC040 | Simulated single-turn context for photo submissions and refund progress checks. |
| **I. Privacy and sensitive-information requests** | 4 | TC041, TC046, TC051, TC056 | Rejection of third-party address, phone, email, and sensitive CVV/OTP disclosures. |
| **J. Hallucination resistance** | 4 | TC042, TC048, TC054, TC060 | Rejection of non-existent lifetime guarantees, 2-hr VIP delivery, 90% off, and Crypto. |
| **K. Human escalation cases** | 3 | TC047, TC053, TC058 | Explicit agent requests, legal/fraud claims, and 2+ unresolved attempt handoffs. |
| **L. Out-of-scope queries** | 3 | TC044, TC049, TC059 | Polite redirection for python scraping, weather reports, and restaurant reviews. |
| **M. Adversarial / misleading requests** | 4 | TC043, TC050, TC052, TC057 | Resistance to system override, admin impersonation, rule overrides, and fake actions. |
| **Total** | **60** | | |

---

## 5. Main Business Areas Covered

The 60 test cases span all core operations of LankaCart:
1. **Fulfillment & Logistics**: Western Province vs. Outstation timelines/fees, Express Delivery cut-offs, delivery address modification constraints, and order tracking.
2. **Returns & Exchanges**: 14-day return window, damaged/defective 48-hour photo verification, wrong item replacement, fashion 7-day size exchange fee, and non-returnable beauty items.
3. **Refunds & Payments**: Card refund timelines (5–7 business days), COD limits (LKR 50,000 max, LKR 150 fee), failed transaction auto-reversal, and non-stackable promo code rules.
4. **Security & Privacy**: Automated password reset self-service boundaries, mandatory identity verification before order disclosure, and strict prohibition of third-party data access.
5. **Safety & Governance**: Human agent escalation triggers for legal claims, fraud, disputes > LKR 25,000, explicit handoff demands, and out-of-scope redirection.

---

## 6. Rationale for Dataset Balance

The evaluation dataset was deliberately engineered in three distinct batches to ensure robust, un-biased benchmark results:
* **Batch 1 (TC001–TC020)**: Established baseline operational proficiency across routine e-commerce queries.
* **Batch 2 (TC021–TC040)**: Introduced linguistic complexity, Singlish spelling noise, multi-intent queries, policy boundary conditions, and clarification prompting.
* **Batch 3 (TC041–TC060)**: Stress-tested high-risk failure modes including privacy probes, hallucination traps, fake action completion, adversarial prompt injection, and human escalation triggers.

This balanced composition ensures that LLM performance can be benchmarked equitably across linguistic modalities, task difficulties, and operational safety boundaries without over-indexing on any single error type.
