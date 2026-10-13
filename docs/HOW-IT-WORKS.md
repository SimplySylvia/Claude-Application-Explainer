# How it works

This page describes how Claude runs the application-explainer skill. For installing and using it, see the
[README](../README.md).

## Workflow

Claude runs the skill as a checklist of nine phases. It does the writing itself and fans out to subagents for
research, review, and glossary drafting. Hexagons are points where it stops and waits for your approval.

```mermaid
flowchart TD
    ask(["You ask for an explainer or onboarding guide"]) --> scope

    scope{{"0 · Scope<br/>app, audience, guide location, screenshots?"}} --> scaffold
    scaffold["1 · Scaffold<br/>new_guide.py creates the guide folder and its git repo"] --> discover

    subgraph discover ["2 · Discover"]
        direction LR
        r1["repo-researcher<br/>routes and UI"]
        r2["repo-researcher<br/>API and data"]
        r3["repo-researcher<br/>infra and CI"]
        r1 ~~~ r2 ~~~ r3
    end
    discover --> outline{{"Section outline approved"}}

    outline --> write
    subgraph write ["3 · Write"]
        direction LR
        w["sections/*.html<br/>diagrams.py"] --> b["build.py"]
        b -- "warnings" --> w
    end

    write --> review
    subgraph review ["4 · Review"]
        direction LR
        sr["structure-reviewer"]
        sv["section-verifier<br/>one per section"]
        sr ~~~ sv
    end
    review --> apply["Spot-check findings, apply fixes, rebuild"]

    apply --> shots{"5 · Screenshots?"}
    shots -- "yes" --> env{{"Environment and synthetic data confirmed"}}
    env --> capture["Capture, scrub, add to shots.py"]
    capture --> glossary
    shots -- "skip" --> glossary

    subgraph glossary ["6 · Glossary"]
        direction LR
        ex["extract_text.py"] --> gd["glossary-drafter<br/>one per area"] --> mg["merge_glossary.py"]
    end

    glossary --> qa["7 · QA<br/>qa_check.py on both builds"]
    qa -- "fails or TODOs left" --> fix["Fix"] --> qa
    qa -- "PASS" --> share{{"8 · Share internally<br/>method recorded in the guide README"}}

    classDef gate fill:#fff4e5,stroke:#d97706,color:#7c2d12
    classDef agent fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    class scope,outline,env,share gate
    class r1,r2,r3,sr,sv,gd agent
```

After every phase, Claude builds the guide, commits it to the guide's own git repo, and gives you a short update.

## Who does what

| Worker | Phase | Can | Job |
|---|---|---|---|
| **Claude** (main session) | All | Read the app repo; write only in the guide folder | Runs the checklist, writes sections and diagrams, spot-checks agent findings, builds, runs QA |
| [`repo-researcher`](../agents/repo-researcher.md) | 2 · Discover | Read only | Maps one area of the repo (routes, API, data, infra, CI, tests) and returns findings with paths |
| [`structure-reviewer`](../agents/structure-reviewer.md) | 4 · Review | Read only | Reviews order, gaps, duplication, and cross-links across the whole guide |
| [`section-verifier`](../agents/section-verifier.md) | 4 · Review | Read only | Fact-checks each claim in its sections against the repo and reports wrong, stale, or missing items |
| [`glossary-drafter`](../agents/glossary-drafter.md) | 6 · Glossary | Read; write one draft file in the guide's `qa/` folder | Drafts glossary rows for one area, each with a definition and repo paths |

Each phase is described in detail in
[`references/workflow.md`](../skills/application-explainer/references/workflow.md), and the agent prompts are in
[`references/agent-prompts.md`](../skills/application-explainer/references/agent-prompts.md).
