import { NextResponse } from "next/server";

export const runtime = "nodejs";

const API_URL = (process.env.BIZLENS_API_URL || "http://localhost:8000").replace(/\/$/, "");
const MAX_INSPECTION_BYTES = 2048;

function reject(status: number, error: string) {
  return NextResponse.json(
    { success: false, error },
    { status, headers: { "Cache-Control": "no-store" } },
  );
}

async function boundedJson(request: Request): Promise<unknown> {
  // Prevent streaming/chunked or forged Content-Length from bypassing the cap.
  const reader = request.body?.getReader();
  if (!reader) throw new Error("Invalid empty inspection request.");
  const decoder = new TextDecoder("utf-8", { fatal: true });
  let size = 0;
  let text = "";
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > MAX_INSPECTION_BYTES) throw new RangeError("Request exceeds 2KB limit.");
      text += decoder.decode(value, { stream: true });
    }
    text += decoder.decode();
  } finally {
    reader.releaseLock();
  }
  return JSON.parse(text) as unknown;
}

export async function POST(request: Request) {
  const mediaType = request.headers.get("content-type")?.split(";")[0].trim().toLowerCase();
  if (mediaType !== "application/json") {
    return reject(415, "The inspection request must be JSON.");
  }
  const declaredSize = request.headers.get("content-length");
  if (declaredSize && Number(declaredSize) > MAX_INSPECTION_BYTES) {
    return reject(413, "Inspection request is too large.");
  }

  let payload: unknown;
  try {
    payload = await boundedJson(request);
  } catch (error) {
    return error instanceof RangeError
      ? reject(413, "Inspection request is too large.")
      : reject(400, "Invalid inspection JSON.");
  }

  try {
    // Explicitly proxy only to the trusted backend, never a user-supplied host.
    const response = await fetch(`${API_URL}/base-usdc/inspect`, {
      method: "POST",
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
        ...(request.headers.get("x-bizlens-rpc-key")
          ? { "X-BizLens-Rpc-Key": request.headers.get("x-bizlens-rpc-key")! }
          : {}),
      },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    return NextResponse.json(result, {
      status: response.status, headers: { "Cache-Control": "no-store" },
    });
  } catch {
    return reject(502, "Unable to inspect Base evidence through BizLens API.");
  }
}
