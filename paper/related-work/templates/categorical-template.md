# Categorical/Thematic Related Work Template

Use this template when organizing related work by approach or methodology.

## Structure

```latex
\section{Related Work}

% Opening paragraph: Set context
[Research area] has been extensively studied from multiple perspectives.
Existing work can be broadly categorized into [N] main approaches:
[list categories]. We review each category and discuss how our work
relates to and extends beyond these efforts.

% Category 1
\subsection{[Category Name]}
% Opening: Introduce the category and its key characteristic
[Category description]. This approach is characterized by [key feature].

% Main papers in this category
[Author1 et al.]~\cite{author1year} pioneered this direction by [contribution].
They demonstrated [achievement/result]. Building on this work,
[Author2 et al.]~\cite{author2year} extended [specific aspect] by [method].
Their approach achieved [result] but required [limitation/assumption].

More recently, [Author3 et al.]~\cite{author3year} addressed [problem]
through [approach]. While effective for [scenario], these methods
share common limitations: [list limitations].

% Category 2
\subsection{[Category Name]}
% Opening: Introduce category and contrast with previous
Unlike [Category 1], which focuses on [aspect], these approaches
tackle the problem from [different angle].

[Continue pattern from Category 1]

% Category 3 (if needed)
\subsection{[Category Name]}
[Continue pattern]

% Comparison and Analysis
\subsection{Comparative Analysis}
% Optional: Add a subsection comparing approaches if you have many categories
Table~\ref{tab:comparison} summarizes the key characteristics of
different approaches. [Category 1] methods excel at [strength] but
struggle with [weakness]. [Category 2] approaches address [aspect]
but at the cost of [tradeoff].

% Gap identification
Our work differs from existing approaches in several key aspects.
First, while [Category 1] methods assume [assumption], our approach
[how you differ]. Second, unlike [Category 2] which requires [requirement],
we [your advantage]. Finally, no existing work addresses the combination
of [problem aspects], which is critical for [application/scenario].
```

## Example Instantiation

### Research Area: Federated Learning

```latex
\section{Related Work}

Federated learning has emerged as a promising paradigm for privacy-preserving
machine learning. Existing work can be broadly categorized into three main
approaches: optimization algorithms, privacy mechanisms, and system designs.
We review each category and discuss how our work extends these efforts.

\subsection{Federated Optimization Algorithms}
A fundamental challenge in federated learning is developing optimization
algorithms that converge efficiently in distributed settings with
heterogeneous data.

McMahan et al.~\cite{mcmahan2017fedavg} pioneered this direction by
introducing Federated Averaging (FedAvg), which enables distributed
training by averaging local model updates. They demonstrated convergence
on both IID and non-IID data distributions. Building on this work,
Li et al.~\cite{li2020fedprox} extended FedAvg by incorporating a
proximal term to handle system heterogeneity. Their approach,
FedProx, achieved better convergence but required careful tuning
of the proximal parameter.

More recently, Karimireddy et al.~\cite{karimireddy2020scaffold}
addressed client drift through SCAFFOLD, which uses control variates
to correct for local updates. While effective for highly non-IID data,
these methods assume synchronous communication, which limits scalability
in real-world deployments.

\subsection{Privacy-Preserving Mechanisms}
Unlike optimization-focused approaches, these methods prioritize
protecting individual data privacy during federated training.

[Continue pattern...]

\subsection{System Designs and Implementations}
[Continue pattern...]

Our work differs from existing approaches in several key aspects.
First, while optimization algorithms assume a fixed privacy budget,
our approach adaptively adjusts the privacy-utility tradeoff based
on data heterogeneity. Second, unlike privacy mechanisms that operate
independently of the optimization process, we integrate privacy
preservation directly into the optimization algorithm. Finally,
no existing work addresses the combination of adaptive privacy,
heterogeneity-aware optimization, and practical system constraints,
which is critical for real-world federated learning deployments.
```

## Tips for Using This Template

1. **Number of Categories**: 3-5 categories work best
   - Too few: Not enough organization
   - Too many: Becomes hard to follow

2. **Category Names**: Should be:
   - Descriptive and specific
   - Mutually exclusive (no overlap)
   - Cover all major work in the area

3. **Within Each Category**:
   - Start with foundational/pioneering work
   - Progress chronologically or by complexity
   - Group similar papers together
   - Highlight both achievements and limitations

4. **Transition Sentences**:
   - Between papers: "Building on this...", "In contrast...", "More recently..."
   - Between categories: "Unlike [previous category]...", "Complementary to..."

5. **Balance**:
   - Don't over-cite one paper
   - Each major paper gets 2-4 sentences
   - Similar papers can be grouped

6. **Critical Analysis**:
   - Don't just list contributions
   - Explain why each contribution matters
   - Identify limitations fairly
   - Show how works relate to each other

## Common Mistakes to Avoid

❌ **Too descriptive**: Listing every detail of each paper
✅ **Right level**: Key contribution, main result, limitations

❌ **No connections**: Treating each paper independently
✅ **Show relationships**: How papers build on or differ from each other

❌ **No critique**: Only positive descriptions
✅ **Balanced**: Acknowledge both strengths and limitations

❌ **Unclear gap**: Vague statement about "no one has done X"
✅ **Specific gap**: Concrete statement of what's missing and why it matters

## Variations

### Variation 1: With Comparison Table
Add a table summarizing approaches:

```latex
\begin{table}
\caption{Comparison of federated learning approaches}
\label{tab:comparison}
\begin{tabular}{lccc}
\toprule
Approach & Handles Non-IID & Privacy & System Cost \\
\midrule
FedAvg~\cite{mcmahan2017fedavg} & Limited & No & Low \\
FedProx~\cite{li2020fedprox} & Moderate & No & Low \\
DP-FedAvg~\cite{...} & Limited & Yes & Medium \\
Ours & Strong & Yes & Low \\
\bottomrule
\end{tabular}
\end{table}
```

### Variation 2: Two-Level Categorization
For very comprehensive surveys:

```latex
\subsection{Machine Learning Approaches}
\subsubsection{Deep Learning Methods}
[Papers...]
\subsubsection{Classical ML Methods}
[Papers...]

\subsection{Optimization-Based Approaches}
[Continue...]
```

### Variation 3: Problem-First Organization
Start each category with the problem it addresses:

```latex
\subsection{Handling Data Heterogeneity}
The challenge of non-IID data distribution across clients is
fundamental in federated learning. [Author] addressed this by...
```
