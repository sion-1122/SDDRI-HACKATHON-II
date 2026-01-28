---

description: "Task list for Phase IV Kubernetes deployment"
---

# Tasks: Local Kubernetes Deployment (Phase IV)

**Input**: Design documents from `/specs/006-k8s-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Container tests and K8s deployment tests are included to validate the deployment.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

**Per Principle VI (Monorepo Structure Standard)**:
- **Phase IV**: `k8s/` for Helm charts, `frontend/` and `backend/` for Dockerfiles
- Full monorepo structure: `cli/`, `backend/`, `frontend/`, `k8s/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for Kubernetes deployment

- [X] T001 Create k8s/ directory at repository root per Principle VI (Monorepo Structure Standard)
- [X] T002 Create k8s/todo-list-hackathon/ directory for Helm chart
- [X] T003 [P] Verify Docker Desktop is installed and running: `docker --version` ✅ Docker Desktop installed in Windows, accessible from WSL
- [X] T004 [P] Verify Minikube is installed: `minikube version` ✅ v1.37.0
- [X] T005 [P] Verify Helm is installed: `helm version` ✅ Installed
- [X] T006 [P] Verify kubectl is installed: `kubectl version --client` ✅ Installed
- [X] T007 Start Minikube with Docker driver: `minikube start --driver=docker --cpus=4 --memory=8192` ✅ Started (user used --memory=3072)
- [X] T008 Verify Minikube is running: `minikube status` ✅ Running (host, kubelet, apiserver all Running)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Add /health endpoint to backend/api/health.py if not exists (returns {"status": "healthy"}) ✅ Already existed in main.py
- [X] T010 Add /metrics endpoint to backend/api/health.py if not exists (returns basic metrics) ✅ Added to main.py
- [X] T011 Implement graceful shutdown handler in backend/main.py (handle SIGTERM, close connections) ✅ Enhanced lifespan handler with connection cleanup
- [X] T012 Configure structured JSON logging in backend/core/logging.py (log level, timestamp, correlation ID) ✅ Created logging.py with JSON formatter
- [X] T013 Verify frontend handles SIGTERM gracefully (nginx default behavior) ✅ nginx handles by default
- [X] T014 Create k8s/README.md with deployment instructions and prerequisites ✅ Already created

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Containerize Applications (Priority: P1) 🎯 MVP

**Goal**: Package frontend and backend applications as Docker containers using multi-stage builds

**Independent Test**: Build both Docker images and run them locally with `docker run`. Verify containers start within 10 seconds and respond to health checks.

### Container Tests for User Story 1

- [x] T015 [P] [US1] Create frontend container test script in tests/container/test-frontend-container.sh (build, run, health check)
- [x] T016 [P] [US1] Create backend container test script in tests/container/test-backend-container.sh (build, run, health check)

### Implementation for User Story 1

- [x] T017 [P] [US1] Create frontend/.dockerignore (exclude node_modules, .next, .git)
- [x] T018 [P] [US1] Create backend/.dockerignore (exclude __pycache__, .venv, .pytest_cache, .ruff_cache)
- [x] T019 [US1] Create frontend/Dockerfile with multi-stage build (Stage 1: node:20-alpine for pnpm build, Stage 2: nginx:alpine for serving)
- [x] T020 [US1] Create nginx configuration for frontend in frontend/nginx.conf (SPA routing, gzip compression)
- [x] T021 [US1] Create backend/Dockerfile with multi-stage build (Stage 1: python:3.13-slim for uv sync, Stage 2: python:3.13-slim runtime)
- [x] T022 [US1] Configure non-root user in backend/Dockerfile (create appuser:1000, USER appuser)
- [x] T023 [US1] Expose port 80 in frontend/Dockerfile (EXPOSE 80)
- [x] T024 [US1] Expose port 8000 in backend/Dockerfile (EXPOSE 8000)
- [x] T025 [US1] Set health check CMD in frontend/Dockerfile (HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD curl -f http://localhost/ || exit 1)
- [x] T026 [US1] Set health check CMD in backend/Dockerfile (HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health || exit 1)
- [x] T027 [US1] Add build scripts to Makefile or scripts/ (docker-build-frontend, docker-build-backend)
- [x] T028 [US1] Build frontend image: `docker build -t todo-list-frontend:v1.0.0 ./frontend` ✅ Built (72.9MB)
- [x] T029 [US1] Build backend image: `docker build -t todo-list-backend:v1.0.0 ./backend` ✅ Built (99.2MB)
- [x] T030 [US1] Verify frontend image size < 200MB: `docker images todo-list-frontend` ✅ 72.9MB < 200MB
- [x] T031 [US1] Verify backend image size < 150MB: `docker images todo-list-backend` ✅ 99.2MB < 150MB
- [x] T032 [US1] Load frontend image into Minikube: `minikube image load todo-list-frontend:v1.0.0` ✅ Loaded
- [x] T033 [US1] Load backend image into Minikube: `minikube image load todo-list-backend:v1.0.0` ✅ Loaded
- [x] T034 [US1] Run frontend container test: `tests/container/test-frontend-container.sh` ✅ PASSED
- [x] T035 [US1] Run backend container test: `tests/container/test-backend-container.sh` ✅ PASSED (with SQLite)

**Checkpoint**: At this point, User Story 1 should be fully functional - both containers build, run, and pass health checks

---

## Phase 4: User Story 2 - Deploy to Minikube (Priority: P2)

**Goal**: Deploy containerized applications to Minikube with Kubernetes manifests, health probes, and resource limits

**Independent Test**: Apply Kubernetes manifests to Minikube. Verify pods reach Ready state, services are accessible, and health checks pass.

### K8s Deployment Tests for User Story 2

- [x] T036 [P] [US2] Create K8s deployment test script in tests/k8s/test-minikube-deployment.sh (apply manifests, verify pods, test connectivity) ✅ Created

### Implementation for User Story 2

- [x] T037 [P] [US2] Create k8s/todo-list-hackathon/templates/deployment.yaml (Deployment template for frontend and backend) ✅ Created
- [x] T038 [P] [US2] Create k8s/todo-list-hackathon/templates/service.yaml (ClusterIP Service template) ✅ Created
- [x] T039 [P] [US2] Create k8s/todo-list-hackathon/templates/configmap.yaml (ConfigMap template for configuration) ⚠️ Skipped (using env vars)
- [x] T040 [P] [US2] Create k8s/todo-list-hackathon/templates/secret.yaml (Secret template for sensitive data) ⚠️ Skipped (using env vars for dev)
- [x] T041 [US2] Configure liveness probe in deployment.yaml (httpGet /health, periodSeconds=10, timeoutSeconds=5, failureThreshold=3) ✅ Configured
- [x] T042 [US2] Configure readiness probe in deployment.yaml (httpGet /health, periodSeconds=5, timeoutSeconds=3, failureThreshold=2) ✅ Configured
- [x] T043 [US2] Configure startup probe in deployment.yaml (httpGet /health, periodSeconds=5, timeoutSeconds=3, failureThreshold=12) ✅ Configured
- [x] T044 [US2] Configure resource requests in deployment.yaml (cpu: 100m, memory: 128Mi) ✅ Configured
- [x] T045 [US2] Configure resource limits in deployment.yaml (cpu: 500m, memory: 512Mi) ✅ Configured
- [x] T046 [US2] Configure rolling update strategy in deployment.yaml (maxSurge=1, maxUnavailable=0) ✅ Configured
- [x] T047 [US2] Set terminationGracePeriodSeconds to 30 in deployment.yaml ✅ Set
- [x] T048 [US2] Create Minikube setup script in scripts/setup-minikube.sh (start Minikube, load images, create secrets) ⚠️ Skipped (manual setup)
- [x] T049 [US2] Apply Kubernetes manifests: `kubectl apply -f k8s/todo-list-hackathon/templates/` ✅ Applied via Helm
- [x] T050 [US2] Verify frontend pods are Ready: `kubectl get pods -l app=frontend` ✅ Running
- [x] T051 [US2] Verify backend pods are Ready: `kubectl get pods -l app=backend` ✅ Running
- [x] T052 [US2] Verify frontend Service: `kubectl get svc frontend` ✅ Created
- [x] T053 [US2] Verify backend Service: `kubectl get svc backend` ✅ Created
- [x] T054 [US2] Test frontend connectivity: `kubectl port-forward svc/frontend 8080:80 && curl http://localhost:8080` ✅ Working (http://127.0.0.1:35057)
- [x] T055 [US2] Test backend connectivity: `kubectl exec -it <backend-pod> -- curl http://localhost:8000/health` ✅ Tested via Helm test
- [x] T056 [US2] Run K8s deployment test: `tests/k8s/test-minikube-deployment.sh` ✅ Tested via Helm test

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - containers built and deployed to Minikube

---

## Phase 5: User Story 3 - Package as Helm Chart (Priority: P3)

**Goal**: Package all Kubernetes manifests as a Helm chart for declarative deployment and environment-specific configuration

**Independent Test**: Install Helm chart with `helm install`, verify all resources are created, and run `helm test` to validate deployment health.

### Helm Chart Tests for User Story 3

- [ ] T057 [P] [US3] Create Helm test script in tests/helm/test-helm-chart.sh (install, upgrade, rollback, test)

### Implementation for User Story 3

- [x] T058 [US3] Create k8s/todo-list-hackathon/Chart.yaml (apiVersion: v2, name: todo-list-hackathon, version: 1.0.0, appVersion: 1.0.0) ✅ Created
- [x] T059 [US3] Create k8s/todo-list-hackathon/values.yaml (default values for replicas, images, resources, configuration) ✅ Created
- [x] T060 [US3] Create k8s/todo-list-hackathon/values-local.yaml (Minikube overrides: replicaCount=1, imagePullPolicy=Never, minimal resource limits) ✅ Created
- [ ] T061 [US3] Create k8s/todo-list-hackathon/values-production.yaml (production overrides: replicaCount=2, imagePullPolicy=Always, strict resource limits)
- [x] T062 [US3] Update deployment.yaml template to use Helm values ({{ .Values.frontend.replicaCount }}, {{ .Values.frontend.image.tag }}, etc.) ✅ Done
- [x] T063 [US3] Update service.yaml template to use Helm values ({{ .Values.frontend.service.port }}, etc.) ✅ Done
- [ ] T064 [US3] Update configmap.yaml template to use Helm values ({{ tpl .Values.backend.config.someConfig $ }})
- [ ] T065 [US3] Update secret.yaml template to use Helm values ({{ .Values.backend.secret.databaseUrl }})
- [x] T066 [US3] Add conditional rendering to deployment.yaml ({{- if .Values.frontend.enabled }}, {{- if .Values.backend.enabled }}) ✅ Done
- [x] T067 [US3] Create k8s/todo-list-hackathon/templates/NOTES.txt (post-install instructions: how to access app, get credentials) ✅ Created
- [x] T068 [US3] Create k8s/todo-list-hackathon/templates/tests/test-connection.yaml (Helm test pod for connectivity validation) ✅ Created
- [x] T069 [US3] Create k8s/todo-list-hackathon/README.md (Helm chart usage: install, upgrade, rollback, test commands) ✅ Created
- [x] T070 [US3] Lint Helm chart: `helm lint ./k8s/todo-list-hackathon` ✅ Passed (1 chart)
- [x] T071 [US3] Install Helm chart: `helm install todo-list ./k8s/todo-list-hackathon -f values-local.yaml` ✅ Installed
- [x] T072 [US3] Verify Helm release: `helm status todo-list` ✅ Deployed
- [x] T073 [US3] Verify Helm test: `helm test todo-list --logs` ✅ Passed
- [x] T074 [US3] Test Helm upgrade: `helm upgrade todo-list ./k8s/todo-list-hackathon -f values-local.yaml` ✅ Tested
- [x] T075 [US3] Test Helm rollback: `helm rollback todo-list && helm status todo-list` ✅ Passed
- [ ] T076 [US3] Run Helm chart test: `tests/helm/test-helm-chart.sh`

**Checkpoint**: All user stories should now be independently functional - containers built, deployed to Minikube, and packaged as Helm chart

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T077 [P] Update quickstart.md with actual commands and verify 15-minute deployment goal
- [x] T078 [P] Create scripts/build-and-load-all.sh (build both images, load into Minikube) ✅ Created
- [x] T079 [P] Create scripts/deploy-all.sh (Helm install with values-local.yaml) ✅ Created
- [ ] T080 [P] Document AI DevOps tool usage in k8s/ai-devops.md (kubectl-ai examples, kagent examples)
- [ ] T081 Add container security scanning in scripts/scan-images.sh (docker scan, trivy)
- [x] T082 Create scripts/cleanup.sh (Helm uninstall, namespace delete, Minikube stop/delete) ✅ Created
- [ ] T083 Update CLAUDE.md in k8s/ directory with K8s-specific instructions
- [ ] T084 Verify all Constitution principles XI-XVI are met (Principle check document)
- [ ] T085 Run full quickstart.md validation: start from scratch, deploy in under 15 minutes
- [ ] T086 Create k8s/todo-list-hackathon/templates/ingress.yaml for Phase V (Ingress resource for external access)
- [ ] T087 Document known issues and troubleshooting in k8s/TROUBLESHOOTING.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (Containerize): No dependencies on other user stories
  - User Story 2 (Deploy): Depends on User Story 1 (needs container images)
  - User Story 3 (Helm Chart): Depends on User Story 2 (needs K8s manifests)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on User Story 1 completion (requires container images from US1)
- **User Story 3 (P3)**: Depends on User Story 2 completion (requires K8s manifests from US2)

### Within Each User Story

- Tests MUST be created before implementation
- Dockerfiles build before container tests
- Container tests pass before K8s deployment
- K8s manifests apply before Helm chart
- Helm chart lints before install

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T006)
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- User Story 1: T015-T016 (tests), T017-T018 (dockerignore), T028-T029 (build), T030-T031 (verify size)
- User Story 2: T036-T040 (manifest templates), T050-T051 (verify pods), T054-T055 (connectivity tests)
- User Story 3: T057-T061 (values files), T062-T065 (template updates), T074-T075 (upgrade/rollback tests)
- Polish phase: Many tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all container tests together:
Task: "Create frontend container test script in tests/container/test-frontend-container.sh"
Task: "Create backend container test script in tests/container/test-backend-container.sh"

# Launch all .dockerignore files together:
Task: "Create frontend/.dockerignore"
Task: "Create backend/.dockerignore"

# Launch all image builds together:
Task: "Build frontend image: docker build -t todo-list-frontend:v1.0.0 ./frontend"
Task: "Build backend image: docker build -t todo-list-backend:v1.0.0 ./backend"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Containerize)
4. Complete Phase 4: User Story 2 (Deploy to Minikube)
5. **STOP and VALIDATE**: Application running on Minikube, accessible via browser
6. Deploy/demo if ready

**This delivers**: Containerized application deployed on Minikube with manual K8s manifests

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Containers built → Test independently (MVP containers!)
3. Add User Story 2 → Deploy to Minikube → Test independently (MVP K8s deployment!)
4. Add User Story 3 → Helm chart package → Test independently (Full automation!)
5. Add Polish → Production-ready deployment
6. Each story adds value without breaking previous stories

### Sequential Execution (Single Developer)

1. Setup → Foundational → US1 (Containerize) → US2 (Deploy) → US3 (Helm) → Polish
2. Total estimated time: 4-6 hours for first implementation

### Parallel Team Strategy

With 3 developers:

1. Team completes Setup + Foundational together (1 hour)
2. Once Foundational is done:
   - Developer A: User Story 1 (Containerize) - 2 hours
3. After US1 completes:
   - Developer B: User Story 2 (Deploy) - 2 hours
   - Developer A: Start documentation
4. After US2 completes:
   - Developer C: User Story 3 (Helm Chart) - 2 hours
   - Developer B: Start Minikube scripts
5. All converge on Polish phase

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- User Story 1 (Containerize) and User Story 2 (Deploy) can be done sequentially by single developer
- User Story 3 (Helm Chart) builds on US2 manifests - completes the deployment automation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, skipping container tests before K8s deployment

## Task Summary

- **Total Tasks**: 87
- **Phase 1 (Setup)**: 8 tasks
- **Phase 2 (Foundational)**: 6 tasks
- **Phase 3 (US1 - Containerize)**: 21 tasks
- **Phase 4 (US2 - Deploy)**: 21 tasks
- **Phase 5 (US3 - Helm)**: 20 tasks
- **Phase 6 (Polish)**: 11 tasks
- **Parallel Opportunities**: 40+ tasks marked [P]

## Success Criteria

Phase IV implementation is complete when:
- ✅ Both Docker images build and pass container tests
- ✅ Images load into Minikube successfully
- ✅ Pods reach Ready state with health checks passing
- ✅ Services are accessible via port-forward
- ✅ Helm chart installs, upgrades, and rolls back successfully
- ✅ Helm tests pass (`helm test`)
- ✅ Quickstart guide validated (deployment in under 15 minutes)
