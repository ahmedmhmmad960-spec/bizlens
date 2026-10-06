import { NextResponse } from "next/server";

export const runtime = "nodejs";

const API_URL = (process.env.BIZLENS_API_URL || "http://localhost:8000").replace(/\/$/, "");

export async function POST(request: Request) {
  try {
    const body = await request.text();
    const response = await fetch(`${API_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      cache: "no-store",
    });

    const payload = await response.json();
    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unable to reach the BizLens API.",
      },
      { status: 502 },
    );
  }
}
