# SuperClaude Installation Guide 📦

SuperClaude installs behavioral context files that Claude Code reads to enhance its capabilities with 21 commands, 14 agents, and 5 modes.

## Quick Start 🚀

**Python (Recommended):**
```bash
pip install SuperClaude
SuperClaude install
```

**NPM:**
```bash
npm install -g @bifrost_inc/superclaude
SuperClaude install
```

**Development:**
```bash
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework
pip install -e ".[dev]"
SuperClaude install --dry-run
```

## Command Types

| Type | Where Used | Format | Example |
|------|------------|--------|----------|
| **Installation** | Terminal | `SuperClaude [command]` | `SuperClaude install` |
| **Slash Commands** | Claude Code | `/sc:[command]` | `/sc:brainstorm "idea"` |
| **Agents** | Claude Code | `@agent-[type]` | `@agent-security "review"` |

## Requirements

**Required:**
- Python 3.8+ with pip
- Claude Code installed and working
- 50MB free space

**Optional:**
- Node.js 16+ (for MCP servers)
- Git (for version control integration)

## Quick Check
```bash
python3 --version    # Should be 3.8+
claude --version     # Verify Claude Code
node --version       # Optional: for MCP servers
```

## Installation Options 🎛️

**Interactive Installation (Default):**
```bash
SuperClaude install
```

**With Options:**
```bash
SuperClaude install --components core mcp modes  # Specific components
SuperClaude install --dry-run                    # Preview only
SuperClaude install --force --yes                # Skip confirmations
```

### Getting SuperClaude 📥

**Choose Your Preferred Method:**

**Python Users:**
```bash
pip install SuperClaude
```

**JavaScript/Node.js Users:**
```bash
npm install -g @bifrost_inc/superclaude
```

**Development/Contributors:**
```bash
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework
pip install -e ".[dev]"
```

### Running the Installer 🎬

**Interactive Installation (Default):**
```bash
SuperClaude install
```
The installer will:
1. Validate system requirements
2. Show available components
3. Install selected components to `~/.claude/`
4. Configure MCP servers if selected
5. Update CLAUDE.md with framework imports

## After Installation ✅

**Verify Installation:**
```bash
python3 -m SuperClaude --version    # Should show 4.0.4
SuperClaude install --list-components
```

**Test Commands:**
```bash
# In Claude Code, try:
/sc:brainstorm "test project"    # Should ask discovery questions
/sc:analyze README.md           # Should provide analysis
```

**What's Installed:**
- Framework files in `~/.claude/`
- 21 slash commands (`/sc:*`)
- 14 agents (`@agent-*`)
- 5 behavioral modes
- MCP server configurations (if selected)

## Managing Your Installation 🛠️

**Update:**
```bash
pip install --upgrade SuperClaude
SuperClaude update
```

**Backup & Restore:**
```bash
SuperClaude backup --create
SuperClaude backup --restore ~/.claude.backup.YYYYMMDD_HHMMSS
```

**Uninstall:**
```bash
SuperClaude uninstall
pip uninstall SuperClaude
```

## Troubleshooting 🔧

**Common Issues:**
- **Command not found**: Verify installation with `python3 -m SuperClaude --version`
- **Permission denied**: Use `pip install --user SuperClaude`
- **Claude Code not found**: Install from https://claude.ai/code

**Get Help:**
- [Troubleshooting Guide](../Reference/troubleshooting.md)
- [GitHub Issues](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues)

## Next Steps 🚀

- [Quick Start Guide](quick-start.md) - First commands and workflows
- [Commands Reference](../User-Guide/commands.md) - All 21 commands
- [Examples Cookbook](../Reference/examples-cookbook.md) - Real-world usage

## Prerequisites Setup 🛠️

**Missing Python?**
```bash
# Linux: sudo apt install python3 python3-pip
# macOS: brew install python3
# Windows: Download from python.org
```

**Missing Claude Code?**
- Download from https://claude.ai/code
- Verify with: `claude --version`

## What's Next? 🚀

1. [Quick Start Guide](quick-start.md) - Essential workflows
2. [Commands Reference](../User-Guide/commands.md) - All 21 commands  
3. [Examples Cookbook](../Reference/examples-cookbook.md) - Real-world usage

---

## Final Notes 📝

**Installation Summary:**

- **Space**: 50MB for full installation
- **Requirements**: Python 3.8+, Claude Code, 1GB RAM recommended
- **Platform**: Linux, macOS, Windows supported
- **Usage**: Immediate access to 21 commands and 5 behavioral modes

**What's Next**: Your Claude Code now has enhanced capabilities. Try `/sc:brainstorm` for your first SuperClaude experience!

---

## Related Guides

**Documentation Roadmap:**

**Beginner** (🌱 Start Here)
- [Quick Start Guide](quick-start.md) - quick setup guide
- [Commands Reference](../User-Guide/commands.md) - Basic usage

**Intermediate** (🌿 Growing)
- [Behavioral Modes](../User-Guide/modes.md) - Context optimization
- [MCP Servers](../User-Guide/mcp-servers.md) - Enhanced capabilities
- [Examples Cookbook](../Reference/examples-cookbook.md) - Practical patterns

**Advanced** (🌲 Expert)
- [Technical Architecture](../Developer-Guide/technical-architecture.md) - System design
- [Contributing Code](../Developer-Guide/contributing-code.md) - Development
- [Quick Start Guide](quick-start.md) - Essential workflows

---

**Installation Complete!** You now have access to 21 commands, 14 agents, and 5 behavioral modes. Try `/sc:brainstorm` in Claude Code to get started.