export type Experience = { empresa: string | null; cargo: string | null; descricao: string };
export type MatchGap = { requisito: string; evidencia: string; prioridade: "alta" | "media" | "baixa" };
export type Question = { slug: string; title: string; difficulty: "Easy" | "Medium" | "Hard"; tags: string[]; content_md: string };
export type DiagnosticQuestion = { id: string; ordem: number; texto: string; competencia: string; categoria: "competência da vaga" | "raciocínio algorítmico" };
export type DiagnosticAnswer = { question_id: string; tipo: "texto" | "nao_sei" | "nao_se_aplica"; texto: string | null };
export type Assessment = { question_id: string; competencia: string; nivel_observado: string; nivel_esperado: string; confianca: string; importancia: string; evidencia_resumida: string; classificacao: string; proximo_foco: string };
export type Recommendation = { papel: "aquecimento" | "nível-alvo" | "extensão"; prioridade_atendida: string; justificativa: string; desafio: Question };
export type Preparation = {
  id: string; created_at: string; status: "criacao_em_processamento" | "aguardando_diagnostico" | "avaliacao_em_processamento" | "pronta" | "pronta_modo_degradado";
  job: { titulo: string; pre_requisitos: string; responsabilidades: string };
  candidate: { nome: string | null; resumo: string; habilidades: string[]; experiencias: Experience[]; formacao: string[] };
  match: { aderencia: number; resumo: string; pontos_fortes: string[]; lacunas: MatchGap[]; focos_de_preparacao: string[] };
  algorithm_profile: { tags: string[]; difficulty: "Easy" | "Medium" | "Hard" };
  diagnostic_questions: DiagnosticQuestion[]; answers: Record<string, DiagnosticAnswer>; assessments: Assessment[];
  readiness: { aderencia_curricular: number; prontidao_tecnica: number | null; indice_preparacao: number | null; evidencias_validas: number; baseline: boolean } | null;
  priorities: { ordem: number; competencia: string; motivo: string; proximo_passo: string }[];
  recommendations: Recommendation[]; questions: Question[];
};
export type ChatMessage = { role: "assistant" | "user"; content: string };
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try { response = await fetch(`${API_BASE_URL}${path}`, init); } catch { throw new Error("Não foi possível acessar a API."); }
  if (!response.ok) { let detail = ""; try { const body = await response.json(); detail = typeof body.detail === "string" ? body.detail : ""; } catch { /* noop */ } throw new Error(detail || `A API retornou ${response.status}.`); }
  return response.json() as Promise<T>;
}
function normalize(data: Omit<Preparation, "questions"> & { questions?: Question[] }): Preparation { return { ...data, questions: data.recommendations.map((item) => item.desafio) }; }
export async function createPreparation(jobUrl: string, cv: File): Promise<Preparation> { const form = new FormData(); form.append("job_url", jobUrl); form.append("cv", cv); return normalize(await request<Preparation>("/api/v1/preparations", { method: "POST", body: form })); }
export async function getPreparation(id: string): Promise<Preparation> { return normalize(await request<Preparation>(`/api/v1/preparations/${id}`)); }
export async function saveDiagnosticAnswer(id: string, questionId: string, answer: { tipo: DiagnosticAnswer["tipo"]; texto?: string }): Promise<Preparation> { return normalize(await request<Preparation>(`/api/v1/preparations/${id}/diagnostic/answers/${questionId}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(answer) })); }
export async function submitDiagnostic(id: string): Promise<Preparation> { return normalize(await request<Preparation>(`/api/v1/preparations/${id}/diagnostic/submit`, { method: "POST" })); }
export async function retryDiagnostic(id: string): Promise<Preparation> { return normalize(await request<Preparation>(`/api/v1/preparations/${id}/diagnostic/retry`, { method: "POST" })); }
export async function getMentorship(id: string, challengeSlug: string): Promise<{ messages: { role: "assistant" | "user"; content: string }[] }> { return request(`/api/v1/preparations/${id}/mentorships/${challengeSlug}`); }
export async function sendMentorMessage(preparationId: string, challengeSlug: string, message: string): Promise<string> { const response = await request<{ message: ChatMessage }>(`/api/v1/preparations/${preparationId}/messages`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ challenge_slug: challengeSlug, message }) }); return response.message.content; }
