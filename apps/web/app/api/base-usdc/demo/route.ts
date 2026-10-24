import { NextResponse } from "next/server";

export const runtime = "nodejs";

const API_URL = (process.env.BIZLENS_API_URL || "http://localhost:8000").replace(/\/$/, "");

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/base-usdc/demo`, { cache: "no-store" });
    const payload = await response.json();
    return NextResponse.json(payload, {
      status: response.status, headers: { "Cache-Control": "no-store" },
    });
  } catch {
    return NextResponse.json(
      { success: false, error: "Unable to reach the evidence API." },
      { status: 502, headers: { "Cache-Control": "no-store" } },
    );
  }
}
