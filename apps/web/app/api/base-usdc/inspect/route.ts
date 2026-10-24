import { NextResponse } from "next/server";

export const runtime = "nodejs";

const API_URL = (process.env.BIZLENS_API_URL || "http://localhost:8000").replace(/\/$/, "");

export async function POST(request: Request) {
  try {
    const payload = await request.json();
    const response = await fetch(`${API_URL}/base-usdc/inspect`, {
      method: "POST",
      cache: "no-store",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    return NextResponse.json(result, {
      status: response.status, headers: { "Cache-Control": "no-store" },
    });
  } catch {
    return NextResponse.json(
      { success: false, error: "Unable to inspect Base evidence through BizLens API." },
      { status: 502, headers: { "Cache-Control": "no-store" } },
    );
  }
}
