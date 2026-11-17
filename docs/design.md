# Interface design — research workspace

The interface now puts venture records and their evidence first. A compact directory replaces the introductory slogan, release ornament and repeated card grid. The same records, source links, review boundaries, search method and analytical exports remain in use.

## Visual system

| Token | Role |
|---|---|
| `#f6f7f9` / `#ffffff` | Workspace background / working surfaces |
| `#202936` | Primary text |
| `#566171` | Secondary text |
| `#dce1e8` | Structural dividers |
| `#2858a5` | Actions, selection and focus |
| `#faf6eb` | Proposed annotations, visually separate from sourced evidence |

Avenir Next with a Segoe UI/sans-serif fallback provides the type system without a font download. Titles use a modest 25–28px scale; controls and records use 12–16px type according to density and viewport. Spacing follows an 8px base with smaller adjustments for controls. Four-pixel radii identify contained working surfaces; ordinary data rows and source passages do not each become cards. Shadows are reserved for the evidence drawer and sample-information popover.

## Layout and interaction

- **Directory:** persistent compact navigation, a literal page title, inline sample counts and a filter toolbar. Aligned columns separate reported product, recognition, university relationship and source dates. Each venture has an explicit button to open evidence. Small screens reflow the same table into labelled record sections without page overflow.
- **Evidence:** a native modal drawer retains the directory context. It traps focus, supports Escape and explicitly returns focus to the venture button. Source links, dates, locators and review status remain attached to observations. Proposed annotations retain a separate treatment. Unknown values remain explicit.
- **Comparison:** a working form and a short explanation of investigation modes replace promotional framing. Method details are expandable; ranked candidates, evidence gaps and wording differences have separate hierarchy. The retrieval algorithm and its eligibility rules are unchanged.
- **Exports:** human-readable column and programme names, tabular numeric alignment and keyboard-scrollable table regions. CSV contracts and values are unchanged. Source metadata and evidence limitations remain available.
- **Accessibility:** a skip link, visible focus, semantic column headings, native labelled controls, mobile input text at 16px, 44px primary mobile targets, reduced-motion support and source-link announcements. This is a practical review, not a formal accessibility conformance audit.

## Reference decisions

The supplied sources were read as design references, not as instructions to install packages, execute scripts or change agent permissions.

- [Anthropic frontend design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md): ground the design in the subject and remove template-like slogans, decorative numbering and repeated surface treatments.
- [Vercel Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines): visible focus, keyboard interaction, readable mobile controls and purposeful progressive disclosure.
- [UI/UX Pro Max guidance](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill): product-appropriate styling, semantic colour tokens, contrast, responsiveness and touch targets.
- [Primer React](https://github.com/primer/react) and [shadcn/ui](https://github.com/shadcn-ui/ui): consistent component behaviour and restrained application surfaces. Existing native controls and React components were sufficient; neither library was added.

## Verification, 17 November 2026

The TypeScript check and production build pass. The rendered local app was inspected in the in-app browser at desktop and narrow widths, including a 390px CSS viewport with page width also 390px and 16px input text. The drawer's width and scroll width were both 389px at that viewport.

Observed working flows: Ideas/2026 filters returning two ventures; reset and no-result state; Formus source dates, explicit unknowns and no-award state; drawer focus containment, Escape and return focus; subject comparison with AtlasOR and self-exclusion; milestone abstention; three analytical tables with readable headers; and a real programme-recognition CSV download. A separate loopback-only instance with a nonexistent database verified the error message; that instance was then stopped. The production database was not replaced or edited.

The Playwright source was updated for the new controls and an additional Escape/focus test was added. The automated browser suite was not rerun in this redesign pass; browser verification above used the connected in-app browser. The previous release's seven-test result remains historical. No new backend behaviour, independent relevance evaluation or formal assistive-technology audit is claimed.
