# Takken

This folder is only for Takken-specific code and data.

Current state: metadata only, fail-closed. There is no configured Question Bank
provider or learning-history store. Do not copy PT taxonomy, Knowledge Nodes,
Safety rules, or strategy semantics into this folder without reviewed Takken data.

Principles:

- PTの問題・分類・Knowledge Nodeを流用しない。
- 宅建専用データで独立設計する。
- 共通ロジックのみ `licensetown.common` から利用する。
- 現時点ではダミー問題・ダミー分類・偽実装を置かない。
