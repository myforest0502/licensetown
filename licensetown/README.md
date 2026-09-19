# LicenseTown three-folder application layout

This is the canonical application-domain layout.

```
licensetown/
├── common/   # every qualification may reuse
├── pt/       # physical therapist only
└── takken/   # real-estate transaction specialist only
```

The repository root still contains Git/Render/test/documentation plumbing such as
`.github`, `Procfile`, `tests`, and `docs`. Those are repository infrastructure,
not a fourth qualification domain.

`qualifications/` remains temporarily as a compatibility import layer so the
running PT application is not broken while existing imports are migrated.
New qualification-domain code should use `licensetown.common`,
`licensetown.pt`, or `licensetown.takken` directly.


## Runtime-root exceptions

Only three Python runtime bridge files intentionally remain without a canonical
same-named module inside `licensetown/common` or `licensetown/pt`:

- `app.py`: production Flask/LINE composition entrypoint.
- `wsgi.py`: Render/Gunicorn startup entrypoint.
- `database.py`: legacy runtime DB module whose module identity is still relied
  on by existing monkeypatch/compatibility tests.

These are runtime entrypoints/bridges, not a fourth qualification domain.
All other top-level Python application modules must have a canonical home under
`licensetown/common`, `licensetown/pt`, or `licensetown/takken`.
