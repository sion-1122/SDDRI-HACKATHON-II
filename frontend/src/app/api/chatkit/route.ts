/* ChatKit API route - Proxy to FastAPI backend with SSE streaming support.

[Task]: T011
[From]: specs/010-chatkit-migration/contracts/backend.md

This route proxies ChatKit requests to the FastAPI backend.
The backend returns Server-Sent Events (SSE) for streaming responses.
All authentication is handled via httpOnly cookies.

Endpoint proxied:
- POST /api/chatkit - ChatKit SSE endpoint for AI chat
*/
import { NextRequest } from 'next/server';

// Read backend URL dynamically to ensure it's available at runtime
function getBackendUrl(): string {
  const backendUrl = process.env.NEXT_PUBLIC_API_URL';
  
  // Log in development to help debug
  if (process.env.NODE_ENV === 'development') {
    console.log('[ChatKit Proxy] Backend URL:', backendUrl);
  }
  
  return backendUrl;
}

export async function POST(request: NextRequest) {
  try {
    const BACKEND_URL = getBackendUrl();
    const backendUrl = `${BACKEND_URL}/api/chatkit`;

    // Prepare headers for backend request
    const headers = new Headers();
    // Forward cookies from the client request
    const cookieHeader = request.headers.get('cookie');
    if (cookieHeader) {
      headers.set('cookie', cookieHeader);
    }
    // Forward content-type if present
    const contentType = request.headers.get('content-type');
    if (contentType) {
      headers.set('content-type', contentType);
    }

    // Get request body
    let body: string | null = null;
    try {
      body = await request.text();
    } catch (e) {
      body = null;
    }

    // Proxy the request to FastAPI backend
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers,
      body: body || undefined,
      credentials: 'include',
    });

    // If response is not ok, return error
    if (!response.ok) {
      // Try to get error message from response
      const errorText = await response.text().catch(() => response.statusText);
      return new Response(errorText, {
        status: response.status,
        statusText: response.statusText,
        headers: {
          'Content-Type': 'application/json',
        },
      });
    }

    // Check if response is SSE stream
    const contentTypeHeader = response.headers.get('content-type');
    const isSSE = contentTypeHeader?.includes('text/event-stream');

    if (isSSE) {
      // Create a ReadableStream to proxy the SSE stream
      const stream = new ReadableStream({
        async start(controller) {
          const reader = response.body?.getReader();
          if (!reader) {
            controller.close();
            return;
          }

          try {
            while (true) {
              const { done, value } = await reader.read();
              
              if (done) {
                controller.close();
                break;
              }

              // Forward the chunk to the client
              controller.enqueue(value);
            }
          } catch (error) {
            console.error('SSE stream error:', error);
            controller.error(error);
          }
        },
      });

      // Return streaming response
      return new Response(stream, {
        status: response.status,
        statusText: response.statusText,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
          // Don't forward Set-Cookie from backend - cookies are handled by auth proxy
        },
      });
    } else {
      // Non-streaming response
      const responseBody = await response.text();
      return new Response(responseBody, {
        status: response.status,
        statusText: response.statusText,
        headers: {
          'Content-Type': response.headers.get('content-type') || 'application/json',
        },
      });
    }
  } catch (error) {
    console.error('ChatKit proxy error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error', detail: error instanceof Error ? error.message : 'Unknown error' }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
  }
}

