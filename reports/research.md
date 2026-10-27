# Research: a local AI-change evidence pack for pull requests

Date: 2026-10-28 (IST)  
Decision: build **Proofline**, a local-first CLI that turns a Git diff plus test output into a concise, reviewable evidence pack for AI-assisted changes.

## The problem

AI makes it cheap to produce a large change, but validation and review have become the bottleneck. A reviewer must reconstruct intent, identify risky changed paths, discover what was actually executed, and determine whether the proposed change has meaningful tests. That is particularly painful for solo developers and small teams using coding agents: the code might look plausible while its verification trail is missing.

This is not another opaque “AI reviewer.” The useful first version is deterministic and local: inspect `git diff`, classify changed files, run a declared test command, capture its output and exit code, and produce a Markdown report/checklist that a human can inspect. An optional local model can later explain the evidence, but correctness does not depend on an API key.

## Evidence of demand and timing

- The [Stack Overflow 2026 Developer Survey](https://survey.stackoverflow.co/2026/ai/data/ai-impact) reports that developers find AI useful for implementation (75%), debugging (73%), documentation (66%), and review (64%). AI is clearly in the daily development workflow; the opportunity is the validation gap around it.
- Stack Overflow’s [2025 AI survey](https://survey.stackoverflow.co/2025/ai) found that 46% distrust AI accuracy, while 66% cite outputs that are “almost right” as a frustration and 45% say debugging AI-generated code takes more time. The needed outcome is evidence, not more generated code.
- [Atlassian’s 2026 Developer Experience report](https://www.atlassian.com/teams/software-development/state-of-developer-experience-2026) surveyed 1,500+ practitioners and reports that 75% of developers now have more responsibility for validating AI-generated quality and safety.
- [Temporal’s 2026 State of Development](https://temporal.io/reports/state-of-development-2026) identifies tracking agent state as the most common blocker to using more AI agents (35.7%). A portable on-disk evidence artifact is directly compatible with multi-agent/local workflows.
- [Black Duck’s June 2026 survey release](https://news.blackduck.com/2026-06-09-AI-Coding-Hits-97-Enterprise-Adoption-New-Black-Duck-Study-Shows-Governance-Is-the-ROI-Multiplier?cmp=pr-sig) describes bottlenecks in manual review (52%), security testing (51%), and rework (48%). The project should address the handoff between generation and trusted review.

These are survey/vendor sources, so they demonstrate direction and stated pain rather than a precise total market. The first project should validate demand by collecting GitHub issues and user feedback after release.

## Target user and job-to-be-done

**Primary user:** a solo developer or small engineering team using Codex/Claude/Copilot to create a feature or fix in a Git repository.

**Job:** “Before I ask someone to review or merge an AI-assisted change, give me a compact, reproducible record of what changed, what looks risky, what tests ran, and what I must still inspect.”

## Proposed MVP

`proofline check [--test <command>]`:

1. Read the working-tree or staged Git diff locally.
2. Summarize changed files, additions/deletions, renames, and high-risk categories (auth, configuration, CI, dependencies, migrations, generated/minified files).
3. Detect likely test files modified or absent.
4. Optionally run exactly the user-provided test command—never invent a destructive command—and capture stdout/stderr and exit status.
5. Write `proofline-report.md` and `proofline-report.json`, including a human review checklist and a reproducibility block.

## Why this is feasible without paid services

Python standard library plus the installed `git` executable are sufficient for the core. No model, cloud service, or API key is required. The runner can use `subprocess` with a clear timeout and redact obvious environment values from captured output. Optional local-model commentary can be explicitly out of scope for v1.

## Alternatives considered

| Alternative | Why not the first build |
|---|---|
| Full autonomous AI code reviewer | Requires model/provider choice, introduces trust/privacy cost, and duplicates crowded tools. |
| Flaky-test detector | Valuable but reliable detection needs repeated CI history and is too narrow for a first local project. |
| Prompt/session memory tool | Useful, but agent state is already represented by this factory’s files; it is less directly testable as an independent repo. |
| Dependency vulnerability scanner | Existing mature tools cover this well; the differentiated gap is linking change evidence and test evidence. |

## Acceptance criteria for planning

- Works offline after Git/Python are installed; no API key.
- A fixture Git repository demonstrates file/risk classification and Markdown/JSON output.
- A passing and failing user-provided test command are both recorded with correct status.
- No test command is run unless explicitly supplied.
- Test suite covers parsing/classification and report generation.
- README makes limitations clear: it does not prove correctness or replace human review/security scanning.

## Risks

- Risk heuristics can be noisy; label them as prompts for human review, not findings.
- Capturing arbitrary test output can expose secrets; redact common `KEY=`, `TOKEN=`, and `PASSWORD=` patterns and document that users should review artifacts before publishing.
- The name may already exist; verify package/repository naming before publishing.
