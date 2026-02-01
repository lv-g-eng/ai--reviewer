# Frontend Build Fix Guide

## Current Status
The frontend has TypeScript compilation errors due to unused imports and variables. These are being fixed systematically.

## Quick Fix

### Option 1: Disable Strict Type Checking (Temporary)
```bash
cd frontend
# Edit tsconfig.json and set:
# "noUnusedLocals": false,
# "noUnusedParameters": false,
npm run build
```

### Option 2: Fix All Errors (Recommended)
Run the automated fix script:
```bash
cd frontend
npm run build 2>&1 | findstr "Type error" > errors.txt
# Then fix each error manually or use the script below
```

## Common Errors and Fixes

### 1. Unused Imports
**Error:** `'X' is declared but its value is never read`

**Fix:** Remove the unused import
```typescript
// Before
import { A, B, C } from 'module';

// After (if B is unused)
import { A, C } from 'module';
```

### 2. Unused Variables
**Error:** `'setX' is declared but its value is never read`

**Fix:** Use underscore or remove
```typescript
// Before
const [value, setValue] = useState();

// After (if setValue is unused)
const [value] = useState();
// or
const [value, _setValue] = useState();
```

### 3. Module Type Errors
**Error:** `Cannot find module 'X/dist/types'`

**Fix:** Import from main module
```typescript
// Before
import { Type } from 'module/dist/types';

// After
import { Type } from 'module';
```

## Automated Fix Script

Create `fix-build.ps1`:
```powershell
# Fix unused imports
$files = Get-ChildItem -Path src -Recurse -Filter *.tsx

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    
    # Remove unused imports (add patterns as needed)
    $content = $content -replace ', Database,', ','
    $content = $content -replace 'const \[(\w+), set\1\] = useState', 'const [$1] = useState'
    
    Set-Content $file.FullName $content
}
```

## Files with Known Issues

1. `src/components/visualizations/ArchitectureGraph.tsx` - Unused Database import
2. `src/components/architecture/architecture-graph.tsx` - Unused setNodes
3. `src/components/charts/gauge-chart.tsx` - Unused color parameter
4. `src/components/common/backend-status.tsx` - Unused CheckCircle2
5. `src/components/reviews/comment-filters.tsx` - Unused Select imports
6. `src/components/theme-provider.tsx` - Wrong import path

## Build Process

```bash
cd frontend

# 1. Clean
Remove-Item -Recurse -Force .next

# 2. Install
npm install

# 3. Build
npm run build

# 4. If successful, start
npm run dev
```

## Temporary Workaround

Edit `frontend/tsconfig.json`:
```json
{
  "compilerOptions": {
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "strict": false
  }
}
```

Then rebuild:
```bash
npm run build
```

## Production Fix

For production, all unused imports/variables should be properly removed rather than disabling type checking.

## Status

- ✅ Fixed: NextAuth route types
- ✅ Fixed: Zod error handling
- ✅ Fixed: ESLint configuration
- ✅ Fixed: theme-provider import
- ✅ Fixed: comment-filters unused imports
- ✅ Fixed: backend-status unused import
- ✅ Fixed: gauge-chart unused parameter
- ✅ Fixed: architecture-graph unused Edge import
- 🔄 In Progress: ArchitectureGraph.tsx Database import
- 🔄 In Progress: Other minor unused imports

## Next Steps

1. Fix remaining unused imports in ArchitectureGraph.tsx
2. Run full build test
3. Start dev server
4. Test all pages for runtime errors
