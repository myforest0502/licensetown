# LicenseTown three-folder layout v0.1

Canonical application-domain code is organized under:

- `licensetown/common/`: reusable across qualifications
- `licensetown/pt/`: physical therapist only
- `licensetown/takken/`: Takken only

The old `qualifications/` package remains as a compatibility import layer so the
running PT application does not need a risky flag-day import rewrite.

Repository infrastructure (`.github`, `Procfile`, `docs`, `tests`, etc.) remains
at repository root. It is not qualification-domain ownership.

No Question Bank, Knowledge Node, DB schema, selector policy, Stage E authority,
Phase11 authority, or Takken activation is changed by this layout.
