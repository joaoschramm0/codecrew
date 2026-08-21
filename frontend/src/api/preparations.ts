export type Experience = {
  empresa: string | null;
  cargo: string | null;
  descricao: string;
};

export type MatchGap = {
  requisito: string;
  evidencia: string;
  prioridade: "alta" | "media" | "baixa";
};

export type Question = {
  slug: string;
  title: string;
  difficulty: "Easy" | "Medium" | "Hard";
  tags: string[];
  content_md: string;
};

export type Preparation = {
  id: string;
  created_at: string;
  job: {
    titulo: string;
    pre_requisitos: string;
    responsabilidades: string;
  };
  candidate: {
    nome: string | null;
    resumo: string;
    habilidades: string[];
    experiencias: Experience[];
    formacao: string[];
  };
  match: {
    aderencia: number;
    resumo: string;
    pontos_fortes: string[];
    lacunas: MatchGap[];
    focos_de_preparacao: string[];
  };
  algorithm_profile: {
    tags: string[];
    difficulty: "Easy" | "Medium" | "Hard";
  };
  questions: Question[];
};

export type ChatMessage = {
  role: "assistant" | "user";
  content: string;
};

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const payload = await response.json();
    if (typeof payload.detail === "string") return payload.detail;
    if (Array.isArray(payload.detail)) {
      return payload.detail
        .map((item: { msg?: string }) => item.msg)
        .filter(Boolean)
        .join(" ");
    }
  } catch {
    return "";
  }
  return "";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init);
  } catch {
    throw new Error("Não foi possível acessar a API. Confirme se o FastAPI está rodando.");
  }

  if (!response.ok) {
    const detail = await getErrorMessage(response);
    throw new Error(detail || `A API retornou o status ${response.status}.`);
  }
  return response.json() as Promise<T>;
}

export function createPreparation(
  jobUrl: string,
  cv: File,
  questionLimit = 10,
): Promise<Preparation> {
  const form = new FormData();
  form.append("job_url", jobUrl);
  form.append("cv", cv);
  form.append("question_limit", String(questionLimit));

  return request<Preparation>("/api/v1/preparations", {
    method: "POST",
    body: form,
  });
}

export async function sendMentorMessage(
  preparationId: string,
  messages: ChatMessage[],
): Promise<string> {
  const response = await request<{ message: string }>(
    `/api/v1/preparations/${preparationId}/messages`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: messages.slice(-12) }),
    },
  );
  return response.message;
}
