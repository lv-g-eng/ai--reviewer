import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

// Use BACKEND_URL for server-side (Docker network), fallback to NEXT_PUBLIC_BACKEND_URL for local dev
const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const error = searchParams.get('error');
    const errorDescription = searchParams.get('error_description');

    // Log for debugging
    console.log('[GitHub Callback] Received:', { code: !!code, state, error, errorDescription });

    if (error) {
      console.error('[GitHub Callback] OAuth error:', error, errorDescription);
      return NextResponse.redirect(
        new URL(`/projects?error=${encodeURIComponent(error)}&error_description=${encodeURIComponent(errorDescription || '')}`, request.url)
      );
    }

    if (!code) {
      console.error('[GitHub Callback] No code received');
      return NextResponse.redirect(
        new URL('/projects?error=no_code', request.url)
      );
    }

    const cookieStore = await cookies();
    const accessToken = cookieStore.get('access_token')?.value;

    if (!accessToken) {
      console.error('[GitHub Callback] No access token in cookies');
      return NextResponse.redirect(
        new URL('/login?returnUrl=/projects', request.url)
      );
    }

    console.log('[GitHub Callback] Exchanging code for GitHub token...');
    console.log('[GitHub Callback] Backend URL:', BACKEND_URL);
    
    // Exchange code for GitHub token via backend
    const response = await fetch(`${BACKEND_URL}/api/v1/github/connect`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });

    console.log('[GitHub Callback] Backend response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('[GitHub Callback] Backend error:', errorData);
      
      // Extract detailed error message
      const errorDetail = errorData.detail || 'Unknown error';
      const errorMessage = typeof errorDetail === 'string' 
        ? errorDetail 
        : JSON.stringify(errorDetail);
      
      console.error('[GitHub Callback] Error detail:', errorMessage);
      
      return NextResponse.redirect(
        new URL(`/projects?error=github_connection_failed&error_detail=${encodeURIComponent(errorMessage)}`, request.url)
      );
    }

    const data = await response.json();
    console.log('[GitHub Callback] Connection successful:', data);

    // Redirect back to projects page with success flag
    return NextResponse.redirect(
      new URL('/projects?github_connected=true', request.url)
    );
  } catch (error) {
    console.error('[GitHub Callback] Unexpected error:', error);
    return NextResponse.redirect(
      new URL('/projects?error=internal_error', request.url)
    );
  }
}
