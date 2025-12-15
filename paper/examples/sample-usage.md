# Sample Usage Examples

This document provides concrete examples of using the paper writing tools.

## Example 1: Related Work Writing

### Scenario
You're writing a paper on "Federated Learning for Healthcare Applications" and need to write the related work section.

### Step-by-Step Usage

#### 1. Invoke the Tool
From Claude Code: Load the paper skill and select "Related Work Writing"

#### 2. Provide Context
```
Research Topic: Federated Learning for Healthcare Applications
Key Contribution: A privacy-preserving federated learning framework
                  that handles heterogeneous medical data across hospitals
                  while maintaining HIPAA compliance
Target Venue: IEEE Journal of Biomedical and Health Informatics
```

#### 3. Tool Suggests Organization
The tool suggests a **Categorical/Thematic** organization:

```
1. Federated Learning Fundamentals
2. Privacy-Preserving Machine Learning in Healthcare
3. Handling Data Heterogeneity in Federated Settings
4. Regulatory Compliance in Medical ML Systems
5. Healthcare Applications of Federated Learning
```

#### 4. Generated Outline Example
```markdown
## Related Work

### Federated Learning Fundamentals
- McMahan et al. (2017): FederatedAveraging algorithm
- Li et al. (2020): FedProx for heterogeneous settings
- Kairouz et al. (2021): Comprehensive survey

### Privacy-Preserving ML in Healthcare
- Sheller et al. (2020): Multi-institutional deep learning
- Kaissis et al. (2020): Privacy-preserving techniques
- Differential privacy approaches: [Paper A, Paper B]

[Continue for other sections...]

### Research Gap
While existing work addresses [X] and [Y], no current approach
combines privacy preservation with heterogeneous medical data
handling while ensuring regulatory compliance. Our work fills
this gap by [brief description].
```

#### 5. Draft Text Generation
The tool helps write each section with proper flow and citations.

---

## Example 2: LaTeX Project Validation

### Scenario
You have a paper draft and want to check for errors before submission.

### Project Structure
```
my-paper/
├── main.tex
├── introduction.tex
├── related_work.tex
├── methodology.tex
├── experiments.tex
├── conclusion.tex
├── references.bib
└── figures/
    ├── architecture.pdf
    └── results.pdf
```

### Running the Checker

#### Option A: Interactive (via Claude Code)
```
1. Invoke the paper skill
2. Select "LaTeX Validation"
3. Provide project path: /path/to/my-paper
4. Provide main file: main.tex
5. Select compiler: pdflatex
6. Review interactive report
```

#### Option B: Command Line Scripts
```bash
cd paper/latex-checker/scripts

# Full compilation check
./compile-check.sh /path/to/my-paper main.tex pdflatex

# Output:
# =========================================
# LaTeX Compilation Check
# =========================================
# Project: /path/to/my-paper
# Main file: main.tex
# Compiler: pdflatex
# =========================================
# ...
# COMPILATION: SUCCESS
# Errors: 0
# Warnings: 3
# Undefined references: 0
# Undefined citations: 0
# Overfull hboxes: 5

# Check typos
./check-typos.sh /path/to/my-paper

# Output saved to: typo_report.txt

# Check structure
./check-structure.sh /path/to/my-paper

# Output saved to: structure_report.txt
```

### Sample Report Output

#### compilation_summary.txt
```
LaTeX Compilation Summary
========================
Project: /path/to/my-paper
Main file: main.tex
Compiler: pdflatex
Status: SUCCESS

Errors: 0
Warnings: 3
Undefined references: 0
Undefined citations: 0
Overfull hboxes: 5

For detailed output, see:
- compile_pass1.log
- compile_pass2.log
- compile_pass3.log
- main.log
```

#### typo_report.txt (excerpt)
```
LaTeX Typo & Mistake Report
==========================
Project: /path/to/my-paper
Date: 2025-12-15

=== COMMON TYPOS ===

[WARNING] Typo: 'can not' should be 'cannot'
methodology.tex:42: We can not assume that all hospitals...

[WARNING] Typo: 'seperate' should be 'separate'
related_work.tex:78: These approaches seperate the training...

=== LATEX ISSUES ===

[WARNING] Bare URL: Use \url{} or \href{}
introduction.tex:15: See https://example.com for more details

=== CITATION STYLE ===

Citation command usage:
  \cite: 45
  \citep: 12
  \citet: 3

[INFO] Mixed citation styles: \cite and \citep
Consider using consistent citation commands throughout.
```

#### structure_report.txt (excerpt)
```
LaTeX Structure & Syntax Report
==============================
Project: /path/to/my-paper
Date: 2025-12-15

=== FILE INVENTORY ===
LaTeX files (.tex): 6
Bibliography files (.bib): 1
Figure directories found

Files:
main.tex
introduction.tex
related_work.tex
methodology.tex
experiments.tex
conclusion.tex

=== SYNTAX CHECKS ===

Checking: main.tex
---
[INFO] Document structure looks good

Checking: experiments.tex
---
[WARNING] experiments.tex:123: Figure without \label (consider adding for referencing)

=== GRAPHICS CHECK ===
[ERROR] experiments.tex: Referenced graphic not found: figures/missing_plot.pdf

=== SUMMARY ===
Errors: 1
Warnings: 1

[RED] Found 1 errors and 1 warnings. Please fix errors before compiling.
```

---

## Example 3: Common Issues and Fixes

### Issue 1: Unmatched Environments

**Reported:**
```
[ERROR] methodology.tex: Unmatched environment 'equation' (begin: 3, end: 2)
```

**Fix:**
Check methodology.tex for a missing `\end{equation}`. Add it:
```latex
\begin{equation}
  f(x) = \sum_{i=1}^{n} w_i x_i
\end{equation}  % <-- This was missing
```

### Issue 2: Undefined Reference

**Reported:**
```
[ERROR] Undefined references found in main.log
LaTeX Warning: Reference `fig:architecture' on page 5 undefined.
```

**Fix:**
Either add the label in the figure:
```latex
\begin{figure}
  \includegraphics{figures/architecture.pdf}
  \caption{System architecture}
  \label{fig:architecture}  % <-- Add this
\end{figure}
```

Or fix the reference:
```latex
See Figure~\ref{fig:system-architecture}  % <-- Use correct label
```

### Issue 3: Citation Style Inconsistency

**Reported:**
```
[INFO] Mixed citation styles: \cite and \citep
```

**Fix:**
Choose one style and convert all citations:

**Before:**
```latex
Recent work \cite{smith2020} has shown...
Another approach \citep{jones2021} demonstrated...
```

**After (using \citep consistently):**
```latex
Recent work \citep{smith2020} has shown...
Another approach \citep{jones2021} demonstrated...
```

### Issue 4: Wrong Quotes

**Reported:**
```
[WARNING] Wrong quotes: Use `` and '' instead of "
introduction.tex:23: The "federated learning" approach...
```

**Fix:**
```latex
% Before
The "federated learning" approach...

% After
The ``federated learning'' approach...
```

### Issue 5: Bare URL

**Reported:**
```
[WARNING] Bare URL: Use \url{} or \href{}
introduction.tex:45: Visit https://github.com/project for code
```

**Fix:**
```latex
% Before
Visit https://github.com/project for code

% After
Visit \url{https://github.com/project} for code

% Or with hyperref:
Visit our \href{https://github.com/project}{code repository} for implementation
```

---

## Example 4: Typical Workflow

### Complete Paper Writing Workflow

```
1. INITIAL DRAFT
   ├─ Write introduction and methodology manually
   ├─ Use Related Work Writer to create related work section
   └─ Write experiments and conclusion

2. FIRST CHECK
   ├─ Run: ./compile-check.sh
   ├─ Fix: Any compilation errors
   └─ Verify: Paper compiles successfully

3. STRUCTURE VALIDATION
   ├─ Run: ./check-structure.sh
   ├─ Review: Unmatched environments, missing labels
   └─ Fix: Structural issues

4. CONTENT REFINEMENT
   ├─ Run: ./check-typos.sh
   ├─ Review: Spelling, word usage, style
   └─ Fix: Typos and common mistakes

5. FINAL COMPILATION
   ├─ Run: ./compile-check.sh again
   ├─ Verify: 0 errors, minimal warnings
   └─ Review: PDF output

6. SUBMISSION PREP
   ├─ Fix: Any remaining warnings
   ├─ Verify: All figures present
   └─ Check: Citation consistency
```

### Time Estimates

| Task | Manual | With Tools | Savings |
|------|--------|------------|---------|
| Related work writing | 4-6 hours | 2-3 hours | ~50% |
| Finding LaTeX errors | 1-2 hours | 10-15 min | ~85% |
| Typo checking | 2-3 hours | 15-20 min | ~85% |
| Structure validation | 1 hour | 5-10 min | ~90% |
| **Total** | **8-12 hours** | **3-4 hours** | **~65%** |

---

## Example 5: Advanced Usage

### Batch Processing Multiple Papers

```bash
#!/bin/bash
# check-all-papers.sh

PAPERS_DIR="/path/to/papers"

for paper in "$PAPERS_DIR"/*; do
    if [ -d "$paper" ]; then
        echo "Checking: $paper"

        # Find main .tex file
        main_file=$(find "$paper" -name "main.tex" -o -name "paper.tex" | head -1)

        if [ ! -z "$main_file" ]; then
            # Run all checks
            ./compile-check.sh "$paper" "$(basename $main_file)"
            ./check-typos.sh "$paper"
            ./check-structure.sh "$paper"

            # Collect results
            mkdir -p "$paper/check-reports"
            mv "$paper"/*.txt "$paper/check-reports/" 2>/dev/null || true
        fi
    fi
done
```

### Custom Typo Dictionary

Extend `check-typos.sh` with your domain-specific terms:

```bash
# Add to check-typos.sh after line 50:

# Domain-specific checks for ML papers
check_pattern '\bneural networks\b' "Consider: 'neural network' (singular) or verify plural usage" "INFO" "*.tex"
check_pattern '\bmachine learning\b' "Verify capitalization: Machine Learning vs machine learning" "INFO" "*.tex"
```

### Continuous Integration

Add to your `.github/workflows/check-latex.yml`:

```yaml
name: LaTeX Check

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install LaTeX
        run: sudo apt-get install texlive-full
      - name: Run checks
        run: |
          cd paper/latex-checker/scripts
          ./compile-check.sh $GITHUB_WORKSPACE/paper main.tex
          ./check-typos.sh $GITHUB_WORKSPACE/paper
          ./check-structure.sh $GITHUB_WORKSPACE/paper
```

---

## Tips for Best Results

1. **Run checks frequently**: Don't wait until the end
2. **Fix errors first**: Then warnings, then info items
3. **Learn from patterns**: Common mistakes will decrease over time
4. **Customize for your field**: Add domain-specific checks
5. **Combine tools**: Use related work writer's output with LaTeX checker
6. **Version control**: Commit after fixing each category of issues
7. **Peer review**: Tools complement, not replace, human review

---

## Getting Help

If you encounter issues:

1. Check that scripts have execute permissions: `chmod +x *.sh`
2. Verify LaTeX installation: `pdflatex --version`
3. Check file paths are correct (use absolute paths)
4. Review the generated log files for details
5. Consult the main README.md for troubleshooting

For more examples and updates, see the project repository.
