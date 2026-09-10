# LicenseTown SEO Foundation Audit — 2026-09-10

## Goal
Make the public LicenseTown site understandable to search engines as a service for physical therapist national exam preparation without redesigning the approved UI.

## Findings before implementation
- `/site` already had a title, description and basic Open Graph metadata.
- The metadata was generic around qualification study and did not strongly describe the primary product as `理学療法士国家試験 / PT国試` preparation.
- The parent `/site` document is primarily an iframe shell, while the useful product copy lives in the rendered PC/mobile documents.
- There was no dedicated root `robots.txt` or `sitemap.xml` boundary for the public site.
- Preview/source documents should not compete with `/site` in search results.

## Implemented foundation
- PT-exam-focused title and meta description on `/site`.
- Canonical URL and Open Graph URL/site/locale metadata.
- Explicit index/follow robots meta on the canonical public page.
- JSON-LD for `WebSite` and `SoftwareApplication` / `EducationalApplication`.
- Root `/robots.txt` with public-site discovery and preview exclusions.
- Root `/sitemap.xml` containing `/site` and `/site/faq`.
- `X-Robots-Tag: noindex, nofollow, noarchive` on preview/source boundaries.
- SEO-specific regression tests.

## Scope intentionally excluded
- No redesign of the approved PC/mobile site.
- No Question Bank or learner-flow changes.
- No keyword stuffing or hidden SEO-only body copy.
- No mass blog/article generation.
- No promise of rankings or search traffic.

## Product viability condition
This SEO-foundation task is complete when the public canonical page exposes the metadata/discovery controls above, preview duplicates are noindex, CI is green, and production deploy is live without visible regression.
