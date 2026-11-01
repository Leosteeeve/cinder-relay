# CINDER RELAY — agent rules

- Communicate with the owner in Chinese; write implementation prompts in English.
- Read `README.md`, `docs/MILESTONES.md`, and `docs/TECHNICAL_DESIGN.md` first.
- Current authorization: Phase05.4 combat feel, bounded grounded slide and curated Workshop/supporting industrial environment polish. Follow docs/COMBAT_ENVIRONMENT_05_4.md. Preserve accepted Phase053 weapon/arms, schema1, IDs, checkpoints, native streaming and workbench lifecycle. Stop before Phase06.
- Canon lives in `docs/GAME_DESIGN.md` and `docs/STORY.md`; mark new creative proposals, never silently invent canon.
- Priorities: reliability, gameplay quality, maintainability, performance, then visual fidelity.
- Preserve existing work. Audit before edits; never upgrade the engine or rewrite working architecture without authorization.
- Target UE 5.8; installed baseline is 5.8.4. Verify `Build.version` and actual project targets before using build commands.
- Prefer Unreal-native systems, C++ foundations, and Blueprint authoring. Add modules/plugins only for a demonstrated requirement.
- Use events/delegates where suitable. Avoid synchronous asset loads in interactive paths and unnecessary cross-level hard references.
- Chapter 01 uses handcrafted linear zones: prefer native Level Streaming, not mandatory World Partition or a custom streaming framework.
- Follow `docs/ASSET_SOURCES.md` before importing external content. Binary Unreal assets require a working Editor pathway; never fabricate them.
- Never rename an existing C++ module without an explicit migration plan. `CinderRelay` was created only after verifying no ThresholdFPS module existed.
- Keep each task bounded by deliverables, dependencies, acceptance criteria, verification, and non-goals.
- Compile relevant C++ changes once, run focused checks, and request one short manual milestone pass. Do not rebuild or run every test without new evidence.
- After two unsuccessful repair attempts on the same failure, stop editing and present an evidence-based diagnosis before continuing.
- Profile before optimizing. Never equate C++, a successful build, or screenshots with performance or gameplay acceptance.
- Report commands, exit codes, evidence paths, and unverified work. Keep raw local logs under ignored `.environment-local/`; summarize durable findings in the milestone.
- Inspect explicit staging paths and staged diff for secrets, generated files, and unlicensed raw packs before commits. Never overwrite or force-push remote history.
- Work on `codex/phase-05-4-combat-slide-environment`; target `main` with a PR, never auto-merge or force-push. Never rerun old generators destructively. Keep R reload/F5 streaming retry. DA_Rook5 is immutable; retain 0.9s cycle, 2.4s reload, five-round magazine and ADS65/60. Cosmetic notifies never award ammo/damage. Preserve Phase03/05/051/052 sources and Phase01A rollback; verify imported bones and real playback.

- Checkpoints use stable IDs and narrow GameMode snapshots. Never serialize Actor references or cinematic/timer state. Restore session flags before streamed actors BeginPlay; release the player only after native readiness and a validated checkpoint floor. Report success only from the native save callback. Tests must use CR04_TEST_ slots; never corrupt or delete player saves.
