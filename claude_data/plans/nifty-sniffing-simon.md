# Theme Switcher Implementation Plan

## Overview

Add a 4-mode theme switcher to the Safari extension via radio buttons in the popup.

## Modes

| Mode | Value | Dark BG | Syntax Colors |
|------|-------|---------|---------------|
| Light | `light-regular` | No | No |
| Light + Syntax | `light-highlighting` | No | Yes |
| Dark | `dark-regular` | Yes | No |
| Dark + Syntax | `dark-highlighting` (DEFAULT) | Yes | Yes |

## Architecture

**CSS Strategy:** Use `data-theme` attribute on `<html>` element with CSS attribute selectors:
- `[data-theme^="dark"]` - matches both dark modes
- `[data-theme$="highlighting"]` - matches both highlighting modes
- `[data-theme="light-regular"]` - no styling applied (site as-is)

**Message Flow:**
```
popup.js → browser.tabs.sendMessage() → content.js → sets data-theme attribute
```

## Files to Modify

### 1. `content.css` (major restructure)

Wrap existing rules with attribute selectors:

```css
/* Dark backgrounds - only for dark modes */
html[data-theme^="dark"] body { ... }

/* Syntax highlighting - only for highlighting modes */
html[data-theme$="highlighting"] .keyword { ... }

/* Monochrome code - for regular modes */
html[data-theme$="regular"] .hl.lean * {
  color: inherit !important;
}

/* Light regular - no-op, site appears as-is */
```

### 2. `content.js`

```javascript
const DEFAULT_THEME = 'dark-highlighting';

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
}

// Apply default on load
applyTheme(DEFAULT_THEME);

// Listen for theme changes
browser.runtime.onMessage.addListener((request) => {
  if (request.action === 'applyTheme') {
    applyTheme(request.theme);
  }
});
```

### 3. `popup.html`

Replace "Hello World!" with radio button UI:

```html
<div class="theme-selector">
  <h2>Theme</h2>
  <label><input type="radio" name="theme" value="light-regular"> Light</label>
  <label><input type="radio" name="theme" value="light-highlighting"> Light + Syntax</label>
  <label><input type="radio" name="theme" value="dark-regular"> Dark</label>
  <label><input type="radio" name="theme" value="dark-highlighting" checked> Dark + Syntax</label>
</div>
```

### 4. `popup.js`

```javascript
const DEFAULT_THEME = 'dark-highlighting';

async function setTheme(theme) {
  const tabs = await browser.tabs.query({ active: true, currentWindow: true });
  if (tabs[0]) {
    browser.tabs.sendMessage(tabs[0].id, { action: 'applyTheme', theme });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelector(`input[value="${DEFAULT_THEME}"]`).checked = true;

  document.querySelectorAll('input[name="theme"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
      if (e.target.checked) setTheme(e.target.value);
    });
  });
});
```

### 5. `popup.css`

Style the radio button group with appropriate width, spacing, and dark mode support.

### 6. `background.js`

May need minor updates if direct popup→content messaging fails in Safari.

## Implementation Order

1. **content.js** - Add `applyTheme()` and message listener
2. **content.css** - Restructure with data-attribute scoping (largest change)
3. **popup.html** - Radio button UI
4. **popup.css** - Style the popup
5. **popup.js** - Theme selection logic
6. **Test** all 4 modes on all matched URLs

## Key Behaviors

- Default: `dark-highlighting` on every page load (no persistence)
- Theme changes apply immediately without page reload
- Each new page/tab starts fresh with default theme
