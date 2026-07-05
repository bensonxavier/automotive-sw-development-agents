# Repository Agent Guidance

Use the repo-maintainer agent for git maintenance tasks in this repository.

## Deployment safety rules for repo-ops
- Preserve existing deployed pages and deployment outputs. Do not disturb live GitHub Pages or other deployment targets unless the user explicitly requests a change.
- For any pull request targeting main, treat deployment safety as a required gate. Review the repo-specific deployment workflow before making changes.
- If a deployment issue is observed, follow a short test → verify → fix → re-test loop. Keep fixes minimal and reversible.
- If a problem cannot be resolved safely and needs human judgment, pause and request confirmation before applying a fix.
- Use the repo-specific build, test, and deployment commands from the repository docs or workflow files rather than assuming one workflow fits every repo.

## Preferred approach
- Inspect repo state before changing anything.
- When a sync or update request identifies a repository that exists remotely but not locally, ask the user for confirmation before pulling the remote main/master branch into the local workspace.
- Treat this confirmation step as part of every sync request and any explicit request to update from a remote repository.
- If the local repository has uncommitted or unpushed changes, confirm the intended pull/sync action with the user before proceeding.
- Prefer native git commands over GitHub CLI.
- Avoid repeated `gh` retries when the tool is missing.
- Use the repo-maintenance skill for repeatable maintenance patterns.
- For larger tasks, coordinate multiple specialist subagents when helpful.
