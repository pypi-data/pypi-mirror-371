
# 🗑️ Junk - Universal Cleanup Executor

A zero-friction Python CLI tool for automated cleanup of unwanted files and directories.

## 🚀 The Problem

You have repositories filled with junk files and folders:
- `/target/`
- `*.log` files
- `__pycache__/`
- `/temp/` directories
- Build artifacts
- Cache files

Manually deleting these is annoying, and you want an automated executor that works universally across any project.

## ✨ The Solution

**Junk** is a PyPI-distributed CLI tool that provides one-shot cleanup with zero approvals or prompts.

Simply run:
```bash
junk
```

The tool:
1. 🔍 Looks for a `junk.fat` file in the current directory
2. 📝 Reads the list of unwanted files/folders
3. 🗑️ Deletes everything listed
4. 🧹 Self-destructs (`junk.fat` is removed after successful cleanup)

## 📦 Installation

Install from PyPI:
```bash
pip install junk-remover-cli
```

Then use anywhere:
```bash
junk
```

## 📋 Usage

1. **Create a `junk.fat` file** in your project root with files/folders to delete:
   ```
   /target/
   /Server/plotter/output/main.png
   /Server/temp/arch.json
   __pycache__/
   *.log
   node_modules/
   .DS_Store
   ```

2. **Run the cleanup**:
   ```bash
   junk
   ```

3. **Done!** All listed items are deleted, and `junk.fat` removes itself.

## 🎯 Key Features

- ✅ **Zero prompts** - No confirmations, just executes
- ✅ **Universal** - Works in any directory with a `junk.fat` file  
- ✅ **Self-cleanup** - Removes `junk.fat` after successful execution
- ✅ **Error handling** - Keeps `junk.fat` if some deletions fail
- ✅ **Cross-platform** - Works on Windows, macOS, and Linux
- ✅ **Encoding aware** - Handles different file encodings automatically

## 🔧 Behavior

- **Success case**: All items deleted → `junk.fat` is removed
- **Partial failure**: Some items couldn't be deleted → `junk.fat` is preserved for retry
- **No `junk.fat`**: Exits gracefully with informative message

## 🤖 AI Integration

This tool is designed to work perfectly with AI code assistants:
- **AI generates** the `junk.fat` file with project-specific junk patterns
- **Junk executes** the cleanup without any human intervention
- **Universal workflow** across different projects and languages

## 🛠️ Examples

### Web Development Project
```
node_modules/
dist/
.cache/
*.log
.DS_Store
```

### Python Project  
```
__pycache__/
*.pyc
.pytest_cache/
build/
*.egg-info/
```

### Java Project
```
target/
*.class
*.jar
*.war
```

## 🔒 Safety

- Only deletes what's explicitly listed in `junk.fat`
- No wildcards or pattern matching (what you list is what gets deleted)
- Skips non-existent files/folders gracefully
- Provides clear feedback on what was deleted

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions welcome! This tool is intentionally simple and focused. Please ensure any changes maintain the core principle: **zero-friction cleanup execution**.

---

*Make cleanup universal. Make it automatic. Make it simple.*