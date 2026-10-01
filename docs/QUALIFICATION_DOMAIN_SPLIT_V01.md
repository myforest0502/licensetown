# Qualification domain split v0.1

## Canonical ownership

`licensetown/common` owns qualification-independent protocols, registries,
session persistence mechanics, payment/site infrastructure and performance
helpers. It has no direct import of PT or Takken.

`licensetown/pt` owns the formal PT Question Bank and data, 18-field taxonomy,
Knowledge Node/evidence/state logic, Safety, adaptive selection, repair and
retention, dashboard/supporter behavior, and PT runtime composition hooks.

`licensetown/takken` is metadata plus empty future-facing directories only. Its
Question Bank, taxonomy, Knowledge Nodes, strategy and services remain
unconfigured and fail closed.

The `licensetown` package root is the composition boundary that registers the
current PT provider/store and recognizes unconfigured Takken. Repository-level
`app.py`, `database.py`, and `wsgi.py` remain runtime bridges. Git/CI/Render,
tests, scripts and docs remain repository infrastructure.

## Compatibility shims

Root Python modules are retained only where existing startup, imports,
monkeypatching or path-sensitive tests depend on them. The four qualification
scope shims now point to their canonical PT modules and are marked
`TODO: compatibility shim`. They can be removed only after all callers use the
canonical package and import-order/module-identity tests prove safety.

## Intentionally not moved in this change

- `app.py` and `wsgi.py`: Flask/LINE/Render composition and startup contracts.
- `database.py`: legacy module identity and monkeypatch compatibility.
- templates/static/tests/scripts/docs: Flask paths and repository
  infrastructure; ownership does not imply Python package placement.
- mixed developer/payment/site adapters already under common: existing root
  compatibility calls and Flask registration are preserved. Their product
  semantics are not generalized by this folder name.

No Question Bank content, DB schema/data, migrations, selector policy, Node
state, Stage E, Phase11, LINE behavior or UI design changes are part of this
split.
