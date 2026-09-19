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
