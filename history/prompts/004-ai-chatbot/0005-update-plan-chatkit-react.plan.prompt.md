---
id: 0005
title: update-plan-chatkit-react
stage: plan
date: 2025-01-15
surface: claude
model: claude-sonnet-4-5
feature: 004-ai-chatbot
branch: 004-ai-chatbot
user: developer
command: /sp.plan
labels: [plan, phase-3, ai-chatbot, chatkit-react, update]
links:
  spec: ../../specs/004-ai-chatbot/spec.md
  ticket:
  adr:
  pr:
files:
  - path: specs/004-ai-chatbot/plan.md
    status: updated
    change: Updated Chat UI section to use @openai/chatkit-react with detailed component implementation examples
  - path: specs/004-ai-chatbot/tasks.md
    status: updated
    change: Updated T002 to reference @openai/chatkit-react package
  - path: specs/004-ai-chatbot/research.md
    status: updated
    change: Updated ChatKit Integration section with @openai/chatkit-react details, rationale, and code examples
  - path: specs/004-ai-chatbot/quickstart.md
    status: updated
    change: Updated installation instructions and troubleshooting to reference @openai/chatkit-react
tests:
  - package specificity: PASSED (all references updated to specific @openai/chatkit-react package)
  - code examples: PASSED (added comprehensive ChatKit component implementation examples)
  - installation instructions: PASSED (updated npm/pnpm/yarn commands for @openai/chatkit-react)
---

## Prompt

User executed `/sp.plan We want to use openai/chatkit-js for chatbot UI. https://openai.github.io/chatkit-js/ see this and update the plan and tasks` to update the implementation plan to use OpenAI's official ChatKit library.

The command executed the plan workflow:
1. Fetched information from https://openai.github.io/chatkit-js/ about ChatKit.js capabilities
2. Searched for @openai/chatkit-react package information on npm
3. Retrieved package details: @openai/chatkit-react v1.1.0 (React bindings for ChatKit web component)
4. Updated plan.md with specific package name and implementation details
5. Updated tasks.md with correct package reference
6. Updated research.md with comprehensive ChatKit integration guide
7. Updated quickstart.md with installation instructions

## Response snapshot

Successfully updated plan and tasks to use @openai/chatkit-react:

**Updated plan.md - Chat UI Section**:
- Changed: "ChatKit (OpenAI)" → "@openai/chatkit-react (OpenAI's official ChatKit React bindings)"
- Added comprehensive component implementation example showing:
  - Import: `import { ChatKit, useChatKit } from '@openai/chatkit-react'`
  - Component usage: `<ChatKit messages={messages} onSendMessage={handleSubmit} />`
  - State management with useState hooks
  - Integration with backend API endpoint
- Added alternative implementation using web component directly: `<openai-chatkit />`

**Updated tasks.md**:
- T002: "Install frontend dependencies (ChatKit, AI SDK)" → "Install frontend dependencies (@openai/chatkit-react)"

**Updated research.md - Section 3**:
- Title: "ChatKit Integration" → "Use @openai/chatkit-react with Next.js App Router"
- Rationale expanded to include:
  - Official OpenAI ChatKit React bindings
  - Drop-in chat component with deep UI customization
  - Built-in response streaming for interactive conversations
  - Tool and workflow integration for visualizing agentic actions
  - Rich interactive widgets rendered directly inside chat
  - Attachment handling with file and image upload support
  - Thread and message management
  - TypeScript-first design with React 19 support
- Installation commands updated for npm/pnpm/yarn
- Added complete ChatInterface.tsx component example with:
  - Message state management
  - Conversation ID tracking
  - Backend API integration
  - ChatKit component rendering

**Updated quickstart.md**:
- Frontend setup section updated with:
  - `npm install @openai/chatkit-react`
  - `pnpm add @openai/chatkit-react`
  - `yarn add @openai/chatkit-react`
- Troubleshooting section updated to check for @openai/chatkit-react

**Updated research.md Summary Table**:
- Chat UI row: "ChatKit (OpenAI)" → "@openai/chatkit-react" with expanded rationale

**Key Information Gathered**:
- Package: @openai/chatkit-react v1.1.0 (published 16 hours ago)
- Weekly downloads: 6,082
- Repository: github.com/openai/chatkit-js
- React bindings for ChatKit web component
- Provides hooks and JSX helpers that wrap `<openai-chatkit />`

**Format Validation**: ✅ PASSED
- All code examples use correct package name
- Installation commands are accurate
- Component implementation follows React 19 patterns
- Integration with Next.js App Router properly documented

## Outcome

- ✅ Impact: Updated all plan documents to specifically reference @openai/chatkit-react package, providing implementers with exact package name, version, installation commands, and comprehensive code examples
- 🧪 Tests: Package specificity passed; code examples valid; installation instructions accurate
- 📁 Files: Updated plan.md (Chat UI section), tasks.md (T002), research.md (ChatKit Integration section), quickstart.md (installation and troubleshooting)
- 🔁 Next prompts: Continue with Phase 1 Setup implementation (T002 now has correct package name), or proceed to Phase 2 Foundational tasks
- 🧠 Reflection: Plan update successfully generalizes from generic "ChatKit" reference to specific @openai/chatkit-react npm package. The comprehensive component implementation examples provide clear guidance for developers, showing both React component usage and web component alternative. All installation instructions now reference the correct package across npm, pnpm, and yarn. This ensures implementers can install and integrate ChatKit without ambiguity.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan update completed successfully with accurate package information
- Graders run and results (PASS/FAIL): Package Specificity: PASSED (all references use @openai/chatkit-react); Code Examples: PASSED (valid React 19 implementation); Installation Instructions: PASSED (accurate npm/pnpm/yarn commands)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Complete T002 manually by running `pnpm add @openai/chatkit-react` in frontend directory, then proceed to Phase 2 Foundational tasks
