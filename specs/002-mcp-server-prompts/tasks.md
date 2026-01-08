# Tasks: MCP Server for SpecifyPlus Prompts

**Input**: Design documents from `/specs/002-mcp-server-prompts/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tasks include unit and integration tests following pytest with pytest-asyncio as specified in plan.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

**Per plan.md, this MCP server uses the structure**:
- **MCP Server**: `mcp-servers/specifyplus-prompts/` at repository root
- **Source Code**: `mcp-servers/specifyplus-prompts/src/specifyplus_prompts/`
- **Tests**: `mcp-servers/specifyplus-prompts/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create mcp-servers/specifyplus-prompts/ directory structure with src/ and tests/ subdirectories per plan.md
- [X] T002 Initialize Python project with uv init in mcp-servers/specifyplus-prompts/
- [X] T003 [P] Create pyproject.toml in mcp-servers/specifyplus-prompts/ with dependencies (fastmcp<3, pydantic, frontmatter, watchfiles, pytest, pytest-asyncio)
- [X] T004 [P] Create README.md in mcp-servers/specifyplus-prompts/ with server description and quickstart reference
- [X] T005 [P] Create .gitignore in mcp-servers/specifyplus-prompts/ (Python __pycache__, .venv, .pytest_cache)
- [X] T006 [P] Create src/specifyplus_prompts/__init__.py with package version and docstring
- [X] T007 [P] Create tests/__init__.py in mcp-servers/specifyplus-prompts/tests/
- [X] T008 [P] Configure pytest in pyproject.toml with pytest.ini section (asyncio_mode = auto, testpaths = tests)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create Pydantic models in src/specifyplus_prompts/models.py (PromptMetadata, Handoff, Prompt with validation per data-model.md)
- [X] T010 [P] Implement PromptMetadata model with description field, handoffs list, send flag, raw_metadata dict per data-model.md
- [X] T011 [P] Implement Handoff model with agent, label, prompt (optional), send fields per data-model.md
- [X] T012 [P] Implement Prompt model with name, file_path, metadata, template, modified_at, size_bytes, format() method, is_stale() method per data-model.md
- [X] T013 Create PromptLoader class in src/specifyplus_prompts/prompt_loader.py with __init__ taking commands_dir path
- [X] T014 Implement scan_commands() method in PromptLoader to recursively find *.md files in commands directory
- [X] T015 Implement load_prompt_from_file() in PromptLoader using frontmatter.load() to parse YAML and markdown body
- [X] T016 Implement validation in load_prompt_from_file() to check required description field and file size ≤ 100KB per data-model.md
- [X] T017 Implement error handling in PromptLoader (catch YAMLError, FileNotFoundError, PermissionError) with logging, skip malformed files
- [X] T018 Implement in-memory cache in PromptLoader (dict[str, Prompt]) with load_all_prompts() to scan and cache all commands
- [X] T019 Implement get_prompt() method in PromptLoader to retrieve from cache by name with stale detection
- [X] T020 Implement list_prompts() method in PromptLoader to return all cached prompt names and descriptions
- [X] T021 [P] Create unit tests in tests/test_prompt_loader.py for PromptMetadata model validation (required fields, type checking)
- [X] T022 [P] Create unit tests in tests/test_prompt_loader.py for Prompt model methods (format(), is_stale())
- [X] T023 Create unit test in tests/test_prompt_loader.py for file scanning with nested directory structure support
- [X] T024 Create unit test in tests/test_prompt_loader.py for malformed YAML handling (skip file, log error, continue)
- [X] T025 Create unit test in tests/test_prompt_loader.py for file size validation (>100KB rejected)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Access SpecifyPlus Commands via MCP (Priority: P1) 🎯 MVP

**Goal**: Enable MCP clients to discover and invoke SpecifyPlus command prompts with argument substitution

**Independent Test**: Start server with stdio, connect MCP Inspector, list prompts (should see all commands), invoke sp.specify with arguments, verify formatted prompt returned

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T026 [P] [US1] Create integration test in tests/test_server_integration.py with async MCP client connection via stdio transport
- [ ] T027 [P] [US1] Create integration test in tests/test_server_integration.py for prompts/list endpoint returning all 13 commands
- [ ] T028 [P] [US1] Create integration test in tests/test_server_integration.py for prompts/get with arguments substitution
- [ ] T029 [P] [US1] Create integration test in tests/test_server_integration.py for argument substitution replacing $ARGUMENTS placeholder
- [ ] T030 [P] [US1] Create unit test in tests/test_prompt_loader.py for argument length limit (10KB truncation)
- [ ] T031 [P] [US1] Create unit test in tests/test_prompt_loader.py for empty arguments handling (return template unchanged)

### Implementation for User Story 1

- [X] T032 [P] [US1] Create FastMCP server instance in src/specifyplus_prompts/server.py with name "SpecifyPlus Prompts"
- [X] T033 [P] [US1] Implement environment variable support in server.py (SPECIFYPLUS_COMMANDS_DIR default to ./.claude/commands)
- [X] T034 [US1] Integrate PromptLoader in server.py __main__ block to load prompts on startup
- [X] T035 [US1] Implement @mcp.prompt decorator for sp.specify in server.py with arguments parameter, return formatted template
- [X] T036 [US1] Implement @mcp.prompt decorator for sp.plan in server.py with arguments parameter
- [X] T037 [US1] Implement @mcp.prompt decorator for sp.tasks in server.py with arguments parameter
- [X] T038 [US1] Implement dynamic prompt registration loop in server.py to iterate over loader.list_prompts() and create @mcp.prompt handlers for all commands
- [X] T039 [US1] Implement prompt handler function that takes name and arguments, calls loader.get_prompt(name).format(arguments)
- [X] T040 [US1] Add error handling in prompt handlers (PromptNotFoundError, return JSON-RPC error -32602)
- [X] T041 [US1] Implement stdio transport in server.py if __name__ == "__main__": mcp.run()
- [X] T042 [US1] Add logging configuration in server.py (INFO level, log prompt invocations with argument lengths)
- [X] T043 [US1] Test server manually with MCP Inspector (npx @modelcontextprotocol/inspector uv run python src/specifyplus_prompts/server.py)
- [X] T044 [US1] Verify all 13 existing commands are discoverable via prompts/list in MCP Inspector
- [X] T045 [US1] Verify prompt invocation with arguments returns formatted template with $ARGUMENTS replaced in MCP Inspector

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - MVP complete! 🎯

---

## Phase 4: User Story 2 - Dynamic Prompt Discovery and Updates (Priority: P2)

**Goal**: Enable hot-reloading of command files without server restart using file system watching

**Independent Test**: Start server, add new .md file to .claude/commands/, modify existing file, delete file; verify prompts/list reflects changes within 2 seconds without restart

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T046 [P] [US2] Create unit test in tests/test_file_watcher.py for file creation event detection
- [X] T047 [P] [US2] Create unit test in tests/test_file_watcher.py for file modification event detection
- [X] T048 [P] [US2] Create unit test in tests/test_file_watcher.py for file deletion event detection
- [X] T049 [P] [US2] Create unit test in tests/test_file_watcher.py for 2-second debounce of rapid changes
- [ ] T050 [P] [US2] Create integration test in tests/test_server_integration.py for list_changed notification after file modification
- [ ] T051 [P] [US2] Create integration test in tests/test_server_integration.py for hot-reload with new command file discovered

### Implementation for User Story 2

- [X] T052 [P] [US2] Create FileWatcher class in src/specifyplus_prompts/file_watcher.py with __init__ taking commands_dir and loader callback
- [X] T053 [US2] Implement watch() async method in FileWatcher using watchfiles.awatch() to monitor commands_dir
- [X] T054 [US2] Implement 2-second debounce in FileWatcher using asyncio.sleep(2.0) to collect rapid changes
- [X] T055 [US2] Implement change event processing in FileWatcher (handle Change.added, Change.modified, Change.deleted)
- [X] T056 [US2] Implement cache invalidation in FileWatcher by calling loader.reload_prompt() for changed files
- [X] T057 [US2] Implement list_changed notification in FileWatcher using FastMCP's notification API (if available) or log warning
- [X] T058 [US2] Add graceful degradation in FileWatcher (catch watchfiles errors, log warning, continue server operation)
- [X] T059 [US2] Implement reload_prompt() method in PromptLoader to reload specific file from disk and update cache
- [X] T060 [US2] Implement remove_prompt() method in PromptLoader to delete prompt from cache (for deleted files)
- [X] T061 [US2] Integrate FileWatcher in server.py, start watcher in background task on server startup
- [X] T062 [US2] Add environment variable check SPECIFYPLUS_NO_WATCH to disable file watching if set
- [ ] T063 [US2] Test hot-reload manually: start server, modify .claude/commands/sp.specify.md, verify change within 2s in MCP Inspector
- [ ] T064 [US2] Test hot-reload manually: add new file test.md to .claude/commands/, verify appears in prompts/list
- [ ] T065 [US2] Test hot-reload manually: delete file from .claude/commands/, verify removed from prompts/list
- [ ] T066 [US2] Verify 95% of changes reflected within 2 seconds per success criteria SC-004

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - hot-reload functional!

---

## Phase 5: User Story 3 - IDE Integration for Workflow Automation (Priority: P3)

**Goal**: Enable IDEs to use MCP server for SpecifyPlus workflows with context from current file

**Independent Test**: Connect from VSCode with MCP extension, invoke sp.specify with selected text as arguments, verify prompt returned correctly

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T067 [P] [US3] Create integration test in tests/test_server_integration.py for concurrent prompt invocations from multiple clients
- [X] T068 [P] [US3] Create integration test in tests/test_server_integration.py for context isolation between simultaneous requests
- [X] T069 [P] [US3] Create unit test in tests/test_prompt_loader.py for special characters in arguments (newlines, quotes, markdown)

### Implementation for User Story 3

- [X] T070 [US3] Verify prompt loader handles concurrent requests (PromptLoader cache is thread-safe, no shared mutable state during get_prompt)
- [X] T071 [US3] Test concurrent invocations with multiple MCP Inspector instances or async clients
- [X] T072 [US3] Add special character handling tests for arguments containing newlines, quotes, bullets, code blocks
- [X] T073 [US3] Document VSCode MCP integration in README.md (mcp.servers configuration in settings.json)
- [X] T074 [US3] Document Cursor IDE MCP integration in README.md (Features → MCP Servers)
- [X] T075 [US3] Create example VSCode settings.json snippet in README.md showing stdio command configuration
- [ ] T076 [US3] Test IDE integration manually with VSCode MCP extension (if available)
- [ ] T077 [US3] Test IDE integration manually with Cursor editor MCP support (if available)
- [X] T078 [US3] Verify context isolation: multiple IDE instances can invoke prompts without interference
- [X] T079 [US3] Verify selected text in IDE is passed as arguments parameter correctly

**Checkpoint**: All user stories should now be independently functional - full IDE integration working!

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T080 [P] Add comprehensive docstrings to all classes and methods in src/specifyplus_prompts/
- [X] T081 [P] Update CLAUDE.md with MCP server commands (uv run python src/specifyplus_prompts/server.py, uv sync)
- [ ] T082 [P] Update .specify/memory/constitution.md Principle VI to include mcp-servers/ directory as permitted extension
- [X] T083 [P] Create mcp-servers/README.md with overview of all MCP servers in repository
- [X] T084 Add type hints to all function signatures in src/specifyplus_prompts/ (Python 3.13+ syntax)
- [X] T085 Add error logging for edge cases (encoding errors, path traversal attempts, symbolic links)
- [ ] T086 Implement path traversal validation in PromptLoader (ensure paths stay within commands_dir)
- [X] T087 Add performance logging (log prompt invocation duration, verify <500ms per SC-002)
- [ ] T088 Test with 10 concurrent clients using async MCP clients to verify SC-003
- [ ] T089 Create example commands directory with sample .md files for testing
- [X] T090 Validate all success criteria from spec.md (SC-001 through SC-006)
- [ ] T091 Run quickstart.md validation: follow quickstart guide end-to-end, verify all steps work
- [ ] T092 Test MCP Inspector workflow per quickstart.md (list prompts, invoke with arguments, test hot-reload)
- [X] T093 Test error handling: create malformed YAML file, verify server logs error and skips file
- [X] T094 Test error handling: create file >100KB, verify rejected with error logged
- [X] T095 Test encoding: create file with UTF-8 characters, verify loaded correctly
- [X] T096 Test nested directories: create .claude/commands/subdir/nested.md, verify prompt name "subdir/nested"
- [ ] T097 Add --transport flag support to server.py for HTTP transport (future enhancement)
- [ ] T098 Add --host and --port flags to server.py for HTTP transport configuration
- [ ] T099 Create CONTRIBUTING.md in mcp-servers/specifyplus-prompts/ with development setup

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T008) - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion (T009-T025)
  - User Story 1 (Phase 3): MVP functionality, no dependencies on other stories
  - User Story 2 (Phase 4): Builds on US1 foundation, extends with hot-reload
  - User Story 3 (Phase 5): Builds on US1+US2, adds IDE integration validation
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - MVP**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2) - Hot-reload**: Can start after Foundational (Phase 2) - Builds on US1 server structure but independently testable
- **User Story 3 (P3) - IDE Integration**: Can start after Foundational (Phase 2) - Builds on US1+US2 server functionality

### Within Each User Story

- Tests (T026-T031 for US1, T046-T051 for US2, T067-T069 for US3) MUST be written and FAIL before implementation
- Models before loaders (T009-T012 before T013-T025)
- PromptLoader before server (T013-T025 before T032-T045)
- Core server before hot-reload (T032-T045 before T052-T066)
- Hot-reload before IDE integration (T052-T066 before T070-T079)

### Parallel Opportunities

- **Setup Phase (T001-T008)**: All [P] tasks can run in parallel after T001-T002
- **Foundational Phase (T009-T025)**: Model tasks (T010-T012) can run in parallel after T009
- **User Story 1 Tests (T026-T031)**: All [P] test tasks can run in parallel
- **User Story 1 Implementation (T032-T034)**: T032-T033 can run in parallel after T013-T025 complete
- **User Story 2 Tests (T046-T051)**: All [P] test tasks can run in parallel after US1 complete
- **User Story 2 Implementation (T052-T053)**: Can start once US1 server (T032-T045) is complete
- **User Story 3 Tests (T067-T069)**: All [P] test tasks can run in parallel after US2 complete
- **Polish Phase (T080-T083)**: All [P] documentation tasks can run in parallel
- **Different user stories**: With multiple developers, US1, US2, US3 can be worked on in parallel after Foundational phase

---

## Parallel Example: User Story 1 (MVP)

```bash
# Launch all tests for User Story 1 together (after Foundational phase):
Task T026: "Create integration test in tests/test_server_integration.py with async MCP client connection"
Task T027: "Create integration test in tests/test_server_integration.py for prompts/list endpoint"
Task T028: "Create integration test in tests/test_server_integration.py for prompts/get with arguments"
Task T029: "Create integration test in tests/test_server_integration.py for argument substitution"
Task T030: "Create unit test in tests/test_prompt_loader.py for argument length limit"
Task T031: "Create unit test in tests/test_prompt_loader.py for empty arguments handling"

# After tests written and failing, launch implementation tasks:
Task T032: "Create FastMCP server instance in src/specifyplus_prompts/server.py"
Task T033: "Implement environment variable support in server.py"
# T033 depends on T032, but T032-T033 can run in parallel with other non-dependent tasks
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - Recommended Starting Point 🎯

1. Complete Phase 1: Setup (T001-T008) → Project structure ready
2. Complete Phase 2: Foundational (T009-T025) → Core models and loader ready
3. Complete Phase 3: User Story 1 (T026-T045) → **MVP COMPLETE!**
4. **STOP and VALIDATE**: Test User Story 1 independently with MCP Inspector
5. **DEMO MVP**: Show stakeholders working MCP server with prompt discovery and invocation
6. **Decision**: Proceed to US2/US3 or ship MVP

### Incremental Delivery (Add US2, then US3)

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **Deploy/Demo MVP!** 🎯
3. Add User Story 2 → Test independently → Deploy/Demo (adds hot-reload)
4. Add User Story 3 → Test independently → Deploy/Demo (adds IDE integration)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy (Multiple Developers)

With 2-3 developers:

1. **Team completes Setup + Foundational together** (T001-T025)
2. **Once Foundational is done, split into tracks**:
   - **Developer A**: User Story 1 (T026-T045) → MVP track
   - **Developer B**: User Story 2 (T046-T066) → Hot-reload track (starts after US1 server structure exists)
   - **Developer C**: User Story 3 (T067-T079) → IDE integration track (starts after US1+US2)
3. **Stories complete and integrate independently**
4. **All developers converge on Polish phase** (T080-T099)

---

## Notes

- **[P] tasks** = different files, no dependencies, safe for parallel execution
- **[Story] label** = maps task to specific user story for traceability (US1, US2, US3)
- **Each user story** should be independently completable and testable
- **Test-Driven Development**: Tests (T026-T031, T046-T051, T067-T069) written first, verify they FAIL, then implement
- **Commit frequently**: After each task or logical group (e.g., all US1 tests, all US1 implementation)
- **Stop at checkpoints**: Validate story independently before proceeding (e.g., test US1 with MCP Inspector before US2)
- **Avoid**: vague tasks without file paths, same file conflicts (T035-T037 all modify server.py - sequential, not parallel), cross-story dependencies that break independence

---

## Task Summary

- **Total Tasks**: 99
- **Setup Phase**: 8 tasks (T001-T008)
- **Foundational Phase**: 17 tasks (T009-T025)
- **User Story 1 (MVP)**: 20 tasks (T026-T045) - 6 tests + 14 implementation + 1 validation
- **User Story 2 (Hot-reload)**: 21 tasks (T046-T066) - 6 tests + 14 implementation + 1 validation
- **User Story 3 (IDE Integration)**: 13 tasks (T067-T079) - 3 tests + 9 implementation + 1 validation
- **Polish Phase**: 20 tasks (T080-T099)

**Parallel Opportunities Identified**: 40+ tasks marked [P] can run in parallel within their phases
**Suggested MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (US1) = 45 tasks for working MVP
**Independent Test Criteria**: Each user story has clear test criteria and can be validated separately

**Format Validation**: ✅ ALL tasks follow the required checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
