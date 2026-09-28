export interface DocumentSummary {
  document_id: string;
  filename: string;
  chunks: number;
}

export interface Citation {
  document_id: string;
  filename: string;
  chunk: number;
  excerpt: string;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
}

const API_BASE = import.meta.env.VITE_API_URL ?? "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body.detail ?? message;
    } catch {
      // The API returned a non-JSON error.
    }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  listDocuments: () => request<DocumentSummary[]>("/api/documents"),
  uploadDocument: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<DocumentSummary & { message: string }>("/api/documents", {
      method: "POST",
      body: form,
    });
  },
  deleteDocument: (id: string) =>
    request<void>(`/api/documents/${id}`, { method: "DELETE" }),
  query: (question: string) =>
    request<QueryResponse>("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    }),
};
