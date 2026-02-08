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

    // Get request body if it exists
    let body: ReadableStream | null = null;
    if (request.method === 'POST' || request.method === 'PUT' || request.method === 'PATCH') {
      body = request.body;
    }

    // Proxy the request to FastAPI backend
    const response = await fetch(backendUrl, {
      method: request.method,
      headers,
      body,
      // Include cookies for session management
      credentials: 'include',
    });

    // Get response body
    const responseBody = await response.text();

    // Create response headers (excluding Set-Cookie which we'll handle separately)
    const responseHeaders = new Headers();
    response.headers.forEach((value, key) => {
      // Skip Set-Cookie header - we'll process it separately
      if (key.toLowerCase() !== 'set-cookie') {
        responseHeaders.set(key, value);
      }
    });

    // Create NextResponse
    const nextResponse = new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });

    // Process Set-Cookie headers from backend and rewrite them for the frontend domain
    // Extract all Set-Cookie headers (there may be multiple)
    const setCookieHeaders: string[] = [];
    response.headers.forEach((value, key) => {
      if (key.toLowerCase() === 'set-cookie') {
        setCookieHeaders.push(value);
      }
    });

    // Forward Set-Cookie headers, but adjust domain/path/secure settings for frontend
    for (const cookie of setCookieHeaders) {
      // Parse the cookie string
      const parts = cookie.split(';');
      const [cookiePart, ...attributes] = parts;
      const nameValue = cookiePart.split('=');
      if (nameValue.length < 2) continue;
      
      const name = nameValue[0].trim();
      const value = nameValue.slice(1).join('='); // Handle values that contain '='
      
      // Extract cookie attributes
      const cookieOptions: {
        httpOnly?: boolean;
        secure?: boolean;
        sameSite?: 'strict' | 'lax' | 'none';
        maxAge?: number;
        path?: string;
      } = {};

      for (const attr of attributes) {
        const trimmed = attr.trim().toLowerCase();
        if (trimmed === 'httponly') {
          cookieOptions.httpOnly = true;
        } else if (trimmed === 'secure') {
          cookieOptions.secure = true;
        } else if (trimmed.startsWith('samesite=')) {
          const sameSiteValue = trimmed.split('=')[1].trim().toLowerCase();
          if (['strict', 'lax', 'none'].includes(sameSiteValue)) {
            cookieOptions.sameSite = sameSiteValue as 'strict' | 'lax' | 'none';
          }
        } else if (trimmed.startsWith('max-age=')) {
          const maxAge = parseInt(trimmed.split('=')[1].trim(), 10);
          if (!isNaN(maxAge)) {
            cookieOptions.maxAge = maxAge;
          }
        } else if (trimmed.startsWith('path=')) {
          cookieOptions.path = trimmed.split('=')[1].trim();
        }
      }

      // Set cookie with frontend-appropriate settings
      // Don't set domain - let browser use default (current domain)
      // In production, ensure secure is true if request is HTTPS
      const isProduction = process.env.NODE_ENV === 'production';
      const isSecure = isProduction || request.url.startsWith('https://');
      
      nextResponse.cookies.set(name, value, {
        httpOnly: cookieOptions.httpOnly ?? true,
        secure: cookieOptions.secure ?? isSecure,
        sameSite: cookieOptions.sameSite ?? 'lax',
        maxAge: cookieOptions.maxAge,
        path: cookieOptions.path ?? '/',
        // Don't set domain - browser will use current domain
      });
    }

    return nextResponse;
  } catch (error) {
    console.error('Auth proxy error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}