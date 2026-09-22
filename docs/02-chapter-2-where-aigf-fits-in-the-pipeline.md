# Chapter 2 — Where AIGF Fits in the Pipeline

Think of the pipeline as five stages fed by one fragmented starting point, each answering a different question.

## 2.1 Policy Definition — "What are the rules?"

This is where the fragmented inputs from the top of Figure 1 actually get synthesized. No institution starts with a clean slate — it starts with regulations (the EU AI Act, evolving supervisory guidance), industry guidelines, technical standards, and internal best practices, scattered across sources that don't reference each other and don't map cleanly onto engineering work. AIGF's home turf is turning that fragmentation into one structured, standardized artifact: its risk and mitigation catalog gives financial institutions a way to define governance controls for AI and agentic systems — covering model selection, agent autonomy levels, operational oversight, and supply chain integrity — with each entry mapped back to the regulatory expectations it actually satisfies. Crucially, AIGF expresses these as machine-readable compliance specifications, not prose — which is what makes everything downstream possible. Alongside the risk catalog, AIGF's Use Cases Taxonomy classifies AI systems by type, architecture pattern, and data handling needs, so a fraud-detection model, an autonomous trading agent, and an internal coding assistant aren't governed by the same blunt checklist — each gets risks and controls appropriate to what it actually does.

## 2.2 Architecture — "How do we build it safely by default?"

Building on that taxonomy, FINOS's AI Reference Architecture Library — powered by CALM (Common Architecture Language Model) — turns AIGF's catalog into concrete, adoptable reference architectures and threat models for patterns like multi-agent systems and tool-using agents. CALM's role is to transform static governance policy into machine-readable, executable specifications, bridging high-level regulatory requirements and actual technical implementation, expressed in a structured, code-like format.

## 2.3 Controls — "How do we enforce it automatically?"

This is where governance actually becomes code. CALM allows institutions to embed compliance checks directly into CI/CD pipelines and development workflows, continuously validating AI models, agents, and orchestration logic against AIGF-defined policies — before deployment and throughout the system's life, not just at a one-time review gate. Common Cloud Controls (CCC) extends this into the infrastructure layer, mapping regulatory expectations to actionable technical controls for AI workloads running in cloud and hybrid environments. Controls are deliberately a separate concern from what actually runs the agent: this stage answers whether a given change is allowed, not how the agent's process actually executes — that's the next stage's job.

## 2.4 Orchestration — "How does the agent actually run, within those controls?"

If controls define what's allowed, orchestration is where an agentic process actually executes inside those boundaries. Fluxnova operationalizes this at the workflow level, letting institutions define and automate agentic processes — multi-step decisions, tool invocations, human-in-the-loop checkpoints — using BPMN/DMN-based orchestration that's governance-embedded by construction, not bolted on afterward. This is also the stage Chapter 3 exists to justify: an LLM is non-deterministic, but the process wrapped around it doesn't have to be, and Fluxnova is the mechanism that keeps that distinction real at runtime rather than aspirational.

Orchestration isn't limited to agents a single team built and hosts itself. Fluxnova can just as readily invoke an external agent — one belonging to another business unit inside the same institution, or one supplied by a partner or vendor outside it — as a step within the workflow, the same way it invokes any other tool. What makes this safe rather than a governance blind spot is that the external agent never operates outside the process: the workflow supporting the use case still owns the sequencing, still gates the step behind whatever deterministic boundary applies, and still traces the call the same way it traces an internal one. An external agent is a participant the process controls, not a hole in the boundary the process draws around itself.

## 2.5 Observability and Feedback — "How do we know it's still working?"

The pipeline closes the loop with real-time monitoring, cost tracking, and continuous improvement through evals and operational data — built on open tooling like OpenTelemetry for instrumentation and dashboards (Grafana is a common choice) for visualization — so governance isn't a point-in-time judgment but a live signal that feeds back into policy and architecture as agents evolve in production.
