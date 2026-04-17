# Frontend Verification

Patterns for verifying frontend changes: UI rendering, component behavior, styling, accessibility, and user interactions.

## Verification Methods (by reliability)

### 1. Automated Component/Unit Tests

Best for: logic in components, state management, data transforms, hooks.

Run the relevant test file, not the whole suite. If the project uses snapshot tests, check whether the snapshot update is intentional (the diff should match what you expect from the change).

### 2. Browser Automation (agent-browser)

Best for: verifying rendered output, user flows, interactive behavior.

Use `agent-browser` to:
- Navigate to the page
- Verify elements are present and visible
- Click buttons, fill forms, submit
- Check that the result matches expectations (text content, element state, navigation)

**Browser strategy: get to proof fast**
- Start from the claim, not from the DOM. Decide what must be proven before opening the browser.
- If you are verifying a frontend implementation or fix in app code we own, and locator thrash is likely to dominate the work, treat temporary stable instrumentation as an allowed early tactic: add a narrow `data-test-id` or equivalent hook to the specific element, use it to prove the claim, then remove it before reporting.
- If selector stability is not the bottleneck, use the normal path: open the page, wait for the relevant state, snapshot with refs, act, then verify the outcome.
- If an element is hard to find, stop retrying blind clicks. Usually the problem is one of: wrong page state, missing wait, stale refs after a DOM change, overly broad scope, or a visual-only control.
- Escalate deliberately: first verify URL/text/state, then re-snapshot, then narrow scope, then use annotated screenshot or another stronger locator only if needed.
- Keep temporary instrumentation narrow and reversible. Do not redesign the DOM for testing, and do not leave verification hooks behind unless the user wants a durable selector.
- Prove the outcome, not just the interaction. A successful click is weak evidence unless the expected text, navigation, state, or visual result also changed.

### 3. Visual Verification (media-processor)

When the claim depends on visual criteria (colors, spacing, layout, design match):
1. Use `agent-browser` to capture a screenshot
2. Use `/media-processor` to analyze it accurately

Don't trust raw vision for precise visual details — pixel-level accuracy matters for design claims.

**Common visual checks:**
- CSS or styling changes
- exact color or spacing claims
- design-match claims against a mockup or screenshot
- responsive layout changes
- theme and dark-mode changes

## Common Frontend Verification Patterns

### Component Rendering
- Verify the component renders without errors
- Check key content is present (text, images, data)
- Verify conditional elements appear/disappear based on state

### Form Behavior
- Submit with valid data → success feedback
- Submit with invalid data → error messages appear on correct fields
- Required field enforcement
- Form state reset after submission

### Navigation / Routing
- Links navigate to correct pages
- Protected routes redirect unauthenticated users
- Back button behavior
- URL parameters are respected

### State Management
- UI reflects state changes
- State persists across navigation (when it should)
- Loading/error/empty states render correctly

## What Makes Frontend Evidence Strong

| Strong evidence | Weak evidence |
|----------------|---------------|
| Browser screenshot showing correct render | "The component code looks right" |
| Test output showing component behavior | "The styles are applied" (without visual proof) |
| Form submission produces expected result | Only tested that form renders |
| Navigation verified in browser | "The routes are configured correctly" |
| Type checker passes after refactor | Only visual inspection of changed files |
