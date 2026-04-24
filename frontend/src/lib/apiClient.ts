const rawApiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

function normalizeApiBase(url: string) {
  const trimmed = url.replace(/\/+$/, "");
  return trimmed.endsWith("/api") ? trimmed : `${trimmed}/api`;
}

const API_BASE_URL = normalizeApiBase(rawApiUrl);

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
};

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);

  let body: BodyInit | undefined;
  if (options.body !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(options.body);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    body,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

async function readErrorMessage(response: Response) {
  try {
    const data = (await response.json()) as { detail?: string };
    return data.detail || "Nao foi possivel concluir a requisicao.";
  } catch {
    return "Nao foi possivel concluir a requisicao.";
  }
}
