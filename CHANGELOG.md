# Changelog

All notable changes to the LICDIA UNLu website are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Versioning policy for this project:

- **MAJOR**: structural site reorganization, breaking URL changes, or major redesign
- **MINOR**: new pages, new features (forms, integrations), new sections
- **PATCH**: bug fixes, content updates, performance and SEO tweaks, asset additions

## [Unreleased]

## [1.0.0] - 2026-06-03

First tagged release. Marks the site as stable after the multi-PR overhaul completed during May–June 2026 (PRs #1–#13 plus this cleanup batch).

### Added
- 70 missing WebP renditions across `assets/img/` (team, mcd-docentes, ipc-fotos, investigaciones, og-*). Site-wide WebP coverage now at 146 files.
- `assets/img/og-default.jpg` and `og-default.webp` (1200×630) for Open Graph fallback used by home and `/charla/*` pages.
- `<h1>` heading on home `masthead-heading` for proper SEO hierarchy.
- Populated `<meta name="description">` on home (was empty).
- `.gitignore` rule for browser "Save Page As Complete" dumps (`**/*_files/`).
- This `CHANGELOG.md`.

### Changed
- WhatsApp deep-link query strings now URL-encode non-ASCII characters (`información` → `informaci%C3%B3n`, `Maestría` → `Maestr%C3%ADa`, `ñ` → `%C3%B1`). WhatsApp was returning HTTP 400 on the previous unencoded links across 46 HTML files.
- `<html lang="en">` corrected to `<html lang="es">` on 15 Spanish-language pages (home, política de privacidad, inscripción dev-ia, proyecto-enseñanza/*, director/*, logos, LLM, fitba-13c, ipc).

### Removed
- Google Maps JS embed (`maps.googleapis.com/maps/api/js`) replaced by a static OpenStreetMap iframe centered on UNLu Luján (−34.5689, −59.1044). Removes the dependency on an exposed and now-revoked Google API key in 5 HTML files (home, política de privacidad, proyecto-enseñanza/{index, juego, ia}).

### Fixed
- Broken images: `assets/img/team/{2,3,4,5,6}.webp` (referenced from `<picture>` but missing on filesystem) and similar gaps across `mcd-docentes/`, `ipc-fotos/`, `investigaciones/`.
- Broken `og:image` on home and `/charla/*` (`og-default.jpg` was referenced but did not exist).

### Security
- Removed the publicly exposed Google Maps API key (`AIzaSy…IE4o`) from all HTML sources. The key should be rotated/revoked in Google Cloud Console if not already.

## Pre-1.0.0 history

Prior history is tracked in the merged PRs:

- **#13** — Parallel agent batch: performance (WebP + minified JS), SEO (OG meta in 23 pages, noindex propuestas, sitemap lastmod), security (Turnstile placeholder, honeypot, ZIP fallback), 404 page, blog index and RSS feed.
- **#12** — `LICDIAForm` shared module with size validation, upload progress, 120 s timeout, ZIP fallback for WhatsApp.
- **#11** — Migrated form webhook to a named Cloudflare tunnel at `n8n.impulsate.lat` (URL no longer rotates on pod restart).
- **#10** — Hotfix for rotating `cloudflared` quick-tunnel URL.
- **#9** — `Aprox.` prefix in date chips; BC timeline uses purple brand palette instead of IA blue.
- **#8** — Horizontal "Proceso de inscripción" timeline with 4 steps and tentative dates on both diplomatura homes.
- **#7** — All Blockchain inscription CTAs point to `/charla/blockchain/#inscripcion`.
- **#6** — 2025 IA Generativa informative talk added as YouTube embed (matches Blockchain layout).
- **#5** — Dark mode, microinteractions, English-language blog SEO.
- **#1–#4** — Initial cohort and content updates.

[Unreleased]: https://github.com/lukisantillan/webLaboratorio/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/lukisantillan/webLaboratorio/releases/tag/v1.0.0
