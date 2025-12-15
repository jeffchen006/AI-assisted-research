#!/bin/bash
# LaTeX Typo and Common Mistakes Checker
# Usage: ./check-typos.sh <project_dir>

PROJECT_DIR="${1:-.}"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "========================================="
echo "LaTeX Typo & Mistake Checker"
echo "========================================="
echo "Project: $PROJECT_DIR"
echo "========================================="

cd "$PROJECT_DIR"

# Check if any .tex files exist
if ! ls *.tex &> /dev/null; then
    echo -e "${RED}ERROR: No .tex files found${NC}"
    exit 1
fi

ISSUES_FOUND=0

# Create report file
REPORT="typo_report.txt"
> "$REPORT"

echo "LaTeX Typo & Mistake Report" >> "$REPORT"
echo "==========================" >> "$REPORT"
echo "Project: $PROJECT_DIR" >> "$REPORT"
echo "Date: $(date)" >> "$REPORT"
echo "" >> "$REPORT"

# Function to check pattern and report
check_pattern() {
    local pattern="$1"
    local description="$2"
    local severity="$3"
    local files="$4"

    local results=$(grep -n "$pattern" $files 2>/dev/null || true)

    if [ ! -z "$results" ]; then
        ISSUES_FOUND=$((ISSUES_FOUND + 1))

        echo "" | tee -a "$REPORT"
        if [ "$severity" = "ERROR" ]; then
            echo -e "${RED}[$severity] $description${NC}" | tee -a "$REPORT"
        else
            echo -e "${YELLOW}[$severity] $description${NC}" | tee -a "$REPORT"
        fi
        echo "$results" | tee -a "$REPORT"
    fi
}

echo ""
echo "Checking for common typos and mistakes..."
echo ""

# 1. Common typos
echo "=== COMMON TYPOS ===" | tee -a "$REPORT"

check_pattern '\balot\b' "Typo: 'alot' should be 'a lot'" "WARNING" "*.tex"
check_pattern '\bcan not\b' "Style: 'can not' should be 'cannot'" "WARNING" "*.tex"
check_pattern '\boccured\b' "Typo: 'occured' should be 'occurred'" "WARNING" "*.tex"
check_pattern '\brecieve\b' "Typo: 'recieve' should be 'receive'" "WARNING" "*.tex"
check_pattern '\bseperate\b' "Typo: 'seperate' should be 'separate'" "WARNING" "*.tex"
check_pattern '\bdefinately\b' "Typo: 'definately' should be 'definitely'" "WARNING" "*.tex"
check_pattern '\baccommodate\b' "Common mistake: 'accommodate' (double-check spelling)" "INFO" "*.tex"
check_pattern '\bwierd\b' "Typo: 'wierd' should be 'weird'" "WARNING" "*.tex"

# 2. Wrong quotes
echo "" | tee -a "$REPORT"
echo "=== QUOTE ISSUES ===" | tee -a "$REPORT"

check_pattern '"[^"]' "Wrong quotes: Use \`\` and '' instead of \"" "WARNING" "*.tex"

# 3. Common word confusions
echo "" | tee -a "$REPORT"
echo "=== WORD CONFUSIONS ===" | tee -a "$REPORT"

check_pattern '\bit'\''s\b' "Check: Use 'its' (possessive) or 'it's' (it is)?" "INFO" "*.tex"
check_pattern '\baffect\b.*\beffect\b' "Check affect/effect usage" "INFO" "*.tex"
check_pattern '\bthen\b.*\bthan\b' "Check then/than usage" "INFO" "*.tex"

# 4. LaTeX-specific issues
echo "" | tee -a "$REPORT"
echo "=== LATEX ISSUES ===" | tee -a "$REPORT"

check_pattern '\$\$' "Use equation environment instead of \$\$" "WARNING" "*.tex"
check_pattern 'http[s]*://[^ }]*[^}]' "Bare URL: Use \\url{} or \\href{}" "WARNING" "*.tex"
check_pattern '  ' "Multiple consecutive spaces" "INFO" "*.tex"
check_pattern ' \.' "Space before period" "WARNING" "*.tex"
check_pattern ' ,' "Space before comma" "WARNING" "*.tex"

# 5. Check for unmatched environments
echo "" | tee -a "$REPORT"
echo "=== ENVIRONMENT MATCHING ===" | tee -a "$REPORT"

for texfile in *.tex; do
    if [ -f "$texfile" ]; then
        # Extract environment names
        begins=$(grep -o '\\begin{[^}]*}' "$texfile" | sed 's/\\begin{\([^}]*\)}/\1/' | sort)
        ends=$(grep -o '\\end{[^}]*}' "$texfile" | sed 's/\\end{\([^}]*\)}/\1/' | sort)

        if [ "$begins" != "$ends" ]; then
            echo -e "${YELLOW}[WARNING] Potential environment mismatch in $texfile${NC}" | tee -a "$REPORT"
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        fi
    fi
done

# 6. Check for undefined references (look for ??)
echo "" | tee -a "$REPORT"
echo "=== REFERENCE CHECKS ===" | tee -a "$REPORT"

# Check if PDF contains ?? (undefined references)
# This requires the .log file from compilation
if ls *.log &> /dev/null; then
    for logfile in *.log; do
        undefined=$(grep "Reference.*undefined" "$logfile" 2>/dev/null || true)
        if [ ! -z "$undefined" ]; then
            echo -e "${RED}[ERROR] Undefined references found in $logfile${NC}" | tee -a "$REPORT"
            echo "$undefined" | tee -a "$REPORT"
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        fi

        undefined_cites=$(grep "Citation.*undefined" "$logfile" 2>/dev/null || true)
        if [ ! -z "$undefined_cites" ]; then
            echo -e "${RED}[ERROR] Undefined citations found in $logfile${NC}" | tee -a "$REPORT"
            echo "$undefined_cites" | tee -a "$REPORT"
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        fi
    done
fi

# 7. Check citation consistency
echo "" | tee -a "$REPORT"
echo "=== CITATION STYLE ===" | tee -a "$REPORT"

cite_count=$(grep -o '\\cite{' *.tex 2>/dev/null | wc -l)
citep_count=$(grep -o '\\citep{' *.tex 2>/dev/null | wc -l)
citet_count=$(grep -o '\\citet{' *.tex 2>/dev/null | wc -l)

echo "Citation command usage:" | tee -a "$REPORT"
echo "  \\cite: $cite_count" | tee -a "$REPORT"
echo "  \\citep: $citep_count" | tee -a "$REPORT"
echo "  \\citet: $citet_count" | tee -a "$REPORT"

if [ "$cite_count" -gt 0 ] && [ "$citep_count" -gt 0 ]; then
    echo -e "${YELLOW}[INFO] Mixed citation styles: \\cite and \\citep${NC}" | tee -a "$REPORT"
elif [ "$cite_count" -gt 0 ] && [ "$citet_count" -gt 0 ]; then
    echo -e "${YELLOW}[INFO] Mixed citation styles: \\cite and \\citet${NC}" | tee -a "$REPORT"
fi

# 8. Check for very long lines (potential readability issues)
echo "" | tee -a "$REPORT"
echo "=== READABILITY ===" | tee -a "$REPORT"

for texfile in *.tex; do
    if [ -f "$texfile" ]; then
        # Find lines longer than 150 characters (excluding LaTeX commands)
        long_lines=$(awk 'length > 150 && !/^%/ && !/^\\/' "$texfile" | wc -l)
        if [ "$long_lines" -gt 0 ]; then
            echo -e "${YELLOW}[INFO] $texfile has $long_lines very long lines (>150 chars)${NC}" | tee -a "$REPORT"
        fi
    fi
done

# 9. Check for TODO/FIXME comments
echo "" | tee -a "$REPORT"
echo "=== TODO/FIXME ===" | tee -a "$REPORT"

check_pattern '%.*TODO' "TODO comment found" "INFO" "*.tex"
check_pattern '%.*FIXME' "FIXME comment found" "INFO" "*.tex"
check_pattern '%.*XXX' "XXX comment found" "INFO" "*.tex"

# Summary
echo "" | tee -a "$REPORT"
echo "=========================================" | tee -a "$REPORT"
echo "Summary: Found potential issues" | tee -a "$REPORT"
echo "Full report saved to: $REPORT" | tee -a "$REPORT"
echo "=========================================" | tee -a "$REPORT"

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}No major issues found!${NC}"
    exit 0
else
    echo -e "${YELLOW}Please review the report for details${NC}"
    exit 0
fi
