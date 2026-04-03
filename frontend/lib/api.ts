import {
  Candidate,
  CandidateDetail,
  ChatResponse,
  CompareResponse,
  FormulaMemberDetail,
  FormulaProfile,
  PresidentialFormula,
  SearchResult,
  SimplifyResponse,
} from "@/lib/types";

const API_URL =
  (typeof window === "undefined"
    ? process.env.API_URL
    : process.env.NEXT_PUBLIC_API_URL) ?? "http://localhost:8000/api";

async function request<T>(
  path: string,
  init?: RequestInit,
  revalidate: number | false = false,
): Promise<T> {
  const isPost = init?.method === "POST";
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    // Server-side: use ISR revalidation for GETs, no-store for POSTs
    ...(typeof window === "undefined" && !isPost && revalidate !== false
      ? { next: { revalidate } }
      : { cache: "no-store" }),
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function getCandidates(): Promise<Candidate[]> {
  return request<Candidate[]>("/candidates", undefined, 3600);
}

export function getCandidate(candidateId: string | number): Promise<CandidateDetail> {
  return request<CandidateDetail>(`/candidate/${candidateId}`, undefined, 3600);
}

export function compareCandidates(leftId: string | number, rightId: string | number): Promise<CompareResponse> {
  return request<CompareResponse>(`/compare?c1=${leftId}&c2=${rightId}`, undefined, 3600);
}

export function searchContent(query: string): Promise<SearchResult[]> {
  return request<SearchResult[]>(`/search?q=${encodeURIComponent(query)}`, undefined, 60);
}

export function askAssistant(question: string): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

export function getShareImageUrl(leftId: string | number, rightId: string | number): string {
  return `${API_URL}/share-image?c1=${leftId}&c2=${rightId}`;
}

export function getFormulas(): Promise<PresidentialFormula[]> {
  return request<PresidentialFormula[]>("/formulas", undefined, 300);
}

export function simplifyText(text: string): Promise<SimplifyResponse> {
  return request<SimplifyResponse>("/simplify", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function getFormulaProfiles(): Promise<FormulaProfile[]> {
  return request<FormulaProfile[]>("/formula-profiles", undefined, 3600);
}

export function getFormulaMemberDetail(id: number): Promise<FormulaMemberDetail> {
  return request<FormulaMemberDetail>(`/formula-members/${id}`, undefined, 3600);
}

export function getFormulaMemberByName(name: string): Promise<FormulaMemberDetail | null> {
  return request<FormulaMemberDetail>(`/formula-members/by-name/${encodeURIComponent(name)}`, undefined, 3600).catch(() => null);
}
