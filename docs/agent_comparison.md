# Agent Framework Comparison

This document summarizes the main differences between the three reasoning frameworks available in this project.

## Chain of Thought (CoT)
- **Flow**: `入力 -> 思考 -> 最終的な答え`
- **Strengths**: Simple linear reasoning. Useful when a brief explanation of intermediate thoughts is enough.
- **Weaknesses**: Cannot interact with tools and cannot explore alternatives.

## ReAct (Reason + Act)
- **Flow**: `入力 -> [思考 -> 行動 -> 観察] ... -> 最終的な答え`
- **Strengths**: Each step can call external tools, enabling factual answers with clear reasoning traces.
- **Weaknesses**: Still limited to a single execution path and may struggle with complex planning.

## Tree of Thoughts (ToT)
- **Flow**: `入力 -> 複数の[思考 ...] を探索 -> 最終的な答え`
- **Strengths**: Explores many candidate reasoning paths and backtracks when necessary, suitable for puzzles or long term planning.
- **Weaknesses**: Computationally expensive and more complex to implement.

You can adjust the search depth and branching factor using the `--depth` and
`--breadth` command line options. When these are omitted, the defaults can be
set via the `TOT_DEPTH` and `TOT_BREADTH` environment variables.

Select the appropriate framework in the GUI or CLI depending on task complexity.
