# akscmd

Natural language → shell command using Gemini.  
Works as:
- `akscmd "<create a folder named apple>"` → prints & (optionally) runs `mkdir apple`
- Optional shell hook so typing `<create a folder named apple>` and pressing **Enter** runs the command directly.

## Quick start
```bash
pip install akscmd
export AKSCMD_GEMINI_API_KEY="YOUR_KEY"
akscmd "<create a folder named apple>" --yes
