# Changelog

All notable changes to lex-harness will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-04-07

### Added
- Initial plugin scaffold with `.claude-plugin/plugin.json`
- 4 skills: `legal-strategy`, `osint-investigation`, `document-production`, `devil-advocate`
- 3 slash commands: `/lex-harness:init`, `/lex-harness:fact`, `/lex-harness:devil`
- Greek law pack (`law-packs/greece/`) with 22 core articles + 3 modules (tenancy, tax_invoices, corporate)
- Templates for case skeleton, PROVEN_FACTS_REGISTER, PENDING_FACTS, DEADLINE_REGISTER, CLAUDE.md
- Git pre-commit hook for T1 write-path isolation (Co-Authored-By trailer detection)
- Codex skill bootstrap script
- Plugin requirements PR-01 through PR-15 (including tool-optionality discipline)
- Documentation: ARCHITECTURE, JURISDICTION_PACK_SPEC, PLUGIN_REQUIREMENTS, TOOL_OPTIONALITY, ROADMAP, SECURITY
- 15 Gherkin acceptance scenarios driving the test plan
- MIT LICENSE
- README, CONTRIBUTING, CODE_OF_CONDUCT
