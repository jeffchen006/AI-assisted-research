# Quick Start Guide

Get started with paper writing tools in under 5 minutes.

## What You Get

Two powerful tools to accelerate paper writing:

1. **Related Work Writer**: AI assistant for writing comprehensive related work sections
2. **LaTeX Checker**: Automated validation for LaTeX projects (errors, typos, structure)

## Installation

Already done! Just ensure you have:
- Claude Code installed ✓
- LaTeX distribution (for LaTeX checker)

```bash
# Verify LaTeX is installed (optional, only for LaTeX checker)
pdflatex --version
```

## Quick Start Option 1: Interactive (Recommended)

### For Related Work Writing

```bash
# From Claude Code CLI, invoke the paper skill
# The skill will ask which tool you want to use
# Select: "Related Work Writing"

# Follow the interactive prompts:
# 1. Describe your research topic
# 2. Explain your key contribution
# 3. Choose organization strategy
# 4. Get structured outline and draft
```

### For LaTeX Checking

```bash
# From Claude Code CLI, invoke the paper skill
# Select: "LaTeX Validation"

# Provide:
# 1. Path to your LaTeX project
# 2. Main .tex file name
# 3. Compiler (usually pdflatex)

# Get comprehensive report with:
# - Compilation status
# - Errors and warnings
# - Typos and suggestions
# - Structure issues
```

## Quick Start Option 2: Direct Scripts

For LaTeX checking only:

```bash
cd /Users/jeffchen/Documents/AI-assisted-research/paper/latex-checker/scripts

# Run all checks at once:
./compile-check.sh /path/to/paper main.tex
./check-typos.sh /path/to/paper
./check-structure.sh /path/to/paper

# Review generated reports in your paper directory:
# - compilation_summary.txt
# - typo_report.txt
# - structure_report.txt
```

## 5-Minute Test Drive

### Test the LaTeX Checker (2 minutes)

```bash
# Create a simple test document
mkdir ~/test-paper
cd ~/test-paper

cat > main.tex <<'EOF'
\documentclass{article}
\begin{document}
\section{Introduction}
This is a test with alot of typos and "wrong quotes".
See Figure~\ref{fig:missing}.
\end{document}
EOF

# Run the checker
cd /Users/jeffchen/Documents/AI-assisted-research/paper/latex-checker/scripts
./check-structure.sh ~/test-paper
./check-typos.sh ~/test-paper

# You'll see:
# ✓ Compilation issues detected
# ✓ Typos found ("alot" → "a lot")
# ✓ Quote issues found
# ✓ Undefined reference found (fig:missing)
```

### Test the Related Work Writer (3 minutes)

From Claude Code:
1. Invoke the paper skill
2. Choose "Related Work Writing"
3. Enter a simple research topic: "Deep Learning for Image Classification"
4. See how it generates a structured outline with categories

## Common First-Time Issues

### Issue 1: Scripts not executable
```bash
chmod +x /Users/jeffchen/Documents/AI-assisted-research/paper/latex-checker/scripts/*.sh
```

### Issue 2: LaTeX not found
```bash
# macOS:
brew install --cask mactex

# Linux:
sudo apt-get install texlive-full
```

### Issue 3: Path not found
Use absolute paths, not relative:
```bash
# ❌ Wrong:
./compile-check.sh ../my-paper main.tex

# ✓ Correct:
./compile-check.sh /full/path/to/my-paper main.tex
```

## Your First Real Paper

### Step 1: Prepare Your Paper
Gather:
- Research topic and contribution description
- List of important papers to cite (optional)
- Your existing LaTeX project (if checking)

### Step 2: Write Related Work
1. Invoke paper skill → Related Work Writing
2. Answer the interactive questions
3. Get structured outline
4. Get draft text with citations
5. Copy to your paper and refine

**Time saved**: 2-3 hours

### Step 3: Check Your LaTeX
1. Run all three check scripts on your paper
2. Review the three report files
3. Fix errors (red) first
4. Then warnings (yellow)
5. Finally review suggestions (blue/info)
6. Re-run to verify

**Time saved**: 1-2 hours

### Step 4: Iterate
- Re-run checks after major changes
- Use Related Work Writer for other papers
- Scripts work for any paper, any field

## What's Next?

### Learn More
- Read `README.md` for comprehensive documentation
- Check `examples/sample-usage.md` for detailed examples
- Review templates in `related-work/templates/`

### Customize
- Add your domain-specific typo patterns to `check-typos.sh`
- Modify templates for your field's conventions
- Create custom checks in the scripts

### Integrate
- Add to your CI/CD pipeline
- Create aliases for quick access
- Batch process multiple papers

## Pro Tips

1. **Run checks frequently**: After each writing session, not just at the end
2. **Start with structure**: Use Related Work Writer early in paper writing
3. **Fix in order**: Errors → Warnings → Info
4. **Learn patterns**: Common mistakes will decrease over time
5. **Combine tools**: Write related work, then validate with LaTeX checker

## Getting Help

- Full documentation: See `README.md`
- Detailed examples: See `examples/sample-usage.md`
- Skill instructions: See `related-work/skill-prompt.md` and `latex-checker/skill-prompt.md`
- Templates: See `related-work/templates/`

## Quick Reference Card

```
┌─────────────────────────────────────────────┐
│ PAPER WRITING TOOLS                         │
├─────────────────────────────────────────────┤
│ Related Work Writer                         │
│ • Interactive AI assistant                  │
│ • Invoke via Claude Code paper skill        │
│ • Provides structure, outline, draft        │
│                                             │
│ LaTeX Checker                               │
│ • Compilation: compile-check.sh             │
│ • Typos: check-typos.sh                     │
│ • Structure: check-structure.sh             │
│ • Reports: *.txt in project dir             │
│                                             │
│ All scripts location:                       │
│ paper/latex-checker/scripts/                │
└─────────────────────────────────────────────┘
```

---

You're ready! Start with the test drive above, then try on your real paper.
