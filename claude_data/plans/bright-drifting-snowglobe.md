# Lean Docs Syntax Highlighter - Safari Extension

## Goal
Create a Safari Web Extension that adds dark mode and syntax highlighting to the Lean language reference documentation at lean-lang.org/doc/reference.

## Key Findings

**Existing Infrastructure**: The Lean docs already output semantic CSS classes via Verso/SubVerso:
- `.hl.lean` - main code wrapper
- `.keyword` - language keywords (structure, where, def, etc.)
- `.const` - constants and constructors
- `.var` - variables
- `.literal` - string/numeric literals
- `.sort` - sort specifications
- `.token` - individual syntax tokens

The classes exist but have minimal color styling on the production site. We just need to inject CSS that applies colors and dark background.

## Implementation

### 1. Create Extension Directory Structure
```
LeanDocsHighlighter/
├── Resources/
│   ├── manifest.json      # Extension manifest (v3)
│   ├── content.css        # Dark theme + syntax highlighting
│   ├── icon-48.png        # Extension icons
│   ├── icon-96.png
│   └── icon-128.png
└── README.md              # Build/install instructions
```

### 2. manifest.json
- Target URLs: `https://lean-lang.org/doc/reference/*`
- Inject `content.css` at document_start
- Manifest v3 format for Safari compatibility

### 3. content.css - Core Styling

**Dark Mode Base:**
- Background: `#1e1e1e` (VS Code dark style)
- Text: `#d4d4d4`
- Code blocks: slightly lighter background for contrast

**Syntax Highlighting (matching live.lean-lang.org):**
- `.keyword`: blue (`#569cd6`)
- `.const`: yellow/gold (`#dcdcaa`)
- `.var`: light blue (`#9cdcfe`)
- `.literal`: orange (`#ce9178`)
- `.sort`: green (`#4ec9b0`)

**Additional polish:**
- Smooth transitions for hover states
- Preserve interactive features (tooltips, tactic toggles)
- Style error/warning messages appropriately

### 4. Generate Icons
Create simple Lean-themed icons (blue "L" or similar) at 48x48, 96x96, 128x128.

### 5. Xcode Project Setup (for Safari)

Safari Web Extensions require an Xcode wrapper:

1. Open Xcode → File → New → Project
2. Select "Safari Extension App"
3. Name: "Lean Docs Highlighter"
4. Replace generated Resources/ with our files
5. Build and run (cmd+R)
6. Enable in Safari → Settings → Extensions

For personal use, you can run in development mode without Apple Developer signing.

## Files to Create

| File | Purpose |
|------|---------|
| `Resources/manifest.json` | Extension configuration |
| `Resources/content.css` | Dark theme + highlighting (~150 lines) |
| `Resources/icon-*.png` | Extension icons (3 sizes) |
| `README.md` | Xcode setup instructions |

## Maintenance

Once installed, the extension auto-applies to all Lean docs pages. No maintenance needed unless:
- Lean team changes their CSS class names (unlikely - they're semantic)
- You want to tweak colors

## Alternative Considered

Userscripts (via apps like "Userscripts for Safari" from App Store) would be simpler but you specified a proper extension.
