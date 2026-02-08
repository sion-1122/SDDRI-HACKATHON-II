# Research: ChatKit Migration with Gemini Compatibility

**Feature**: 010-chatkit-migration
**Date**: 2026-02-06
**Status**: Complete

## Executive Summary

**CRITICAL FINDING**: ChatKit **CAN** work with Gemini as the LLM, but **ONLY** through the **advanced (self-hosted) integration** approach. The standard OpenAI-hosted integration requires OpenAI's infrastructure and workflows.

**Migration Viability**: ✅ **FEASIBLE**

The technical path is clear and well-supported by official documentation. The key is implementing a custom `ChatKitServer` backend with the OpenAI Agents SDK configured to use Gemini's OpenAI-compatible endpoint.

---

## Decision: Self-Hosted ChatKit Integration

### Decision Summary

Use ChatKit's **advanced (self-hosted) integration** pattern, which involves:
- Frontend: ChatKit React UI component
- Backend: Custom `ChatKitServer` implementation using ChatKit Python SDK
- LLM: Gemini via OpenAI-compatible endpoint
- Orchestration: OpenAI Agents SDK with custom AsyncOpenAI client

### Rationale

1. **Gemini Compatibility**: Self-hosted integration allows custom OpenAI client configuration with `base_url` set to Gemini's OpenAI-compatible endpoint
2. **Full Control**: Backend maintains ownership of tools, auth, rate limiting, and persistence
3. **No Vendor Lock-in**: Avoid OpenAI-hosted workflows and infrastructure
4. **Code Reduction**: ChatKit replaces ~600+ lines of custom chat UI code
5. **Feature Parity**: All required features (streaming, tool calling, persistence) are supported

### Alternatives Considered

| Alternative | Description | Rejected Because |
|-------------|-------------|------------------|
| OpenAI-Hosted Integration | Use ChatKit with OpenAI Agent Builder workflows | Requires OpenAI infrastructure; no custom base_url support; forces GPT models |
| Keep Custom Chat UI | Maintain existing custom implementation | Higher maintenance burden; misses goal of code reduction and improved UX |
| Hybrid Approach | ChatKit UI with custom streaming implementation | More complex than full self-hosted pattern; negates ChatKit benefits |

---

## Key Research Findings

### 1. ChatKit Architecture Models

**OpenAI-Hosted Integration** (NOT viable for Gemini):
- ChatKit UI → OpenAI Agent Builder → OpenAI infrastructure
- No custom base_url support
- OpenAI manages backend, storage, authentication

**Self-Hosted Integration** (✅ VIABLE):
- ChatKit UI → Custom backend (ChatKit Python SDK) → Your LLM choice
- Full control over authentication, data, orchestration
- Custom OpenAI client with any base_url

### 2. Gemini OpenAI Compatibility

**Gemini provides full OpenAI-compatible endpoint:**

```python
from openai import AsyncOpenAI

gemini_client = AsyncOpenAI(
    api_key="GEMINI_API_KEY",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
```

**Key Configuration:**
- `base_url`: `https://generativelanguage.googleapis.com/v1beta/openai/`
- `api_key`: Gemini API key
- `model`: Gemini models (`gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-2.5-pro`)

### 3. OpenAI Agents SDK Custom Client Support

**CRITICAL**: The OpenAI Agents SDK **explicitly supports custom OpenAI clients**:

```python
from agents import set_default_openai_client

set_default_openai_client(gemini_client)
```

This is the integration point for using Gemini with ChatKit's backend.

### 4. Self-Hosted Session Creation

**No OpenAI Sessions API involvement**. Authentication is entirely custom:

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()
server = MyChatKitServer(data_store, file_store)

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    # Extract user from existing JWT auth
    user_id = get_current_user_id(request)
    result = await server.process(await request.body(), {"user_id": user_id})
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
```

### 5. Streaming Implementation

**ChatKit uses Server-Sent Events (SSE)** for streaming:

- Backend: `StreamingResponse` with `media_type="text/event-stream"`
- Frontend: ChatKit.js handles SSE consumption automatically
- Gemini: Supports OpenAI-compatible streaming via `stream=True`

### 6. Authentication Boundaries

**No client_secret/session tokens** in self-hosted mode:

```
Frontend (ChatKit.js)
    ↓ SSE with custom auth headers (JWT via cookies)
Your Backend (ChatKit Python SDK)
    ↓ OpenAI SDK with custom client
Gemini API (via OpenAI-compatible endpoint)
```

**Implementation:**
- Frontend → Backend: Custom `fetch` override with auth headers
- Backend → Gemini: AsyncOpenAI client with Gemini API key
- No OpenAI Sessions API calls

### 7. Tool Visualization Support

**ChatKit provides rich widget system:**
- Cards, Lists, Forms, Text blocks, Buttons
- Server-side widget rendering
- Client tool execution support

**Gemini supports OpenAI-compatible function calling:**
- Full OpenAI tool schema compatibility
- Server-side tool execution
- MCP tools can be wrapped as Agents SDK tools

### 8. Feature Support Matrix

| Feature | Support Level | Notes |
|---------|---------------|-------|
| Chat completions | ✅ Full | Via OpenAI-compatible endpoint |
| Streaming responses | ✅ Full | SSE protocol compatible |
| Function calling | ✅ Full | OpenAI tool schema |
| Multi-turn conversations | ✅ Full | Thread management |
| Tool execution visualization | ✅ Full | Widget system |
| Custom authentication | ✅ Full | Fetch override |
| Conversation persistence | ✅ Full | Your storage layer |

---

## Current System Analysis

### Existing Components

**Frontend (~600 LOC to be removed):**
- `ChatInterface.tsx` (286 lines) - Main chat component
- `MessageList.tsx` (~80 lines) - Message display
- `MessageInput.tsx` (~60 lines) - Input handling
- `ProgressBar.tsx` (~40 lines) - Progress visualization
- `ConnectionStatus.tsx` (~30 lines) - WebSocket status
- `useWebSocket.ts` (~100 lines) - WebSocket hook

**Backend (~350 LOC to be removed):**
- `ws_manager/manager.py` (196 lines) - WebSocket connection manager
- `ws_manager/events.py` (~50 lines) - WebSocket event broadcasting
- `ai_agent/agent_streaming.py` (159 lines) - Streaming wrapper with progress events

**Total LOC to remove: ~950 lines**

### Existing Architecture

```
Frontend (Custom React)
    ↓ WebSocket + REST API
Backend (FastAPI)
    ↓ OpenAI Agents SDK
Gemini (via AsyncOpenAI with base_url)
```

### Target Architecture

```
Frontend (ChatKit React)
    ↓ SSE with custom fetch
Backend (ChatKit Python SDK + Agents SDK)
    ↓ AsyncOpenAI with base_url
Gemini (OpenAI-compatible endpoint)
```

---

## Technical Requirements Validation

### ✅ Confirmed Capabilities

1. **Custom base_url Support**: OpenAI SDK and Agents SDK fully support custom base_url
2. **Gemini Compatibility**: Gemini provides OpenAI-compatible endpoint with streaming and tool calling
3. **Self-Hosted Sessions**: ChatKit Python SDK designed for self-hosted implementations
4. **Authentication**: Custom fetch override allows JWT/cookie-based auth
5. **Streaming**: SSE streaming supported by ChatKit and Gemini
6. **Tool Calling**: Full OpenAI tool schema compatibility

### ⚠️ Known Limitations

1. **Beta Status**: Gemini's OpenAI compatibility is "still in beta"
2. **Feature Parity**: Some OpenAI-specific features may not map perfectly
3. **Model Differences**: Gemini models have different reasoning behavior
4. **Testing Required**: Thorough testing needed to verify all features work

---

## Migration Approach

### Phase 1: Backend Setup
1. Install `openai-chatkit` and `openai-agents` packages
2. Configure Gemini client with custom base_url
3. Implement `ChatKitServer` class
4. Implement `Store` and `FileStore` interfaces
5. Create `/chatkit` endpoint with SSE streaming

### Phase 2: Frontend Integration
1. Install `@openai/chatkit-react` package
2. Replace custom chat components with `ChatKit` embed
3. Configure custom fetch for authentication
4. Remove WebSocket-related code

### Phase 3: Tool Migration
1. Wrap existing MCP tools as Agents SDK functions
2. Configure agent with Gemini model
3. Test tool execution and visualization

### Phase 4: Cleanup
1. Delete custom chat UI components
2. Delete WebSocket manager and events
3. Delete streaming wrapper
4. Update documentation

---

## Risk Assessment

### High Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Gemini compatibility gaps | Feature breakage | Thorough testing; fallback to custom implementation |
| Streaming format differences | UI issues | Agents SDK handles abstraction; test edge cases |

### Medium Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tool calling nuances | Tool execution failures | Use OpenAI-compatible tool schema; validate each tool |
| Model capability differences | Response quality changes | Adjust prompts; test with Gemini models |

### Low Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Rate limiting differences | Service disruption | Monitor Gemini quota separately |
| Beta stability | Potential breaking changes | Pin versions; monitor updates |

---

## Dependencies

### New Dependencies Required

**Backend:**
- `openai-chatkit` - ChatKit Python SDK
- `openai-agents` - OpenAI Agents SDK (likely already installed)

**Frontend:**
- `@openai/chatkit-react` - ChatKit React component

### Existing Dependencies Preserved

- `openai` - OpenAI Python SDK (for custom client)
- `fastapi` - Web framework
- React 19, Next.js 16 - Frontend framework
- Existing MCP tools and database

---

## Success Criteria Validation

| Criterion | Feasibility | Notes |
|-----------|-------------|-------|
| < 2s first token response | ✅ | SSE streaming supported |
| < 500ms tool visibility | ✅ | Widget system for tool visualization |
| 100% Gemini LLM usage | ✅ | Custom client configuration |
| Zero WebSocket code | ✅ | SSE replaces WebSocket |
| 95% conversation persistence | ✅ | Custom Store implementation |
| 600+ LOC reduction | ✅ | ~950 LOC of custom code removed |
| All 7 tools execute | ✅ | Tool wrapping preserves functionality |
| Graceful error handling | ✅ | Try/catch in streaming |
| < 1s session creation | ✅ | No OpenAI Sessions API call |

---

## Documentation Sources

**Official Documentation Referenced:**
- [ChatKit Main Guide](https://platform.openai.com/docs/guides/chatkit)
- [ChatKit.js API Reference](https://platform.openai.com/docs/api-reference/chatkit-react)
- [ChatKit Sessions Guide](https://platform.openai.com/docs/guides/chatkit/sessions)
- [ChatKit Python Guide](https://platform.openai.com/docs/guides/chatkit/python)
- [ChatKit Python API](https://platform.openai.com/docs/api-reference/chatkit-python)
- [OpenAI Agents SDK Guide](https://platform.openai.com/docs/guides/agents)
- [OpenAI Agents API](https://platform.openai.com/docs/api-reference/agents)
- [Gemini OpenAI Compatibility](https://ai.google.dev/gemini-api/docs/openai)

**Reference Implementation:**
- [openai-chatkit-advanced-samples](https://github.com/openai/openai-chatkit-advanced-samples)

---

## Conclusion

The migration to ChatKit with Gemini is **technically feasible** using the self-hosted integration pattern. The research confirms:

1. ✅ ChatKit supports custom LLM providers via self-hosted backend
2. ✅ Gemini provides OpenAI-compatible endpoint
3. ✅ OpenAI Agents SDK supports custom clients
4. ✅ All required features (streaming, tools, persistence) are supported
5. ✅ Significant code reduction achievable (~950 LOC)

**Recommendation**: Proceed with implementation using the self-hosted ChatKit + Gemini architecture documented in this research.
