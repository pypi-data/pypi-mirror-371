# LaTeX Package for Research Paper

This directory contains the complete LaTeX package for the research paper "Comprehensive Benchmarking Framework for Long-Range Dependence Estimation: Foundation for Physics-Informed Fractional Operator Learning in Neurological Time Series Analysis".

## File Structure

```
documentation/research/
├── main.tex                    # Main LaTeX document
├── abstract.tex               # Abstract content
├── references.bib             # Bibliography file
├── Makefile                   # Compilation automation
├── README.md                  # This file
├── sections/                  # Main paper sections
│   ├── introduction.tex
│   ├── theoretical_foundations.tex
│   ├── framework_design.tex
│   ├── methodology.tex
│   ├── results.tex
│   ├── discussion.tex
│   ├── future_directions.tex
│   └── conclusion.tex
├── appendices/                # Appendix sections
│   ├── appendix_a.tex
│   ├── appendix_b.tex
│   ├── appendix_c.tex
│   ├── appendix_d.tex
│   └── appendix_e.tex
└── figures/                   # Figure directory (create as needed)
    └── [figure files]
```

## Prerequisites

- LaTeX distribution (TeX Live, MiKTeX, or similar)
- pdflatex compiler
- bibtex for bibliography processing
- make (for automated compilation)

## Compilation Instructions

### Using Makefile (Recommended)

1. **Complete compilation with bibliography:**
   ```bash
   make all
   # or
   make pdf
   ```

2. **Quick compilation (no bibliography):**
   ```bash
   make quick
   ```

3. **Clean auxiliary files:**
   ```bash
   make clean
   ```

4. **Clean everything including PDF:**
   ```bash
   make cleanall
   ```

5. **Compile and view PDF:**
   ```bash
   make view
   ```

6. **Show help:**
   ```bash
   make help
   ```

### Manual Compilation

If you prefer manual compilation:

```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

## Adding Content

### Tables

Replace the placeholder comments in the .tex files:

```latex
% PLACEHOLDER: Insert Table 1 - Quality Leaderboard Summary
\begin{table}[h]
\centering
\caption{Quality Leaderboard Summary}
\label{tab:quality_leaderboard}
% INSERT TABLE CONTENT HERE
% \begin{tabular}{lccc}
% \toprule
% Estimator & Category & Avg Error (\%) & Success Rate (\%) \\
% \midrule
% CWT & Wavelet & 14.8 & 100 \\
% R/S & Temporal & 15.6 & 100 \\
% \bottomrule
% \end{tabular}
\end{table}
```

### Figures

Replace the placeholder comments:

```latex
% PLACEHOLDER: Insert Figure 1 - Estimator Performance Comparison
\begin{figure}[h]
\centering
\caption{Estimator Performance Comparison Across Categories}
\label{fig:estimator_performance}
% INSERT FIGURE HERE
% \includegraphics[width=0.8\textwidth]{figures/estimator_performance.png}
\end{figure}
```

### Bibliography

Add new references to `references.bib` in BibTeX format:

```bibtex
@article{Author2024,
  title={Title of the Paper},
  author={Author, A. and Author, B.},
  journal={Journal Name},
  year={2024},
  volume={1},
  pages={1--10}
}
```

## Customization

### Document Information

Edit the following in `main.tex`:
- Author name
- Institution name
- Department name
- Keywords
- PDF metadata

### Styling

The document uses:
- 11pt font size
- A4 paper format
- 1-inch margins
- Professional formatting with headers and footers
- Color-coded hyperlinks
- Harvard-style citations (apalike bibliography style)

### Packages

The document includes comprehensive LaTeX packages for:
- Mathematics and equations
- Tables and figures
- Bibliography management
- Hyperlinks and references
- Professional formatting

## Troubleshooting

### Common Issues

1. **Bibliography not appearing:**
   - Ensure `references.bib` exists and contains valid BibTeX entries
   - Run `bibtex main` after the first `pdflatex` compilation
   - Run `pdflatex` twice more to resolve references

2. **Missing figures:**
   - Create the `figures/` directory
   - Place figure files in the directory
   - Use relative paths in `\includegraphics{}`

3. **Compilation errors:**
   - Check for missing packages in your LaTeX distribution
   - Ensure all referenced files exist
   - Check for syntax errors in .tex files

### Getting Help

- Use `make help` for available commands
- Check LaTeX documentation for package-specific issues
- Ensure your LaTeX distribution is up to date

## Notes

- The document is structured for academic publication
- All placeholders are clearly marked with comments
- The Makefile automates the compilation process
- The bibliography uses Harvard-style citations
- Figures and tables are properly labeled and referenced
