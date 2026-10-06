import { NextResponse } from "next/server";

export const runtime = "nodejs";

const API_URL = (process.env.BIZLENS_API_URL || "http://localhost:8000").replace(/\/$/, "");

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const response = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      body: formData,
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
