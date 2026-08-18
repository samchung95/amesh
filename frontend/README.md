# AMESH web client

The production web client will use **React and TypeScript**.

The initial frontend architecture should use:

- a generated typed API client from the versioned OpenAPI contract;
- React Router for route ownership;
- TanStack Query or an equivalent cache for server state;
- a source editor capable of YAML language services and schema-aware diagnostics;
- a graph/canvas layer for visual workflow authoring;
- WebSocket or server-sent event adapters for live execution state and logs;
- AMESH-owned design tokens and components rather than copied Kestra visuals;
- WCAG 2.2 AA as the accessibility baseline;
- permission-aware route, action and field rendering backed by server authorization.

The concrete package manager, component library, editor and graph libraries should be recorded in follow-up ADRs before scaffolding. No frontend application has been generated yet.
