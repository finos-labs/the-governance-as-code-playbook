<!--
SPDX-License-Identifier: CC-BY-4.0
Copyright 2026 Fintech Open Source Foundation
-->

# Chapter 10 — Solution Architecture in Depth: From Reference Pattern to CALM Specification

Chapter 9 produced four artifacts for the KYC use case: a narrative, a taxonomy classification, a risk shortlist, and a mitigation mapping. This chapter picks up exactly where that leaves off — Steps 3 and 4 — turning that classification into an actual architecture decision, then expressing that decision as a CALM specification concrete enough for engineering to build against and for Fluxnova (Chapter 11) to enforce.

## 10.1 Selecting the Reference Architecture (Step 3)

Chapter 9's taxonomy classification already did most of the work here: a single agent with tool access (an extraction tool and a sanctions/PEP lookup), bounded autonomy, and a mandatory human-in-the-loop touchpoint for escalations. That maps directly onto the AI Reference Architecture Library's single-agent, tool-using pattern — not the multi-agent pattern, and not a plain retrieval-augmented pattern, because there's exactly one reasoning agent involved and its job is bounded tool use rather than open-ended document synthesis.

Selecting this pattern is not a formality — it commits the team to a known threat model that comes with the pattern, before a single line of the use case's own code is written. The single-agent, tool-using pattern's threat model already flags tool-scope creep (the agent reaching for a tool it wasn't meant to have), prompt injection via content returned from a tool call, and human-review bypass as the risks any implementation of this pattern needs to address. None of that is specific to KYC — it's inherited the moment the pattern is chosen, which is the entire point of maintaining a reference architecture library rather than threat-modeling every use case from a blank page.

It's worth noting what would have happened with a different classification. Had Chapter 9 classified this as a multi-agent use case — say, a separate agent for extraction and a separate one for sanctions screening, coordinated by a third — a different pattern would apply, with a different threat model: inter-agent trust boundaries and coordinator compromise, rather than the single-agent pattern's tool-scope concerns. The architecture follows the classification; it is never chosen first and used to justify the classification after the fact.

Sign-off at this stage sits with Hub Architecture, checking one thing specifically: does the chosen pattern's default threat model actually cover everything in Chapter 9's risk shortlist, or does the use case have a risk the pattern doesn't anticipate. Here, it does: the pattern's standard threat model has nothing to say about a sanctions match specifically, because that's a KYC-specific regulatory concern, not a generic tool-using-agent concern. That gap doesn't block the architecture selection — it becomes a control the team adds explicitly in Section 10.3, rather than something the pattern was ever going to hand over for free.

## 10.2 What the Pattern Leaves for This Use Case to Decide

This is the concrete version of the point made in Section 4.2: a reference architecture pattern, like a design pattern, gives capability structure without settling compliance specifics. Choosing the single-agent, tool-using pattern says the agent will reason over a bounded set of tools with a human checkpoint somewhere in the loop — it does not say which tools, what the checkpoint actually blocks, or which of Chapter 9's mitigations become enforceable rules rather than aspirations. Those decisions are what the CALM specification in Section 10.3 exists to pin down: exactly two tools (extraction, sanctions lookup), exactly one downstream system the agent can write to (the case management system), and exactly which of Chapter 9's mitigations get expressed as CALM controls rather than left as prose in a risk assessment document.

## 10.3 Translating the Pattern into CALM (Step 4)

With the pattern selected and its gaps identified, the architecture gets expressed as an actual CALM specification — the same nodes/relationships/controls structure introduced generically in Section 4.1, now applied for real. It's tempting to stop at the business-logic nodes — the agent, its two tools, the system it writes to — but a specification that only shows those leaves out exactly what a reviewer or an auditor asks about next: what actually executes this, and whose model is doing the reasoning. A complete architecture names the infrastructure too: the Fluxnova engine and its DMN decision service that Chapter 11 builds out in full, and the LLM provider platform the subprocess calls for reasoning.

```
{
  "nodes": [
    {
      "unique-id": "kyc-agentic-subprocess",
      "node-type": "service",
      "name": "KYC document review (agentic ad-hoc subprocess)",
      "description": "LLM-driven subprocess bounded to two inner tools: field extraction and sanctions/PEP lookup",
      "interfaces": []
    },
    {
      "unique-id": "kyc-extraction-tool",
      "node-type": "service",
      "name": "KYC field extraction tool",
      "description": "Extracts structured fields from an uploaded identity document"
    },
    {
      "unique-id": "sanctions-lookup-tool",
      "node-type": "service",
      "name": "Sanctions / PEP lookup tool",
      "description": "Queries sanctions and PEP lists for a given identity"
    },
    {
      "unique-id": "kyc-case-management",
      "node-type": "system",
      "name": "Case management system",
      "description": "Receives the subprocess's structured output and the process's routing decision"
    },
    {
      "unique-id": "fluxnova-engine",
      "node-type": "system",
      "name": "Fluxnova orchestration engine",
      "description": "Executes the KYC BPMN process definition and hosts the agentic ad-hoc subprocess (Chapter 11)"
    },
    {
      "unique-id": "fluxnova-dmn-service",
      "node-type": "service",
      "name": "Fluxnova DMN decision service",
      "description": "Evaluates the risk & confidence decision table at the process's first gateway (Section 11.5)"
    },
    {
      "unique-id": "llm-provider",
      "node-type": "service",
      "name": "LLM provider platform",
      "description": "Hosted large language model service the agentic subprocess calls for reasoning; provider and model selected via Fluxnova's agent configuration (Section 11.2)"
    }
  ],
  "relationships": [
    {
      "unique-id": "agent-calls-extraction",
      "connects": { "source": "kyc-agentic-subprocess", "destination": "kyc-extraction-tool" },
      "description": "Agent invokes extraction as a bounded tool call"
    },
    {
      "unique-id": "agent-calls-sanctions",
      "connects": { "source": "kyc-agentic-subprocess", "destination": "sanctions-lookup-tool" },
      "description": "Agent invokes sanctions/PEP lookup as a bounded tool call"
    },
    {
      "unique-id": "agent-writes-case",
      "connects": { "source": "kyc-agentic-subprocess", "destination": "kyc-case-management" },
      "description": "Structured output (fields, confidence, match status) is written to the case record"
    },
    {
      "unique-id": "engine-hosts-subprocess",
      "connects": { "source": "fluxnova-engine", "destination": "kyc-agentic-subprocess" },
      "description": "Fluxnova engine executes and hosts the agentic ad-hoc subprocess as part of the KYC BPMN process"
    },
    {
      "unique-id": "engine-uses-dmn",
      "connects": { "source": "fluxnova-engine", "destination": "fluxnova-dmn-service" },
      "description": "Engine invokes the DMN service to evaluate the risk & confidence gateway"
    },
    {
      "unique-id": "agent-calls-llm",
      "connects": { "source": "kyc-agentic-subprocess", "destination": "llm-provider" },
      "description": "Agent sends prompts to the configured LLM provider for reasoning inside the subprocess boundary"
    }
  ]
}
```

    {

      "unique-id": "kyc-extraction-tool",

      "node-type": "service",

      "name": "KYC field extraction tool",

      "description": "Extracts structured fields from an uploaded identity document"

    },

    {

      "unique-id": "sanctions-lookup-tool",

      "node-type": "service",

      "name": "Sanctions / PEP lookup tool",

      "description": "Queries sanctions and PEP lists for a given identity"

    },

    {

      "unique-id": "kyc-case-management",

      "node-type": "system",

      "name": "Case management system",

      "description": "Receives the subprocess's structured output and the process's routing decision"

    },

    {

      "unique-id": "fluxnova-engine",

      "node-type": "system",

      "name": "Fluxnova orchestration engine",

      "description": "Executes the KYC BPMN process definition and hosts the agentic ad-hoc subprocess (Chapter 11)"

    },

    {

      "unique-id": "fluxnova-dmn-service",

      "node-type": "service",

      "name": "Fluxnova DMN decision service",

      "description": "Evaluates the risk & confidence decision table at the process's first gateway (Section 11.5)"

    },

    {

      "unique-id": "llm-provider",

      "node-type": "service",

      "name": "LLM provider platform",

      "description": "Hosted large language model service the agentic subprocess calls for reasoning; provider and model selected via Fluxnova's agent configuration (Section 11.2)"

    }

  ],

  "relationships": [

    {

      "unique-id": "agent-calls-extraction",

      "connects": { "source": "kyc-agentic-subprocess", "destination": "kyc-extraction-tool" },

      "description": "Agent invokes extraction as a bounded tool call"

    },

    {

      "unique-id": "agent-calls-sanctions",

      "connects": { "source": "kyc-agentic-subprocess", "destination": "sanctions-lookup-tool" },

      "description": "Agent invokes sanctions/PEP lookup as a bounded tool call"

    },

    {

      "unique-id": "agent-writes-case",

      "connects": { "source": "kyc-agentic-subprocess", "destination": "kyc-case-management" },

      "description": "Structured output (fields, confidence, match status) is written to the case record"

    },

    {

      "unique-id": "engine-hosts-subprocess",

      "connects": { "source": "fluxnova-engine", "destination": "kyc-agentic-subprocess" },

      "description": "Fluxnova engine executes and hosts the agentic ad-hoc subprocess as part of the KYC BPMN process"

    },

    {

      "unique-id": "engine-uses-dmn",

      "connects": { "source": "fluxnova-engine", "destination": "fluxnova-dmn-service" },

      "description": "Engine invokes the DMN service to evaluate the risk & confidence gateway"

    },

    {

      "unique-id": "agent-calls-llm",

      "connects": { "source": "kyc-agentic-subprocess", "destination": "llm-provider" },

      "description": "Agent sends prompts to the configured LLM provider for reasoning inside the subprocess boundary"

    }

  ]

}

Notice what adding these three nodes changes. The business-logic view (agent, tools, case management) shows what the use case does; the infrastructure view (the engine, the DMN service, the LLM provider) shows what it runs on and whose model is in the loop — and both now live in the same reviewable file rather than one living in a design document and the other living nowhere until an auditor asks. The llm-provider node in particular is what gives vendor risk and model governance something concrete to review: which provider, which model, and — per Section 10.4 — whether that choice is still the one Governance signed off on.

This is where Chapter 9's mitigation mapping stops being prose and starts being enforceable: the sanctions-override gap identified in Section 10.1, and the mandatory-human-review mitigation from Chapter 9.2, both become controls attached directly to the agent node. The infrastructure nodes get their own, separate control — this is deliberately not the same compliance block as the agent's, because it's enforced by Common Cloud Controls (Chapter 2) rather than by CALM's own graph.

```
{
  "nodes": [
    {
      "unique-id": "kyc-agentic-subprocess",
      "node-type": "service",
      "name": "KYC document review (agentic ad-hoc subprocess)",
      "controls": {
        "compliance": {
          "description": "Controls derived from Chapter 9's risk shortlist and mitigation mapping",
          "requirements": [
            {
              "control-requirement-url": "https://fsi.example/controls/schema/no-sanctions-override.json",
              "control-config-url": "https://fsi.example/controls/config/kyc-no-sanctions-override.json"
            },
            {
              "control-requirement-url": "https://fsi.example/controls/schema/mandatory-human-review.json",
              "control-config-url": "https://fsi.example/controls/config/kyc-confidence-threshold-95.json"
            }
          ]
        }
      }
    },
    {
      "unique-id": "fluxnova-engine",
      "node-type": "system",
      "name": "Fluxnova orchestration engine",
      "controls": {
        "infrastructure": {
          "description": "Common Cloud Controls mappings for the hosting environment (Chapter 2)",
          "requirements": [
            {
              "control-requirement-url": "https://fsi.example/controls/schema/ccc-workload-isolation.json",
              "control-config-url": "https://fsi.example/controls/config/kyc-fluxnova-hosting.json"
            }
          ]
        }
      }
    }
  ]
}
```

            {

              "control-requirement-url": "https://fsi.example/controls/schema/mandatory-human-review.json",

              "control-config-url": "https://fsi.example/controls/config/kyc-confidence-threshold-95.json"

            }

          ]

        }

      }

    },

    {

      "unique-id": "fluxnova-engine",

      "node-type": "system",

      "name": "Fluxnova orchestration engine",

      "controls": {

        "infrastructure": {

          "description": "Common Cloud Controls mappings for the hosting environment (Chapter 2)",

          "requirements": [

            {

              "control-requirement-url": "https://fsi.example/controls/schema/ccc-workload-isolation.json",

              "control-config-url": "https://fsi.example/controls/config/kyc-fluxnova-hosting.json"

            }

          ]

        }

      }

    }

  ]

}

Nothing here is new mechanism — Section 4.1 already covered how a requirement and a configuration file combine. What's new is that both controls now trace directly back to a specific line in Chapter 9: “no override on a sanctions hit” is the architecture-level gap flagged in Section 10.1, and “mandatory human confirmation before any sanctions-adjacent case is cleared” is lifted verbatim from Chapter 9.2's mitigation mapping. A reviewer can trace every control in this file back to a specific, already-approved line in the risk assessment — there is no control here that wasn't first justified as a mitigation.

## 10.4 Architecture Review and Sign-off

Before engineering proceeds to Fluxnova modeling, this CALM file goes through a specific, narrow review — not a general architecture review, but a check against three things:

- **Coverage.** Does every mitigation in Chapter 9's mapping have a corresponding control in this file? A mitigation with no matching control is a mitigation that exists on paper only.

- **Scope match.** Does the relationships list match exactly the tool authority the taxonomy approved in Chapter 9 — no more, no less? An extra relationship here is exactly the kind of scope creep the pattern's threat model in Section 10.1 flagged.

- **Data-sensitivity consistency.** Does the node's classification align with the data-handling requirements Chapter 9 identified for PII and government ID data?

- **Infrastructure and vendor accountability.** Does the llm-provider node name a specific, approved provider and model — not a placeholder — and does the fluxnova-engine node's hosting environment carry the Common Cloud Controls mapping it needs? A CALM file with a business-logic layer but no named infrastructure is exactly the gap this review exists to close.

This review sits with Hub Architecture and Governance Layer (MRM) jointly — the same pairing Chapter 7's Step 3 and Step 4 task lists already assign. Once both sign off, the CALM file is the approved architecture: not a proposal engineering will refine later, but the specification Chapter 11's Fluxnova process gets built against.

## 10.5 From CALM to Fluxnova: What Carries Forward

Every element defined in this chapter has a direct, named counterpart in Chapter 11. The two tool nodes — kyc-extraction-tool and sanctions-lookup-tool — become the two inner tools of the agentic ad-hoc subprocess in Section 11.3. The fluxnova-engine and fluxnova-dmn-service nodes are the literal CALM-level names for the workflow and decision-table components Chapter 11 builds out in full — the BPMN process and the DMN table are not new things Chapter 11 introduces, they're what these two nodes already committed the architecture to. The llm-provider node becomes the specific Provider and Model fields configured on the agentic ad-hoc subprocess in Section 11.2. The no-sanctions-override control becomes the row in the DMN decision table (Section 11.5) that routes any confirmed or possible match to escalation with no auto-clear path. The mandatory-human-review control becomes the analyst review task that Fluxnova's process definition will not let a case bypass. None of this is a loose thematic connection — Fluxnova's configuration literally references the node and control identifiers defined here, which is what makes the architecture review in Section 10.4 a real gate rather than a documentation exercise: get it wrong here, and Chapter 11 inherits the mistake.
