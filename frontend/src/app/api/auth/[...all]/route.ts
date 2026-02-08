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

// Read backend URL dynamically to ensure it's available at runtime
function getBackendUrl(): string {
  const backendUrl = process.env.NEXT_PUBLIC_API_URL;
  
  // Log in development to help debug
  if (process.env.NODE_ENV === 'development') {
    console.log('[Auth Proxy] Backend URL:', backendUrl);
  }
  
  return backendUrl;
}

export async function GET(request: NextRequest) {
  return proxyRequest(request);
}

export async function POST(request: NextRequest) {
  return proxyRequest(request);
}

async function proxyRequest(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const BACKEND_URL = getBackendUrl();
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
    let body: string | null = null;
    if (request.method === 'POST' || request.method === 'PUT' || request.method === 'PATCH') {
      try {
        // Read the request body as text
        body = await request.text();
      } catch (e) {
        // If body is empty or unreadable, set to null
        body = null;
      }
    }

    // Proxy the request to FastAPI backend
    const response = await fetch(backendUrl, {
      method: request.method,
      headers,
      body: body || undefined,
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

    // Determine if we're in a secure context (HTTPS or production)
    const isProduction = process.env.NODE_ENV === 'production';
    const isSecure = isProduction || request.url.startsWith('https://');

    // Forward Set-Cookie headers, but adjust domain/path/secure settings for frontend
    for (const cookie of setCookieHeaders) {
      try {
        // Parse the cookie string
        const parts = cookie.split(';');
        const [cookiePart, ...attributes] = parts;
        
        // Handle cookie name=value (value may be empty for deletion)
        const equalsIndex = cookiePart.indexOf('=');
        if (equalsIndex === -1) {
          // Invalid cookie format, skip
          continue;
        }
        
        const name = cookiePart.substring(0, equalsIndex).trim();
        const value = cookiePart.substring(equalsIndex + 1).trim();
        
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
            const maxAgeStr = trimmed.split('=')[1].trim();
            const maxAge = parseInt(maxAgeStr, 10);
            if (!isNaN(maxAge)) {
              cookieOptions.maxAge = maxAge;
            }
          } else if (trimmed.startsWith('expires=')) {
            // Handle Expires attribute (for cookie deletion, backend might use this)
            // If Expires is in the past, treat as deletion (maxAge: 0)
            try {
              const expiresStr = trimmed.split('=')[1].trim();
              const expiresDate = new Date(expiresStr);
              if (expiresDate.getTime() < Date.now()) {
                // Cookie is expired, set maxAge to 0 to delete
                cookieOptions.maxAge = 0;
              }
            } catch (e) {
              // Invalid date, ignore
            }
          } else if (trimmed.startsWith('path=')) {
            const pathValue = trimmed.split('=')[1].trim();
            cookieOptions.path = pathValue;
          }
        }

        // Handle cookie deletion: if maxAge is 0 or negative, delete the cookie
        if (cookieOptions.maxAge !== undefined && cookieOptions.maxAge <= 0) {
          nextResponse.cookies.delete(name, {
            path: cookieOptions.path ?? '/',
            sameSite: cookieOptions.sameSite ?? 'lax',
          });
        } else {
          // Set cookie with frontend-appropriate settings
          // Don't set domain - let browser use default (current domain)
          nextResponse.cookies.set(name, value, {
            httpOnly: cookieOptions.httpOnly ?? true,
            secure: cookieOptions.secure ?? isSecure,
            sameSite: cookieOptions.sameSite ?? 'lax',
            maxAge: cookieOptions.maxAge,
            path: cookieOptions.path ?? '/',
            // Don't set domain - browser will use current domain
          });
        }
      } catch (parseError) {
        // If cookie parsing fails, log but continue with other cookies
        console.warn('Failed to parse cookie:', cookie, parseError);
      }
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