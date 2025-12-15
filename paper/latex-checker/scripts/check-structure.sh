#!/bin/bash
# LaTeX Structure and Syntax Checker
# Usage: ./check-structure.sh <project_dir>

PROJECT_DIR="${1:-.}"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================="
echo "LaTeX Structure & Syntax Checker"
echo "========================================="
echo "Project: $PROJECT_DIR"
echo "========================================="

cd "$PROJECT_DIR"

# Check if any .tex files exist
if ! ls *.tex &> /dev/null; then
    echo -e "${RED}ERROR: No .tex files found${NC}"
    exit 1
fi

REPORT="structure_report.txt"
> "$REPORT"

echo "LaTeX Structure & Syntax Report" >> "$REPORT"
echo "==============================" >> "$REPORT"
echo "Project: $PROJECT_DIR" >> "$REPORT"
echo "Date: $(date)" >> "$REPORT"
echo "" >> "$REPORT"

ERRORS=0
WARNINGS=0

# Function to report issue
report_issue() {
    local severity="$1"
    local message="$2"

    if [ "$severity" = "ERROR" ]; then
        echo -e "${RED}[ERROR] $message${NC}" | tee -a "$REPORT"
        ERRORS=$((ERRORS + 1))
    elif [ "$severity" = "WARNING" ]; then
        echo -e "${YELLOW}[WARNING] $message${NC}" | tee -a "$REPORT"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${BLUE}[INFO] $message${NC}" | tee -a "$REPORT"
    fi
}

echo "" | tee -a "$REPORT"
echo "=== FILE INVENTORY ===" | tee -a "$REPORT"

# Count files
tex_files=$(ls -1 *.tex 2>/dev/null | wc -l)
bib_files=$(ls -1 *.bib 2>/dev/null | wc -l)

echo "LaTeX files (.tex): $tex_files" | tee -a "$REPORT"
echo "Bibliography files (.bib): $bib_files" | tee -a "$REPORT"

if [ -d "figures" ] || [ -d "figs" ] || [ -d "images" ]; then
    echo "Figure directories found" | tee -a "$REPORT"
fi

echo "" | tee -a "$REPORT"
echo "Files:" | tee -a "$REPORT"
ls -1 *.tex 2>/dev/null | tee -a "$REPORT"

# Check each .tex file
echo "" | tee -a "$REPORT"
echo "=== SYNTAX CHECKS ===" | tee -a "$REPORT"

for texfile in *.tex; do
    if [ ! -f "$texfile" ]; then
        continue
    fi

    echo "" | tee -a "$REPORT"
    echo "Checking: $texfile" | tee -a "$REPORT"
    echo "---" | tee -a "$REPORT"

    # 1. Check for unmatched braces
    open_braces=$(grep -o "{" "$texfile" | wc -l)
    close_braces=$(grep -o "}" "$texfile" | wc -l)

    if [ "$open_braces" -ne "$close_braces" ]; then
        report_issue "ERROR" "$texfile: Unmatched braces (open: $open_braces, close: $close_braces)"
    fi

    # 2. Check for unmatched brackets
    open_brackets=$(grep -o "\[" "$texfile" | wc -l)
    close_brackets=$(grep -o "\]" "$texfile" | wc -l)

    if [ "$open_brackets" -ne "$close_brackets" ]; then
        report_issue "WARNING" "$texfile: Unmatched brackets (open: $open_brackets, close: $close_brackets)"
    fi

    # 3. Check for unmatched dollar signs (math mode)
    # This is tricky because $$ is valid
    dollar_count=$(grep -o '\$' "$texfile" | wc -l)
    double_dollar_count=$(grep -o '\$\$' "$texfile" | wc -l)
    # Each $$ counts as 2 $, so actual singles = total - (doubles * 2)
    single_dollar_count=$((dollar_count - double_dollar_count * 2))

    if [ $((single_dollar_count % 2)) -ne 0 ]; then
        report_issue "ERROR" "$texfile: Unmatched \$ (math mode delimiter)"
    fi

    # 4. Check \begin{} and \end{} matching
    while IFS= read -r env; do
        if [ ! -z "$env" ]; then
            begin_count=$(grep -c "\\\\begin{$env}" "$texfile" 2>/dev/null || echo "0")
            end_count=$(grep -c "\\\\end{$env}" "$texfile" 2>/dev/null || echo "0")

            if [ "$begin_count" -ne "$end_count" ]; then
                report_issue "ERROR" "$texfile: Unmatched environment '$env' (begin: $begin_count, end: $end_count)"
            fi
        fi
    done < <(grep -o '\\begin{[^}]*}' "$texfile" | sed 's/\\begin{\([^}]*\)}/\1/' | sort -u)

    # 5. Check for \label{} usage
    labels=$(grep -o '\\label{[^}]*}' "$texfile" | sed 's/\\label{\([^}]*\)}/\1/')

    if [ ! -z "$labels" ]; then
        # Check for duplicate labels
        duplicates=$(echo "$labels" | sort | uniq -d)
        if [ ! -z "$duplicates" ]; then
            report_issue "ERROR" "$texfile: Duplicate labels found: $duplicates"
        fi

        # Check for labels with spaces
        bad_labels=$(echo "$labels" | grep ' ')
        if [ ! -z "$bad_labels" ]; then
            report_issue "WARNING" "$texfile: Labels with spaces found (not recommended)"
        fi
    fi

    # 6. Check figure/table structure
    grep -n "\\\\begin{figure}" "$texfile" 2>/dev/null | while read -r line; do
        line_num=$(echo "$line" | cut -d: -f1)
        # Check if there's a \caption within next 20 lines
        next_lines=$(sed -n "${line_num},$((line_num + 20))p" "$texfile")

        if ! echo "$next_lines" | grep -q "\\\\caption"; then
            report_issue "WARNING" "$texfile:$line_num: Figure without \\caption"
        fi

        if ! echo "$next_lines" | grep -q "\\\\label"; then
            report_issue "INFO" "$texfile:$line_num: Figure without \\label (consider adding for referencing)"
        fi
    done

    grep -n "\\\\begin{table}" "$texfile" 2>/dev/null | while read -r line; do
        line_num=$(echo "$line" | cut -d: -f1)
        next_lines=$(sed -n "${line_num},$((line_num + 20))p" "$texfile")

        if ! echo "$next_lines" | grep -q "\\\\caption"; then
            report_issue "WARNING" "$texfile:$line_num: Table without \\caption"
        fi

        if ! echo "$next_lines" | grep -q "\\\\label"; then
            report_issue "INFO" "$texfile:$line_num: Table without \\label (consider adding for referencing)"
        fi
    done

    # 7. Check for common problematic patterns
    grep -n "\\\\ref{}" "$texfile" 2>/dev/null | while read -r line; do
        report_issue "ERROR" "$texfile:$(echo $line | cut -d: -f1): Empty \\ref{}"
    done

    grep -n "\\\\cite{}" "$texfile" 2>/dev/null | while read -r line; do
        report_issue "ERROR" "$texfile:$(echo $line | cut -d: -f1): Empty \\cite{}"
    done

    # 8. Check section hierarchy
    has_chapter=$(grep -c "\\\\chapter" "$texfile" 2>/dev/null || echo "0")
    has_chapter=$(echo "$has_chapter" | tr -d ' \n')
    has_section=$(grep -c "\\\\section" "$texfile" 2>/dev/null || echo "0")
    has_section=$(echo "$has_section" | tr -d ' \n')
    has_subsection=$(grep -c "\\\\subsection" "$texfile" 2>/dev/null || echo "0")
    has_subsection=$(echo "$has_subsection" | tr -d ' \n')
    has_subsubsection=$(grep -c "\\\\subsubsection" "$texfile" 2>/dev/null || echo "0")
    has_subsubsection=$(echo "$has_subsubsection" | tr -d ' \n')

    if [ "$has_subsubsection" -gt 0 ] && [ "$has_subsection" -eq 0 ]; then
        report_issue "WARNING" "$texfile: Has \\subsubsection but no \\subsection (check hierarchy)"
    fi

    if [ "$has_subsection" -gt 0 ] && [ "$has_section" -eq 0 ] && [ "$has_chapter" -eq 0 ]; then
        report_issue "WARNING" "$texfile: Has \\subsection but no \\section (check hierarchy)"
    fi
done

# Check for referenced but missing graphics
echo "" | tee -a "$REPORT"
echo "=== GRAPHICS CHECK ===" | tee -a "$REPORT"

for texfile in *.tex; do
    if [ ! -f "$texfile" ]; then
        continue
    fi

    # Extract all \includegraphics references
    graphics=$(grep -o '\\includegraphics\[*[^]]*\]*{[^}]*}' "$texfile" | sed 's/.*{\([^}]*\)}/\1/')

    for graphic in $graphics; do
        # Try common extensions if no extension given
        if [ ! -f "$graphic" ]; then
            found=false
            for ext in .pdf .png .jpg .jpeg .eps; do
                if [ -f "${graphic}${ext}" ]; then
                    found=true
                    break
                fi
            done

            if [ "$found" = false ]; then
                report_issue "ERROR" "$texfile: Referenced graphic not found: $graphic"
            fi
        fi
    done
done

# Check bibliography
echo "" | tee -a "$REPORT"
echo "=== BIBLIOGRAPHY CHECK ===" | tee -a "$REPORT"

has_bibliography=false
for texfile in *.tex; do
    if grep -q "\\\\bibliography{" "$texfile" || grep -q "\\\\addbibresource{" "$texfile"; then
        has_bibliography=true
        break
    fi
done

if [ "$has_bibliography" = true ]; then
    echo "Bibliography commands found" | tee -a "$REPORT"

    if [ "$bib_files" -eq 0 ]; then
        report_issue "ERROR" "Bibliography command found but no .bib files present"
    fi
else
    if grep -q "\\\\cite" *.tex; then
        report_issue "WARNING" "Citations found but no \\bibliography or \\addbibresource command"
    fi
fi

# Summary
echo "" | tee -a "$REPORT"
echo "=========================================" | tee -a "$REPORT"
echo "SUMMARY" | tee -a "$REPORT"
echo "=========================================" | tee -a "$REPORT"
echo "Errors: $ERRORS" | tee -a "$REPORT"
echo "Warnings: $WARNINGS" | tee -a "$REPORT"
echo "" | tee -a "$REPORT"
echo "Full report saved to: $REPORT" | tee -a "$REPORT"
echo "=========================================" | tee -a "$REPORT"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}No issues found! Structure looks good.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}Found $WARNINGS warnings. Please review.${NC}"
    exit 0
else
    echo -e "${RED}Found $ERRORS errors and $WARNINGS warnings. Please fix errors before compiling.${NC}"
    exit 1
fi
