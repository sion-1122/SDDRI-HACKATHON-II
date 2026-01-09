/* Auth API route - Proxy to FastAPI backend.

[Task]: T019
[From]: specs/001-user-auth/quickstart.md

This route proxies authentication requests to the FastAPI backend.
All actual authentication logic is handled by the FastAPI backend.

Endpoints proxied:
- POST /api/auth/sign-in - User login
- POST /api/auth/sign-up - User registration
- POST /api/auth/sign-out - User logout
- GET /api/auth/session - Get current session
*/
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  return proxyRequest(request);
}

export async function POST(request: NextRequest) {
  return proxyRequest(request);
}

async function proxyRequest(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const backendUrl = `${BACKEND_URL}/api/auth${url.pathname.replace('/api/auth', '')}${url.search}`;

    // Prepare headers
    const headers = new Headers();
    request.headers.forEach((value, key) => {
      headers.set(key, value);
    });

    // Proxy the request to FastAPI backend
    const response = await fetch(backendUrl, {
      method: request.method,
      headers,
      body: request.body,
      // Include cookies for session management
      credentials: 'include',
    });

    // Return the response from FastAPI
    return new NextResponse(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
  } catch (error) {
    console.error('Auth proxy error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}