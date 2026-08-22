# AMESH Design System

## Direction

AMESH is a graphite control room: dense enough for operators, calm enough for long authoring sessions,
and legible at a glance during incidents. The interface pairs a dark instrument rail with a warm
paper-like workspace, using signal green only for primary actions and live state—not decoration.
Typography and alignment should feel closer to a technical field notebook than a generic SaaS card
grid.

## Tokens

- Type: IBM Plex Mono for display, identifiers and telemetry; IBM Plex Sans for body and controls.
  Scale: 12 / 14 / 16 / 20 / 28 / 40 px with 1.5 body leading and 1.15 heading leading.
- Color: workspace `#F3F1E8`; surface `#FFFEF8`; rail `#151A18`; text `#17201C`; muted
  `#5C685F`; border `#CDD2C9`; accent `#0A6F53`; signal `#C9F31D`; info `#0B6E99`; warning
  `#A85A00`; danger `#B42318`; focus `#0B84F3`.
- Spacing: 4 px base — 4 / 8 / 12 / 16 / 24 / 32 / 48.
- Radius: 6 px for controls, 10 px for large surfaces. Shadow: one low level for sticky surfaces and
  one high level for the command palette only.
- Motion: 180 ms ease-out for hover, focus and panel state. Disable non-essential motion under
  `prefers-reduced-motion`.

## Components

- App rail: 264 px on desktop, compact 76 px on tablet and a modal drawer on phone. Navigation is
  grouped into Build, Operate and Govern; the current route uses both a signal bar and text treatment.
- Top bar: tenant and namespace context, global command trigger, connection state, notifications and
  user menu. Controls retain a 44 px minimum target.
- Buttons: solid accent for the single primary action, outlined surface for secondary actions, quiet
  text for low emphasis and red outline for destructive actions. Every variant has hover, focus,
  active, disabled and busy states.
- Data surfaces: bordered sections with square internal dividers; reserve cards for discrete summaries,
  not every block. Tables remain the default for operational collections.
- Status: icon, label and shape accompany color. Running uses blue, success green, warning amber,
  failure red and unknown gray.
- Empty/error/loading: every data region owns a purposeful empty instruction, retryable error panel and
  skeleton that preserves layout.
- Command palette: high-shadow dialog with an explicit title, labelled search, grouped results,
  keyboard hints and a designed no-results state.
- Focus: all interactive elements receive a 3 px focus ring with a 2 px surface offset. A skip link is
  the first tab stop.
- Authentication gate: local user login is the primary entry path and uses the same split graphite/paper
  composition as the existing connection gate. User handle and password remain ordinary labelled fields;
  tenant context is visually secondary. API-token entry is an explicit alternate mode for service and
  operator workflows, never a second competing primary form. Busy, rejected, locked and federated-only
  states keep the panel dimensions stable and announce their result.

## Responsive and accessibility contract

- Desktop is optimized at 1440 px, tablet at 1024/768 px and phone at 390 px. Information priority,
  not merely width, determines what collapses.
- Semantic landmarks, real controls, bound labels, live regions and announced route headings are
  mandatory. Never use color alone, and never suppress a focus outline without the shared replacement.
- Body text and controls meet 4.5:1 contrast; large text and non-text boundaries meet 3:1. Touch
  targets are at least 44 by 44 px.
- English and Simplified Chinese are the first locale fixtures. Dates, numbers and time zones use the
  selected locale and explicit IANA zone.
