# Chapter 4 — What This Means for Engineering Teams

For engineers, the practical shift is significant: governance stops being someone else's job that shows up at the end. This chapter looks at what that shift actually looks like in the artifacts engineers write and review day to day, starting with CALM itself.

## 4.1 CALM in Practice: Nodes, Relationships, and Controls

CALM is a JSON-based, version-controlled schema — the kind of file that sits in a repository and gets reviewed in a pull request like any other. Its three core building blocks are nodes (the components of an architecture), relationships (how those components connect), and controls (the requirements attached to a node or relationship, and how they're satisfied). The point of CALM isn't specific to any one use case, so the smallest useful illustration is a “hello world” agent rather than a full financial-services scenario — the mechanics below are exactly what a real use case builds on.

A minimal CALM fragment starts with the nodes and the relationships between them: a simple greeter agent, one tool it can call, and a place it logs its output.

```
{
  "nodes": [
    {
      "unique-id": "hello-world-agent",
      "node-type": "service",
      "name": "Hello World Agent (agentic ad-hoc subprocess)",
      "description": "LLM-driven subprocess bounded to a single inner tool: composing a greeting",
      "interfaces": []
    },
    {
      "unique-id": "greeting-tool",
      "node-type": "service",
      "name": "Greeting Composer Tool",
      "description": "Formats a greeting string for a given name and language"
    },
    {
      "unique-id": "interaction-log",
      "node-type": "system",
      "name": "Interaction Log",
      "description": "Receives the agent's output for auditing"
    }
  ],
  "relationships": [
    {
      "unique-id": "agent-calls-greeting-tool",
      "connects": { "source": "hello-world-agent", "destination": "greeting-tool" },
      "description": "Agent invokes greeting composition as a bounded tool call"
    },
    {
      "unique-id": "agent-writes-log",
      "connects": { "source": "hello-world-agent", "destination": "interaction-log" },
      "description": "Agent's output is written to the interaction log"
    }
  ]
}
```

Notice what this fragment does and doesn't say. It says the agentic subprocess exists, what it's called, and exactly which one tool and which downstream system it's allowed to talk to — the relationships list is the complete set of connections; there is no relationship to anything else, which means a reviewer (or an automated CI check) can see the agent's entire reachable surface at a glance. It doesn't yet say anything about compliance requirements — that's what controls are for.

Controls attach directly to a node, pairing a requirement (what must be true) with a configuration (the specific values that satisfy it for this case). Here, a simple content-safety control on the same agent:

```
{
  "nodes": [
    {
      "unique-id": "hello-world-agent",
      "node-type": "service",
      "name": "Hello World Agent (agentic ad-hoc subprocess)",
      "controls": {
        "content-safety": {
          "description": "Controls governing what the agent is permitted to output",
          "requirements": [
            {
              "control-requirement-url": "https://example.org/controls/schema/no-restricted-languages.json",
              "control-config-url": "https://example.org/controls/config/hello-world-allowed-languages.json"
            }
          ]
        }
      }
    }
  ]
}
```

The requirement file (“no-restricted-languages.json”) is the reusable, versioned statement of the rule itself — in this case, that the agent may only respond in a language from an approved list. The configuration file is what makes that rule concrete for this specific node: the actual list of approved languages. A real use case follows exactly this same pattern, just with requirements that matter more than a greeting's language — a control stating that a sanctions match can never be auto-cleared, say, looks structurally identical to the one above, with a different requirement and a different configuration behind it. Later chapters build one of those in full.

Because this is JSON, checking it is mechanical. A CI job can confirm that every node tagged as an agentic subprocess has a non-empty controls block, that every relationship listed matches a tool the agent is actually configured to call, and that no new relationship was added without a matching control review — the same category of check a security team already runs against infrastructure-as-code today, just pointed at the architecture of the agent instead of the cloud resources around it.

## 4.2 Where Agentic Design Patterns Stop and Governance-as-Code Starts

Most of what engineering teams read about building agents right now comes from design-pattern guidance — Anthropic's widely-read write-up on building effective agents, for instance, lays out patterns like prompt chaining, routing, parallelization, orchestrator-workers, and evaluator-optimizer, alongside the general shape of an autonomous agent loop. Other common patterns in circulation — ReAct-style reasoning-and-acting loops, plan-and-execute — cover similar ground. These are genuinely useful, and nothing in this guide argues against using them.

But it's worth being precise about what these patterns are for. Every one of them answers a capability question: how should an agent structure its reasoning and tool use to complete a task well, reliably, and efficiently. None of them, on their own, answers a compliance question: which of this agent's actions require a human sign-off that cannot be skipped, how do you prove after the fact that a specific decision was reached the same way it would be reached again, or how does this pattern map to the risk categories a regulator or an internal audit committee actually cares about. That's not a criticism of the patterns — it's simply outside what they set out to do.

- **Orchestrator-workers**, for example, is a pattern for decomposing a task across multiple specialized calls — it says nothing about which of those worker calls, if any, needs a mandatory human checkpoint before its output can be acted on.

- **Routing** decides which specialized path handles a given input — it doesn't specify what evidence needs to exist afterward to show a regulator which path a specific case took and why.

- **Evaluator-optimizer** improves output quality through iterative self-critique — it has no concept of a control that can never be overridden regardless of how confident the evaluator becomes.

This is exactly the gap Governance-as-Code fills, and it does so by sitting one level below the pattern rather than replacing it. An engineering team is free to implement whatever reasoning pattern best suits the tools available inside an agentic ad-hoc subprocess like the one above — a simple routing decision between tools, a small ReAct-style loop, or nothing more sophisticated than a fixed call sequence. Whichever pattern is chosen lives entirely inside the subprocess boundary defined in the CALM fragment. The pattern determines how well the agent reasons within that boundary; the CALM controls, the AIGF risk mapping, and the Fluxnova process definition determine that the boundary itself cannot be crossed, that every action is traced, and that the specific decision point a regulator will ask about has an answer that doesn't depend on trusting the pattern's judgment. Put another way: design patterns make the agent good at its job inside the box. Governance-as-code is what defines and enforces the box, and hands you the evidence that it held.

## 4.3 What Changes Day to Day for Engineers

- **Compliance checks run where code already runs.** Because AIGF policies get expressed through CALM as executable specifications, they slot into existing CI/CD pipelines. A pull request that changes an agent's tool permissions or data access can be checked against AIGF's risk catalog automatically, the same way a linter or test suite runs today.

- **Reference architectures remove guesswork.** Rather than each team inventing its own pattern for a multi-agent system and hoping it satisfies risk and compliance later, the AI Reference Architecture Library gives engineers pre-vetted, composable patterns with security, observability, and cost boundaries already designed in.

- **Governance becomes a build-time signal, not a launch blocker.** Automated policy validation surfaces issues while a system is being built, not in a review meeting three weeks before a planned launch — which means fewer late-stage redesigns and a much shorter path from prototype to production.

- **The FINOS AIGF MCP Server makes this conversational and contextual.** It takes requirements documents and architectural descriptions and turns them into actionable, governed insights — flagging relevant risks and mitigations directly inside the development workflow, with AI-generated outputs quality-assured by human review before anything is acted on.
