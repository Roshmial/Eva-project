---
name: artifact-delivery-and-runbooks
description: Deliver requested files directly and default to operational step-by-step runbooks when the user asks for deployment or setup instructions.
version: 1.0.0
tags: [delivery, artifacts, runbooks, deployment, instructions]
category: consulting
priority: 80
---

# Artifact Delivery and Runbooks

## When to Use
Use this skill when:
- the user asks for a file, attachment, export, or document to hand off to someone else;
- the user asks for deployment instructions, setup instructions, or an operational runbook;
- the user explicitly rejects explanatory prose and wants the deliverable itself.

## Core Rules
1. If the user asks for a file, send the file directly once it exists.
2. Do not paste the file contents into chat unless the user explicitly asks for inline text.
3. If the user asks for an instruction or deployment guide, default to a numbered step-by-step format.
4. Prefer actionable commands, checks, expected results, and rollback/verification points over conceptual explanation.

## Delivery Pattern
1. Build the artifact.
2. Verify the artifact exists and is in the requested format.
3. Deliver the artifact directly.
4. For runbooks, structure the document as:
   - prerequisites;
   - setup;
   - configuration;
   - launch;
   - verification;
   - troubleshooting.

## Pitfalls
- Do not answer a request for a file with a summary of the file.
- Do not give architecture description when the user asked for a deployment instruction.
- Do not mix conceptual overview and runbook by default; start with the operational version.
- Do not force the user to ask a second time for the actual attachment after generating it.

## For This User Pattern
This user often wants handoff-ready artifacts and gets irritated when given descriptions instead of the file or when a requested instruction turns into conceptual documentation. In these cases, deliver the file and make the instruction operational first.

## Verification
Before finishing, check:
- is the requested artifact actually created;
- is the output in the requested format;
- if the user asked for instructions, are they step-by-step and executable;
- did I deliver the artifact itself instead of re-describing it?
