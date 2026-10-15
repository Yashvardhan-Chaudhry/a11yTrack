# ACCESSIBILITY.md

What I checked, what I found, what I fixed, and what is still open. Target was
the WCAG 2.2 AA basics listed in the brief. Everything below was done on the
shipped code, not a mock-up.

## 1. Scope and tools

| Item | Detail |
|---|---|
| Date | 15 October 2026 |
| OS | Windows 10 Home 22H2 |
| Browser | Google Chrome 155.0.8059.40 |
| Screen reader | NVDA 2026.2 with Speech Viewer open to log announcements |
| Automated checker | axe-core 4.13.0 via the axe CLI, headless Chrome, rule tags wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa, best-practice |
| Second checker | Lighthouse (Chrome DevTools), Accessibility category |
| Zoom / width | Chrome 200 % zoom; DevTools device toolbar at 320 px |

The app is server-rendered HTML with native controls and one small script
(the status-message re-announce in `base.html`), so most criteria are met by
the markup itself rather than by ARIA.

## 2. Keyboard-only pass

Mouse unplugged. Every flow below was completed with Tab, Shift+Tab, Enter,
Space and the arrow keys only.

| Flow | Result |
|---|---|
| First Tab on every page lands on "Skip to main content"; Enter moves focus into `<main>` and the next Tab is the first control inside it | Pass |
| Sign in: select user with arrows, Enter submits; submitting with no user shows an inline error and focus moves to the select, which is marked invalid and described by the error text | Pass |
| Issue list: filters (two selects + Apply + Clear) and every title link reachable in visual order | Pass |
| Create issue: every field, Save and Cancel reachable; nothing skipped or hit twice | Pass |
| Create with empty fields: focus lands on the error summary; each summary link moves focus to its field | Pass |
| Detail page: Edit link and one button per allowed transition; Enter and Space both activate | Pass |
| Full workflow Open → In Progress → Fixed → Verified → Closed; Reopened offered after Fixed and Verified; Closed offers nothing | Pass |
| Edit issue and save; stale second tab gets the 409 message with focus on it and typed values kept | Pass |
| Sign out, sign in as the other user: first user's issues absent; typed URL of the other user's issue gives the 404 page with heading, "Error:" title and a link back | Pass |
| Focus ring visible on every focusable element including selects, table links and the blue buttons (two-ring indicator: 3 px dark outline plus 2 px white inner ring) | Pass |
| No keyboard trap anywhere; Shift+Tab reverses cleanly | Pass |

### Reflow (320 px and 200 % zoom)

Checked in Chrome on every page state, including the validation-error, 400,
409 and 404 pages.

| Check | Result |
|---|---|
| 320 px wide (DevTools device toolbar): header and filter bar wrap onto new lines; the issue table keeps its four columns and wraps long text inside cells (`overflow-wrap: anywhere`); no horizontal page scroll and no clipped content | Pass |
| 200 % zoom (Ctrl+Plus) at a normal window width: same wrapping behaviour; forms, buttons and the error summary stay fully visible; no sideways scroll | Pass |

## 3. Automated checks

### axe

Because most pages need a signed-in session and some states only exist after a
POST (validation errors, 400, 409, 404), I rendered every state through the
Flask test client to static HTML and ran axe on each file. 16 page states,
0 violations, 0 "needs review" items.

| Page state | Violations | Needs review | Rules passed |
|---|---|---|---|
| Sign in | 0 | 0 | 39 |
| Sign in, no user chosen (400) | 0 | 0 | 39 |
| Issue list after sign-in (status message shown) | 0 | 0 | 44 |
| Issue list | 0 | 0 | 44 |
| Issue list, filtered | 0 | 0 | 44 |
| Issue list, no matches | 0 | 0 | 39 |
| New issue | 0 | 0 | 40 |
| New issue with validation errors (400) | 0 | 0 | 40 |
| Detail after create (status message shown) | 0 | 0 | 37 |
| Detail | 0 | 0 | 37 |
| Detail, blocked transition (400) | 0 | 0 | 38 |
| Detail after status change (status message shown) | 0 | 0 | 42 |
| Detail, stale version (409) | 0 | 0 | 44 |
| Edit issue | 0 | 0 | 40 |
| Edit, stale version (409) | 0 | 0 | 41 |
| Another user's issue (404) | 0 | 0 | 35 |

One finding came out of this run and was fixed before the table above was
produced: the first version of the error-summary fix (section 4) used
`aria-labelledby` on a plain `<div>`, which axe flags as `aria-prohibited-attr`
because a generic element cannot take a label. Adding `role="group"` resolved
it.

### Lighthouse

Desktop, Accessibility category only. Lighthouse runs a subset of the same axe
rules, so it is a second opinion rather than a new check; it also lists ten
manual items (tab order, focus not trapped, focus directed to new content, and
so on) that are covered by sections 2 and 4.

| Page | Accessibility score |
|---|---|
| Sign in | 100 |
| Issue list | 100 |
| New issue | 100 |
| Issue detail | 100 |

### Colour contrast

Computed from the values in `style.css` with the WCAG relative-luminance
formula. AA needs 4.5:1 for text and 3:1 for UI components and focus
indicators.

| Pair | Ratio |
|---|---|
| Body text #1a1a1a on white | 17.4:1 |
| Hint text #4a4a4a on white | 8.9:1 |
| Links #0b3d91 on white | 10.0:1 |
| Error text #a4000f on white | 8.1:1 |
| Input border #5c5c5c on white (UI, 3:1) | 6.7:1 |
| Focus ring #0b3d91 on white (UI, 3:1) | 10.0:1 |
| Focus ring on the status box background #e8f1fb | 8.8:1 |
| Text on the status box #e8f1fb | 15.3:1 |
| Text on table header #f0f0f0 | 15.3:1 |
| White text on blue buttons #0b3d91 | 10.0:1 |

## 4. Screen reader pass (NVDA)

Checked with NVDA 2026.2 in Chrome, browse mode, Speech Viewer logging. Keys
used: Tab, H (headings), D (landmarks), T (tables), Ctrl+Alt+arrows (table
cells), F (form fields), NVDA+T (title).

| Brief requirement | What NVDA said / did |
|---|---|
| Every input has a visible label; required marked in text | Each field announced with its label and "required" as part of the label text, e.g. "Title (required), edit" |
| Errors next to the field, findable by a screen reader user | Invalid fields announced as "invalid" with the error text read via `aria-describedby`; focus moved to the summary on load (see flag 2) |
| Status messages announced without moving focus | Not announced in the first build (see flag 3). Fixed and retested; focus stays at the top of the page |
| Severity and status as words | Table cells and transition buttons read as words ("Serious", "Mark as In Progress, button") |
| One h1, sensible heading order, title changes per page | H walks h1 then h2s in order on every page; NVDA+T gives a distinct title per page and "Error:" is spoken first on error states |
| Skip link | First Tab reads "Skip to main content, link"; Enter lands in main |
| Native controls, real table | T announces "table with 4 columns and N rows"; arrowing across a row reads the column header before each cell; status history is also a real table |

### Flags found and what was done

**Flag 1: the focus ring does not move when arrowing through the table.**
Pressing T then Ctrl+Alt+Right moves NVDA's browse cursor, not browser focus,
so the app's focus ring stays on the last focused link. This is how NVDA works
in browse mode and is not an app defect. Making cells focusable to drag the
ring along would add a dozen tab stops per page for keyboard users, so I left
it. NVDA's own "Focus Highlight" (Settings, Vision) draws a cursor outline for
users who want one. Documented, not changed.

**Flag 2: error summary announced as "alert" rather than its heading.**
The summary had `role="alert"` and also received focus on load, so NVDA spoke
the role name and the "There is a problem" heading was lost. Changed to
`role="group" aria-labelledby="error-summary-heading"` with focus still moved
on load, so NVDA now reads "There is a problem, grouping" and then the list of
errors. NVDA also says "same page link" for each error link; that is correct
behaviour for in-page anchors and was left alone.
Retest after the fix: on submitting an empty form NVDA reads the heading
and then the error list; no "alert" prefix.

**Flag 3: "Issue saved." and "Status changed from X to Y." were never spoken.**
Reproduced: after submitting, NVDA read the new page title and started reading
the page, but the message box was never announced. Cause, from reading the
code: the script blanked the live region at load and re-inserted it 150 ms
later. NVDA builds its reading buffer from the DOM as loaded, so the box was
empty in the reading pass, and the 150 ms re-insertion was a polite
live-region update that fired while NVDA was still speaking the title, so it
was dropped. Fix: the box now lives inside `<main>` above the heading so it
is in reading order and reachable with D. The element is
`role="status" aria-live="assertive" aria-atomic="true"`: the role is kept for
semantics and assertive overrides the role's default politeness so it can
interrupt page-load speech. The message is present in the HTML at load, so it
is in reading order. After one second the node is detached and re-attached
once, which NVDA treats as a change and announces. Focus does not move.
Retest after the fix: "Issue saved." and "Status changed from Open to In
Progress." are both spoken after the page title with no key pressed, and
focus is still at the top of the page.

## 5. Brief checklist, where each point is met

| Brief bullet | Where |
|---|---|
| Keyboard for every button, link, form, filter; visible focus; tab order | Native controls in document order; `:focus-visible` two-ring style in `style.css`; links underlined (browser default, not reset) |
| Visible label on every input; required in text | `<label for>` on every field; "(required)" inside the label text |
| Errors in text next to the field, findable by screen reader | `validation.py` returns `{field: message}`; template renders inline `<p id="field-error">` wired with `aria-describedby`/`aria-invalid`, plus a summary that receives focus through `tabindex="-1"` + `autofocus` (no script); sign-in moves focus to the invalid select |
| Messages announced without moving focus | Flask `flash()` → `role="status" aria-live="assertive" aria-atomic="true"` region in `base.html`, re-attached once after 1 s by the only script in the app (section 4, flag 3) |
| Severity and status shown as words | Plain text in table cells, detail list and button labels; no colour-only badges |
| One h1, heading order, per-page title, skip link | `{% block title %}` per template, "Error: " prefix on error states, one `<h1>` per page, skip link first in `<body>` |
| Native controls; list as a real table | `<table>` with `<caption>`, `<th scope="col">` and `<th scope="row">`; `<select>`, `<button>`, `<input list>` + `<datalist>` |
| Contrast 4.5:1 text, 3:1 UI | Table in section 3 |
| 320 px and 200 % zoom | Flex-wrapping header and filters, 4-column table with wrapping cells, no fixed widths; results in section 2, "Reflow" |

### WCAG 2.2-specific criteria

The 2.2 additions that apply to this app, checked by hand:

| Criterion | How it is met |
|---|---|
| 2.4.11 Focus Not Obscured (Minimum) | No sticky or fixed header, footer or overlay, so nothing can cover a focused element |
| 2.5.8 Target Size (Minimum) | Buttons are about 44 px tall (0.5 rem padding on 1.5 line-height text); inline links in table cells and prose are exempt under the inline exception |
| 3.3.7 Redundant Entry | Validation errors and the 409 response re-render the form with the typed values; the edit form is prefilled |
| 3.3.8 Accessible Authentication (Minimum) | Sign-in is a user picker with no password, CAPTCHA or memory test |

## 6. Remaining issues and honest limitations

- The status announcement depends on a one-second timer in the only script
  in the app. Without JavaScript the box is still in reading order under
  the main landmark, but it is not announced automatically.
- `aria-live="assertive"` interrupts whatever NVDA is saying. Acceptable here
  because it is the only live region and fires once per page load, but it
  would need to be polite if the page ever had more than one.
- The focus ring does not follow NVDA's browse cursor in tables (flag 1).
  By design, but a first-time NVDA user may find it confusing.
- The WCAG criterion field uses `<input list>` + `<datalist>`. Chrome, Edge
  and Firefox expose the suggestions to NVDA; Safari support is weaker.
- Screen reader testing was NVDA + Chrome only. Not tested with JAWS,
  VoiceOver or Firefox.
- Zoom and 320 px checks were done in Chrome only.
- Sign-in is a "sign in as" picker with no password, by the brief's ground
  rules, so no real authentication flow was tested for accessibility.
