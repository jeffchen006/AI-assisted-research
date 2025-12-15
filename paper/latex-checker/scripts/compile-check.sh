#!/bin/bash
# LaTeX Compilation Check Script
# Usage: ./compile-check.sh <project_dir> <main_file> [compiler]

set -e

PROJECT_DIR="${1:-.}"
MAIN_FILE="${2:-main.tex}"
COMPILER="${3:-pdflatex}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "LaTeX Compilation Check"
echo "========================================="
echo "Project: $PROJECT_DIR"
echo "Main file: $MAIN_FILE"
echo "Compiler: $COMPILER"
echo "========================================="

cd "$PROJECT_DIR"

# Extract basename without extension
BASENAME=$(basename "$MAIN_FILE" .tex)

# Check if main file exists
if [ ! -f "$MAIN_FILE" ]; then
    echo -e "${RED}ERROR: Main file $MAIN_FILE not found${NC}"
    exit 1
fi

# Check if .bib file exists
BIB_EXISTS=false
if ls *.bib &> /dev/null; then
    BIB_EXISTS=true
    echo "Bibliography files found"
fi

# Clean previous build artifacts
echo "Cleaning previous build artifacts..."
rm -f "${BASENAME}.aux" "${BASENAME}.log" "${BASENAME}.out" "${BASENAME}.bbl" "${BASENAME}.blg" "${BASENAME}.pdf" 2>/dev/null || true

# First compilation
echo ""
echo "========================================="
echo "First compilation pass..."
echo "========================================="
if $COMPILER -interaction=nonstopmode -file-line-error "$MAIN_FILE" 2>&1 | tee compile_pass1.log; then
    echo -e "${GREEN}First pass completed${NC}"
else
    echo -e "${RED}First pass failed${NC}"
    COMPILE_STATUS="FAILED"
fi

# Run BibTeX if bibliography exists
if [ "$BIB_EXISTS" = true ]; then
    echo ""
    echo "========================================="
    echo "Running BibTeX..."
    echo "========================================="
    if bibtex "$BASENAME" 2>&1 | tee bibtex.log; then
        echo -e "${GREEN}BibTeX completed${NC}"
    else
        echo -e "${YELLOW}BibTeX warnings (may be normal)${NC}"
    fi
fi

# Second compilation (resolve references)
echo ""
echo "========================================="
echo "Second compilation pass..."
echo "========================================="
if $COMPILER -interaction=nonstopmode -file-line-error "$MAIN_FILE" 2>&1 | tee compile_pass2.log; then
    echo -e "${GREEN}Second pass completed${NC}"
else
    echo -e "${RED}Second pass failed${NC}"
    COMPILE_STATUS="FAILED"
fi

# Third compilation (finalize)
echo ""
echo "========================================="
echo "Third compilation pass..."
echo "========================================="
if $COMPILER -interaction=nonstopmode -file-line-error "$MAIN_FILE" 2>&1 | tee compile_pass3.log; then
    echo -e "${GREEN}Third pass completed${NC}"
    COMPILE_STATUS="SUCCESS"
else
    echo -e "${RED}Third pass failed${NC}"
    COMPILE_STATUS="FAILED"
fi

# Analyze the log file
echo ""
echo "========================================="
echo "Analysis"
echo "========================================="

LOG_FILE="${BASENAME}.log"

if [ -f "$LOG_FILE" ]; then
    # Count errors
    ERROR_COUNT=$(grep -c "^!" "$LOG_FILE" 2>/dev/null || echo "0")

    # Count warnings
    WARNING_COUNT=$(grep -c "Warning" "$LOG_FILE" 2>/dev/null || echo "0")

    # Count undefined references
    UNDEFINED_REFS=$(grep -c "Reference.*undefined" "$LOG_FILE" 2>/dev/null || echo "0")

    # Count undefined citations
    UNDEFINED_CITES=$(grep -c "Citation.*undefined" "$LOG_FILE" 2>/dev/null || echo "0")

    # Count overfull hboxes
    OVERFULL=$(grep -c "Overfull" "$LOG_FILE" 2>/dev/null || echo "0")

    echo "Errors: $ERROR_COUNT"
    echo "Warnings: $WARNING_COUNT"
    echo "Undefined references: $UNDEFINED_REFS"
    echo "Undefined citations: $UNDEFINED_CITES"
    echo "Overfull hboxes: $OVERFULL"

    # Show errors if any
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo ""
        echo -e "${RED}=== ERRORS ===${NC}"
        grep -A 2 "^!" "$LOG_FILE" || true
    fi

    # Show critical warnings
    if [ "$WARNING_COUNT" -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}=== WARNINGS (showing first 10) ===${NC}"
        grep "Warning" "$LOG_FILE" | head -10 || true
    fi

    # Show undefined references
    if [ "$UNDEFINED_REFS" -gt 0 ] || [ "$UNDEFINED_CITES" -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}=== UNDEFINED REFERENCES ===${NC}"
        grep "undefined" "$LOG_FILE" || true
    fi
fi

# Final status
echo ""
echo "========================================="
if [ "$COMPILE_STATUS" = "SUCCESS" ]; then
    echo -e "${GREEN}COMPILATION: SUCCESS${NC}"
    if [ -f "${BASENAME}.pdf" ]; then
        echo "PDF generated: ${BASENAME}.pdf"
    fi
else
    echo -e "${RED}COMPILATION: FAILED${NC}"
fi
echo "========================================="

# Save summary
cat > compilation_summary.txt <<EOF
LaTeX Compilation Summary
========================
Project: $PROJECT_DIR
Main file: $MAIN_FILE
Compiler: $COMPILER
Status: $COMPILE_STATUS

Errors: ${ERROR_COUNT:-0}
Warnings: ${WARNING_COUNT:-0}
Undefined references: ${UNDEFINED_REFS:-0}
Undefined citations: ${UNDEFINED_CITES:-0}
Overfull hboxes: ${OVERFULL:-0}

For detailed output, see:
- compile_pass1.log
- compile_pass2.log
- compile_pass3.log
- ${BASENAME}.log
EOF

echo ""
echo "Summary saved to: compilation_summary.txt"

# Exit with appropriate code
if [ "$COMPILE_STATUS" = "SUCCESS" ]; then
    exit 0
else
    exit 1
fi
