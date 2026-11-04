---
type: Index
title: Project Skills Index
description: Routes litestar-asyncapi work to its domain engineering skill, review skill, paired subagents and knowledge chapters.
tags: [skills, agents, index]
---

# Project Skills

| Domain | Prefix | Engineering Skill | Review Skill | Reviewer Subagent | Specialist Subagent | Knowledge Chapters |
| --- | --- | --- | --- | --- | --- | --- |
| Document generation & discovery | `GEN` | [asyncapi-generation](./asyncapi-generation/SKILL.md) | [review-asyncapi-generation](./review-asyncapi-generation/SKILL.md) | [asyncapi-generation-reviewer](../agents/asyncapi-generation-reviewer.md) | [asyncapi-generation-specialist](../agents/asyncapi-generation-specialist.md) | [02](../bundles/knowledge/architecture/02-generator-pipeline.md), [03](../bundles/knowledge/architecture/03-discovery-and-extractors.md), [05](../bundles/knowledge/architecture/05-spec-objects-and-serialization.md), [contracts](../bundles/knowledge/domains/asyncapi-contracts.md) |
| Schema bridge & Draft07 | `SCH` | [asyncapi-schema](./asyncapi-schema/SKILL.md) | [review-asyncapi-schema](./review-asyncapi-schema/SKILL.md) | [asyncapi-schema-reviewer](../agents/asyncapi-schema-reviewer.md) | [asyncapi-schema-specialist](../agents/asyncapi-schema-specialist.md) | [04](../bundles/knowledge/architecture/04-schema-generation.md), [schema patterns](../bundles/knowledge/patterns/schema-generation.md), [ADR-002](../bundles/knowledge/decisions/adr-002-draft07-wire-dialect.md) |
| Docs routes, renderers & UI | `UI` | [asyncapi-docs-ui](./asyncapi-docs-ui/SKILL.md) | [review-asyncapi-docs-ui](./review-asyncapi-docs-ui/SKILL.md) | [asyncapi-docs-ui-reviewer](../agents/asyncapi-docs-ui-reviewer.md) | [asyncapi-docs-ui-specialist](../agents/asyncapi-docs-ui-specialist.md) | [01](../bundles/knowledge/architecture/01-system-overview.md), [06](../bundles/knowledge/architecture/06-render-plugins-and-ui.md), [renderer security](../bundles/knowledge/patterns/renderer-security.md), [ADR-003](../bundles/knowledge/decisions/adr-003-packaged-upstream-ui.md) |
| Release, CI & distribution | `REL` | [asyncapi-release-ci](./asyncapi-release-ci/SKILL.md) | [review-asyncapi-release-ci](./review-asyncapi-release-ci/SKILL.md) | [asyncapi-release-ci-reviewer](../agents/asyncapi-release-ci-reviewer.md) | [asyncapi-release-ci-specialist](../agents/asyncapi-release-ci-specialist.md) | [CI supply chain](../bundles/knowledge/patterns/ci-supply-chain.md), [distribution lanes](../bundles/knowledge/testing/distribution-and-browser.md), [workflow](../bundles/knowledge/workflow.md) |

All domains share [testing/public-seam-tdd](../bundles/knowledge/testing/public-seam-tdd.md) and [gotchas/runtime-and-tooling](../bundles/knowledge/gotchas/runtime-and-tooling.md).
