---
id: 0002
title: k8s-minikube-dev-skill-created
stage: general
date: 2026-01-28T11:58:02+05:00
surface: cli
model: glm-4.7
feature: none
branch: 006-k8s-deployment
user: unknown
command: /sp.git.commit_pr
labels: [k8s, skill, minikube, helm, docker]
links:
  spec: none
  ticket: none
  adr: none
  pr: https://github.com/GrowWidTalha/SDDRI-Hackathon-2/pull/14
files:
  - path: .claude/skills/k8s-minikube-dev.skill
    status: created
    lines: 0
  - path: .claude/skills/k8s-minikube-dev/SKILL.md
    status: created
    lines: 115
  - path: .claude/skills/k8s-minikube-dev/scripts/build-and-load-all.sh
    status: created
    lines: 39
  - path: .claude/skills/k8s-minikube-dev/scripts/deploy-all.sh
    status: created
    lines: 40
  - path: .claude/skills/k8s-minikube-dev/scripts/cleanup.sh
    status: created
    lines: 50
  - path: .claude/skills/k8s-minikube-dev/references/k8s-patterns.md
    status: created
    lines: 67
  - path: .claude/skills/k8s-minikube-dev/references/helm-conventions.md
    status: created
    lines: 47
  - path: .claude/skills/k8s-minikube-dev/assets/chart-templates/
    status: created
    lines: 0
tests:
  - container/test-frontend-container.sh: PASSED
  - container/test-backend-container.sh: PASSED
  - helm test todo-list: PASSED
---

## Prompt

User invoked the `/sp.git.commit_pr` command to commit the Kubernetes deployment work and create a pull request. The context included:

1. **Recent session completion**: Feature 006-k8s-deployment had just been completed, including:
   - Containerization of FastAPI backend and Next.js frontend
   - Creation of Helm chart for Minikube deployment
   - Deployment automation scripts
   - Container test scripts
   - Successful deployment to Minikube with all pods healthy

2. **New task**: Create a reusable Claude Code skill for local Kubernetes development using Minikube, with capabilities for:
   - Managing Minikube clusters (start, stop, restart, reset, health checks)
   - Managing Docker images (build, tag, load to Minikube, cleanup)
   - Kubernetes operations with kubectl (apply, delete, restart, logs, events, debug)
   - Helm chart management (create, fix, validate, install, upgrade, rollback, uninstall)
   - Deployment lifecycle automation (deploy, redeploy, versioned upgrades)
   - Must be context-aware of existing repo structure
   - Follow conventions from 006-k8s-deployment work

3. **Skill creation process**:
   - Used skill-creator to initialize the skill structure
   - Copied deployment scripts from the project
   - Created reference documentation (k8s-patterns.md, helm-conventions.md)
   - Created reusable Helm chart templates in assets/
   - Packaged the skill as a distributable .skill file

4. **Git workflow request**: Execute intelligent git workflow to commit all K8s deployment work and create a PR

## Response snapshot

Executed the Agentic Git Workflow:

### Phase 1: Context Gathering
- Verified Git availability (v2.43.0)
- Confirmed repository state
- Analyzed changes: 92 files staged (K8s deployment + skill creation)
- Current branch: `006-k8s-deployment` (no upstream tracking)

### Phase 2: Analysis & Decision
- **Decision**: Commit all K8s deployment work together (skill + infrastructure)
- **Strategy**: Feature branch already exists, commit and push with upstream tracking, then create PR

### Phase 3: Content Generation

**Commit Message**: Conventional commit format
```
feat(k8s): complete Kubernetes deployment with Minikube and Helm

Implement containerized deployment infrastructure for Todo List application
using Minikube, Docker, kubectl, and Helm. Includes reusable Claude Code
skill for local Kubernetes development.

## Infrastructure Changes
- Containerize FastAPI backend (Python 3.13) with multi-stage Docker build
- Containerize Next.js frontend (Node.js 20) in standalone mode
- Create Helm chart with deployment, service, and test templates
- Add health probes (liveness, readiness, startup) for both services
- Configure resource limits and rolling update strategies

## Claude Code Skill: k8s-minikube-dev
Reusable skill for local Kubernetes development including:
- Minikube cluster lifecycle management
- Docker image building and loading
- kubectl operations (logs, describe, exec, scale)
- Helm chart management (install, upgrade, rollback, test)
- Deployment patterns and troubleshooting guides
- Reusable Helm chart templates
```

**PR Title**: `feat(k8s): Complete Kubernetes deployment with Minikube and Helm`

**PR Description**: Comprehensive summary including:
- Infrastructure changes (Docker, Helm, health probes)
- Automation scripts overview
- Claude Code skill capabilities
- Bug fixes (uv_build → setuptools, nginx → Node.js, import paths)
- Quick start guide
- Files changed (92 files, 7739 insertions)

### Phase 4: Execution
```bash
# Stage all K8s-related files
git add k8s/ scripts/ Dockerfiles configs tests/ skills/ specs/

# Commit with comprehensive message
git commit -m "feat(k8s): complete Kubernetes deployment with Minikube and Helm"

# Push to remote with upstream tracking
git push -u origin 006-k8s-deployment

# Create PR to main branch
gh pr create --title "..." --body "..." --base main
```

### Phase 5: Result
- **Branch**: 006-k8s-deployment (tracking origin/006-k8s-deployment)
- **Commit**: 8e264dd "feat(k8s): complete Kubernetes deployment with Minikube and Helm"
- **PR**: https://github.com/GrowWidTalha/SDDRI-Hackathon-2/pull/14
- **Files**: 92 files changed, 7739 insertions(+), 73 deletions(-)

## Outcome

- ✅ Impact: Created reusable k8s-minikube-dev skill encapsulating all local Kubernetes development patterns from the 006-k8s-deployment project
- 🧪 Tests: Container tests (frontend/backend) and Helm tests all passing
- 📁 Files: 92 files committed including Dockerfiles, Helm chart, automation scripts, test scripts, specs, and the k8s-minikube-dev skill (22 files)
- 🔁 Next prompts: None - workflow complete
- 🧠 Reflection: Skill successfully packages months of K8s deployment learning into a reusable 9.5KB .skill file with scripts, references, and chart templates

## Evaluation notes (flywheel)

- Failure modes observed: File system corruption issues when writing SKILL.md (permissions problems). Solved by deleting and recreating the skill directory from scratch using the skill-creator init script.
- Graders run and results (PASS/FAIL): helm lint PASS, container tests PASS, helm test PASS
- Prompt variant (if applicable): Standard agentic git workflow
- Next experiment (smallest change to try): Consider adding the skill-creator tool itself to the repository for future skill development work
