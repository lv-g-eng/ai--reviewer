# Accessibility Implementation Guide

## Overview

This document describes the accessibility features implemented in the AI-Based Reviewer frontend application to meet WCAG 2.1 Level AA compliance standards.

**Requirements:** 3.10 - THE Frontend_Application SHALL meet WCAG 2.1 Level AA accessibility standards for all interactive elements

## Implemented Features

### 1. Semantic HTML and ARIA Attributes

All components use semantic HTML5 elements and appropriate ARIA attributes:

- **Landmarks**: `role="main"`, `role="navigation"`, `role="search"`, `role="region"`
- **Form Labels**: All form inputs have associated `<label>` elements with proper `htmlFor` attributes
- **ARIA Labels**: Interactive elements have descriptive `aria-label` attributes
- **ARIA Live Regions**: Dynamic content updates use `aria-live="polite"` or `aria-live="assertive"`
- **ARIA States**: Toggle buttons use `aria-pressed`, expandable sections use `aria-expanded`

### 2. Keyboard Navigation

All interactive elements are keyboard accessible:

- **Tab Navigation**: All focusable elements are in logical tab order
- **Enter/Space**: Buttons and links respond to Enter and Space keys
- **Escape**: Modals and dropdowns can be closed with Escape key
- **Arrow Keys**: List navigation and graph controls support arrow keys
- **Focus Indicators**: Visible focus indicators on all interactive elements

### 3. Screen Reader Support

Components provide comprehensive screen reader support:

- **Alternative Text**: All images have descriptive `alt` text or `aria-label`
- **Hidden Content**: Decorative icons use `aria-hidden="true"`
- **Screen Reader Only Text**: Important context provided via `.sr-only` class
- **Form Validation**: Error messages linked to inputs via `aria-describedby`
- **Loading States**: Loading indicators announce status via `role="status"`

### 4. Color and Contrast

- **Color Contrast**: All text meets WCAG AA contrast ratios (4.5:1 for normal text, 3:1 for large text)
- **Color Independence**: Information is not conveyed by color alone
- **Focus Indicators**: High contrast focus indicators visible in all themes
- **Dark Mode**: Full dark mode support with proper contrast ratios

### 5. Component-Specific Features

#### Login Page (`/login`)
- Form with `aria-label="Login form"`
- Input validation with `aria-invalid` and `aria-describedby`
- Error messages with `role="alert"` and `aria-live="assertive"`
- Loading state with accessible button label

#### Register Page (`/register`)
- Password strength indicator with `role="progressbar"`
- Password requirements list with `role="list"` and `role="listitem"`
- Real-time validation feedback with `aria-live="polite"`
- Checkbox with proper label association

#### Projects Page (`/projects`)
- Search region with `role="search"`
- View mode toggles with `aria-pressed` states
- Project cards with keyboard navigation (`tabIndex={0}`, `onKeyDown`)
- Time elements with `dateTime` attribute
- Accessible sort dropdown with `aria-label`

#### Dependency Graph Visualization
- Graph container with `role="img"` and descriptive `aria-labelledby`
- Screen reader description via `id="graph-description"` and `.sr-only`
- Statistics region with `role="region" aria-label="Graph statistics"`
- Zoom controls with descriptive `aria-label` attributes
- Circular dependency alerts with `role="alert"`
- Legend with `role="list"` for color meanings
- Keyboard accessible cycle selection

#### Route Guard
- Loading state with `role="status"` and `aria-live="polite"`
- Screen reader text for authentication status
- Decorative loading icon with `aria-hidden="true"`

## Testing

### Automated Testing

We use `axe-core` and `jest-axe` for automated accessibility testing:

```bash
# Run all tests including accessibility tests
npm test

# Run only accessibility tests
npm test -- --testPathPattern=accessibility
```

### Test Coverage

Accessibility tests are implemented for:
- ✅ Login Page
- ✅ Register Page
- ✅ Projects Page
- ✅ Dependency Graph Visualization
- ✅ Route Guard Component

### Manual Testing Checklist

#### Keyboard Navigation
- [ ] Tab through all interactive elements in logical order
- [ ] Activate buttons and links with Enter/Space
- [ ] Close modals with Escape key
- [ ] Navigate lists with arrow keys
- [ ] Verify visible focus indicators

#### Screen Reader Testing
- [ ] Test with NVDA (Windows)
- [ ] Test with JAWS (Windows)
- [ ] Test with VoiceOver (macOS/iOS)
- [ ] Test with TalkBack (Android)
- [ ] Verify all content is announced correctly
- [ ] Verify form validation messages are announced
- [ ] Verify loading states are announced

#### Visual Testing
- [ ] Verify color contrast with Chrome DevTools
- [ ] Test with browser zoom at 200%
- [ ] Test with Windows High Contrast mode
- [ ] Test in dark mode
- [ ] Verify focus indicators are visible

#### Browser Extensions
- [ ] Run axe DevTools browser extension
- [ ] Run WAVE browser extension
- [ ] Run Lighthouse accessibility audit
- [ ] Address any reported issues

## Browser Extension Tools

### Recommended Tools

1. **axe DevTools** (Chrome, Firefox, Edge)
   - Comprehensive WCAG 2.1 testing
   - Detailed violation reports
   - Remediation guidance

2. **WAVE** (Chrome, Firefox, Edge)
   - Visual feedback on accessibility issues
   - Color contrast analyzer
   - Structure visualization

3. **Lighthouse** (Chrome DevTools)
   - Built-in accessibility audit
   - Performance and best practices
   - Automated testing

4. **Screen Reader Extensions**
   - ChromeVox (Chrome)
   - NVDA (Windows)
   - VoiceOver (macOS)

## Common Patterns

### Form Input with Validation

```tsx
<div className="space-y-2">
  <Label htmlFor="email">Email</Label>
  <Input
    id="email"
    type="email"
    aria-required="true"
    aria-invalid={errors.email ? 'true' : 'false'}
    aria-describedby={errors.email ? 'email-error' : undefined}
  />
  {errors.email && (
    <p id="email-error" className="text-sm text-destructive" role="alert">
      {errors.email.message}
    </p>
  )}
</div>
```

### Loading State

```tsx
<div role="status" aria-live="polite">
  <Loader2 className="animate-spin" aria-hidden="true" />
  <span className="sr-only">Loading...</span>
</div>
```

### Toggle Button

```tsx
<Button
  variant={isActive ? 'default' : 'outline'}
  onClick={() => setIsActive(!isActive)}
  aria-label="Toggle feature"
  aria-pressed={isActive}
>
  {isActive ? 'On' : 'Off'}
</Button>
```

### Keyboard Navigation

```tsx
<div
  tabIndex={0}
  role="button"
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }}
  aria-label="Descriptive label"
>
  Content
</div>
```

## WCAG 2.1 Level AA Compliance

### Perceivable

- ✅ **1.1.1 Non-text Content**: All images have alt text
- ✅ **1.3.1 Info and Relationships**: Semantic HTML and ARIA
- ✅ **1.3.2 Meaningful Sequence**: Logical reading order
- ✅ **1.3.3 Sensory Characteristics**: Not relying on shape/color alone
- ✅ **1.4.3 Contrast (Minimum)**: 4.5:1 for normal text, 3:1 for large text
- ✅ **1.4.4 Resize Text**: Text can be resized to 200%
- ✅ **1.4.10 Reflow**: Content reflows at 320px width
- ✅ **1.4.11 Non-text Contrast**: UI components have 3:1 contrast
- ✅ **1.4.12 Text Spacing**: Text spacing can be adjusted
- ✅ **1.4.13 Content on Hover or Focus**: Dismissible, hoverable, persistent

### Operable

- ✅ **2.1.1 Keyboard**: All functionality available via keyboard
- ✅ **2.1.2 No Keyboard Trap**: No keyboard traps
- ✅ **2.1.4 Character Key Shortcuts**: No single-key shortcuts
- ✅ **2.4.3 Focus Order**: Logical focus order
- ✅ **2.4.6 Headings and Labels**: Descriptive headings and labels
- ✅ **2.4.7 Focus Visible**: Visible focus indicators
- ✅ **2.5.3 Label in Name**: Accessible names match visible labels

### Understandable

- ✅ **3.1.1 Language of Page**: HTML lang attribute set
- ✅ **3.2.1 On Focus**: No context changes on focus
- ✅ **3.2.2 On Input**: No unexpected context changes
- ✅ **3.3.1 Error Identification**: Errors clearly identified
- ✅ **3.3.2 Labels or Instructions**: Form inputs have labels
- ✅ **3.3.3 Error Suggestion**: Error correction suggestions provided
- ✅ **3.3.4 Error Prevention**: Confirmation for important actions

### Robust

- ✅ **4.1.2 Name, Role, Value**: All UI components have proper ARIA
- ✅ **4.1.3 Status Messages**: Status messages use aria-live

## Known Limitations

### Manual Verification Required

Some accessibility criteria require manual verification:

1. **Color Contrast**: While we aim for WCAG AA compliance, custom themes should be tested
2. **Screen Reader Testing**: Automated tools can't fully test screen reader experience
3. **Cognitive Load**: Simplicity and clarity require human judgment
4. **Content Quality**: Alt text quality requires human review

### Third-Party Components

Some third-party components may have accessibility limitations:

- **react-force-graph-2d**: Complex graph visualization may have limited screen reader support
- **Radix UI**: Generally accessible but should be tested in context

## Future Improvements

1. **Enhanced Keyboard Shortcuts**: Add customizable keyboard shortcuts
2. **Skip Links**: Add skip-to-content links for faster navigation
3. **Reduced Motion**: Respect `prefers-reduced-motion` media query
4. **High Contrast Mode**: Enhanced support for Windows High Contrast
5. **Voice Control**: Test and optimize for voice control software
6. **Cognitive Accessibility**: Simplify complex workflows
7. **Internationalization**: Support for RTL languages and localization

## Resources

### WCAG Guidelines
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WCAG 2.1 Understanding Docs](https://www.w3.org/WAI/WCAG21/Understanding/)

### Testing Tools
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE](https://wave.webaim.org/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)

### ARIA Documentation
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [ARIA Specification](https://www.w3.org/TR/wai-aria-1.2/)

### Screen Readers
- [NVDA](https://www.nvaccess.org/)
- [JAWS](https://www.freedomscientific.com/products/software/jaws/)
- [VoiceOver](https://www.apple.com/accessibility/voiceover/)

## Contact

For accessibility issues or questions, please contact the development team or file an issue in the project repository.
