# Glossary

**Flow / workflow**

A named, versioned graph of inputs, tasks and outputs. The UI usually says “workflow”; the API and DSL
use “flow”.

**Node / task**

One typed unit in a workflow. “Node” describes its visual position; “task” is the persisted DSL and
execution term.

**Execution**

One durable run of an exact flow revision with validated inputs.

**Task run**

One task's attempt within an execution. Retries create additional attempts without rewriting earlier
evidence.

**Artifact**

A governed file or image stored through AMESH's object-storage boundary and referenced by tenant,
namespace, version and digest metadata.

**Agent definition**

An immutable resource that pins input/output schemas, prompts, skills, model policy, tools, evaluations
and hard budgets.

**Agent session**

A durable execution of an agent revision. One logical session can contain ordered later turns while
each execution turn retains its own journal and checkpoint.

**Harness**

The swappable runtime adapter that drives the bounded model/tool loop. It must pass AMESH's conformance
contract and cannot widen the pinned capability envelope.

**Plugin**

A versioned package that contributes declared resources or process services through supported extension
contracts.

**ToolProvider**

The AMESH interface that discovers, validates and invokes typed tools under policy.

**MCP connection**

A governed, revisioned connection whose selected MCP tools can be pinned into an agent envelope.

**Capability envelope**

The resolved immutable set of resources, permissions, budgets and schemas that bounds an agent run.

**Chronological progress**

The persisted safe sequence of model, tool, validation and terminal frames. It is not raw hidden
reasoning.

**Replay**

A new governed execution tied to frozen source inputs and resource pins. It does not mutate the source
execution.
