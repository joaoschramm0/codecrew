import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  BrainCircuit,
  BriefcaseBusiness,
  Check,
  ChevronDown,
  ChevronUp,
  CircleGauge,
  Code2,
  FileText,
  ExternalLink,
  HelpCircle,
  Link2,
  LockKeyhole,
  MessageCircle,
  RefreshCw,
  RotateCcw,
  Rocket,
  Send,
  Target,
  Trophy,
  Upload,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
  type CSSProperties,
  type DragEvent,
  type FormEvent,
  type ReactNode,
} from "react";
import {
  createPreparation,
  getPreparation,
  getMentorship,
  saveDiagnosticAnswer,
  sendMentorMessage,
  submitDiagnostic,
  retryDiagnostic,
  type ChatMessage,
  type Preparation,
  type Question,
} from "./api/preparations";

type Screen = "onboarding" | "loading" | "diagnostic" | "evaluation-recovery" | "stories" | "workspace";
type WorkspaceTab = "chat" | "topics" | "challenges";
type LoadStatus = "pending" | "success" | "error";
type Submission = { jobUrl: string; cv: File };

function Brand() {
  return (
    <div className="brand" aria-label="CodeCrew">
      <span className="brand__mark"><img src="/codecrew-robot.webp" alt="" /></span>
      <span>CodeCrew</span>
    </div>
  );
}

function Onboarding({ onSubmit }: { onSubmit: (submission: Submission) => void }) {
  const [jobUrl, setJobUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  function chooseFile(selected?: File) {
    if (!selected) return;
    if (!selected.name.toLowerCase().endsWith(".pdf")) {
      setError("Escolha um currículo no formato PDF.");
      return;
    }
    setFile(selected);
    setError("");
  }

  function handleFile(event: ChangeEvent<HTMLInputElement>) {
    chooseFile(event.target.files?.[0]);
  }

  function handleDrop(event: DragEvent<HTMLButtonElement>) {
    event.preventDefault();
    setDragging(false);
    chooseFile(event.dataTransfer.files?.[0]);
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!jobUrl.trim() || !file) {
      setError("Informe a vaga e adicione seu currículo para continuar.");
      return;
    }
    onSubmit({ jobUrl: jobUrl.trim(), cv: file });
  }

  return (
    <main className="onboarding page-shell">
      <header className="topbar">
        <Brand />
        <button className="icon-button icon-button--ghost" type="button" aria-label="Como funciona" title="Como funciona" onClick={() => document.getElementById("como-funciona")?.scrollIntoView({ behavior: "smooth", block: "center" })}>
          <HelpCircle size={20} />
        </button>
      </header>

      <section className="onboarding__content">
        <div className="hero-copy">
          <h1>Prepare-se para a vaga que você realmente quer.</h1>
          <p>
            Seu currículo e uma vaga real viram uma preparação feita para você,
            com foco no que mais importa agora.
          </p>

          <div className="benefits" id="como-funciona">
            <div className="benefit">
              <span><Target size={20} /></span>
              <strong>Diagnóstico personalizado</strong>
            </div>
            <div className="benefit">
              <span><CircleGauge size={20} /></span>
              <strong>Foco nas suas lacunas</strong>
            </div>
            <div className="benefit">
              <span><Rocket size={20} /></span>
              <strong>Treino direcionado</strong>
            </div>
          </div>
        </div>

        <form className="onboarding-card" onSubmit={handleSubmit}>
          <div className="card-heading">
            <h2>Comece sua preparação</h2>
          </div>

          <label className="field-label" htmlFor="job-url">URL da vaga</label>
          <div className="input-wrap">
            <Link2 size={19} />
            <input
              id="job-url"
              type="url"
              value={jobUrl}
              onChange={(event) => setJobUrl(event.target.value)}
              placeholder="https://empresa.gupy.io/job/..."
            />
          </div>

          <label className="field-label">Currículo em PDF</label>
          <button
            className={`dropzone ${dragging ? "dropzone--dragging" : ""} ${file ? "dropzone--ready" : ""}`}
            type="button"
            onClick={() => inputRef.current?.click()}
            onDragEnter={() => setDragging(true)}
            onDragLeave={() => setDragging(false)}
            onDragOver={(event) => event.preventDefault()}
            onDrop={handleDrop}
          >
            <span className="dropzone__icon">{file ? <Check size={25} /> : <Upload size={25} />}</span>
            <strong>{file ? file.name : "Arraste seu currículo aqui"}</strong>
            <small>{file ? "Arquivo pronto para análise" : "ou clique para selecionar um arquivo"}</small>
          </button>
          <input ref={inputRef} hidden type="file" accept="application/pdf,.pdf" onChange={handleFile} />

          {error && <p className="form-error">{error}</p>}

          <div className="privacy-note"><LockKeyhole size={14} /> Seu PDF não fica armazenado.</div>
          <button className="primary-button" type="submit">
            Iniciar preparação <ArrowRight size={19} />
          </button>
        </form>
      </section>
    </main>
  );
}

const loadingSteps = [
  { label: "Vaga encontrada", icon: BriefcaseBusiness },
  { label: "Currículo processado", icon: FileText },
  { label: "Perfil comparado", icon: Target },
  { label: "Montando sua preparação", icon: BrainCircuit },
  { label: "Selecionando desafios", icon: Trophy },
];

type LoadingScreenProps = {
  submission: Submission;
  preparation: Preparation | null;
  status: LoadStatus;
  error: string;
  onRetry: () => void;
  onBack: () => void;
};

function LoadingScreen({
  submission,
  preparation,
  status,
  error,
  onRetry,
  onBack,
}: LoadingScreenProps) {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    if (status === "success") {
      setActiveStep(loadingSteps.length - 1);
      return;
    }
    if (status !== "pending") return;

    setActiveStep(0);

    const interval = window.setInterval(() => {
      setActiveStep((current) => Math.min(current + 1, loadingSteps.length - 2));
    }, 1400);
    return () => window.clearInterval(interval);
  }, [status]);

  return (
    <main className="loading page-shell">
      <header className="topbar"><Brand /></header>
      <section className="loading__content">
        <h1>{status === "error" ? "Não conseguimos concluir a análise" : "Estamos preparando seu treino"}</h1>
        <p>{status === "error" ? error : "Cruzando a vaga com seu currículo para encontrar o melhor ponto de partida."}</p>

        <div
          className="progress-card"
          aria-label={status === "error" ? "A análise foi interrompida" : `Etapa ${activeStep + 1} de ${loadingSteps.length}: ${loadingSteps[activeStep].label}`}
          aria-live="polite"
        >
          <div className="progress-line" aria-hidden="true"><span style={{ width: `${activeStep * 25}%` }} /></div>
          {loadingSteps.map((step, index) => {
            const Icon = step.icon;
            const completed = index < activeStep;
            const active = status !== "error" && index === activeStep;
            return (
              <div className={`progress-step ${completed ? "is-complete" : ""} ${active ? "is-active" : ""}`} key={step.label}>
                <span className="progress-step__icon">{completed ? <Check size={21} /> : <Icon size={21} />}</span>
                <strong>{step.label}</strong>
              </div>
            );
          })}
        </div>

        <div className="processing-summary">
          <div><BriefcaseBusiness size={19} /><span><small>Vaga</small><strong>{preparation?.job.titulo ?? "Processando URL informada"}</strong></span></div>
          <div><FileText size={19} /><span><small>Currículo</small><strong>{submission.cv.name}</strong></span></div>
        </div>
        {status === "error" ? (
          <div className="loading-actions">
            <button className="primary-button" type="button" onClick={onRetry}><RefreshCw size={18} />Tentar novamente</button>
            <button className="secondary-button" type="button" onClick={onBack}><ArrowLeft size={18} />Revisar dados</button>
          </div>
        ) : (
          <p className="loading-note">
            Sua preparação aparecerá automaticamente
            <span className="loading-dots" aria-hidden="true"><i /><i /><i /></span>
          </p>
        )}
      </section>
    </main>
  );
}

function DiagnosticScreen({ preparation, onChange, onComplete }: { preparation: Preparation; onChange: (value: Preparation) => void; onComplete: (value: Preparation) => void }) {
  const [index, setIndex] = useState(0);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const question = preparation.diagnostic_questions[index];
  const saved = preparation.answers[question.id];
  const [text, setText] = useState(saved?.texto ?? "");
  const [type, setType] = useState<"texto" | "nao_sei" | "nao_se_aplica">(saved?.tipo ?? "texto");

  useEffect(() => { const answer = preparation.answers[question.id]; setText(answer?.texto ?? ""); setType(answer?.tipo ?? "texto"); }, [question.id, preparation.answers]);

  async function saveAndMove(next: number): Promise<boolean> {
    const clean = text.trim();
    if (type === "texto" && !clean) { setError("Escreva uma resposta ou selecione uma das opções."); return false; }
    setSaving(true); setError("");
    try { const updated = await saveDiagnosticAnswer(preparation.id, question.id, { tipo: type, texto: type === "texto" ? clean : undefined }); onChange(updated); setIndex(next); return true; }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Não foi possível salvar."); return false; }
    finally { setSaving(false); }
  }

  async function finish() {
    if (!await saveAndMove(index)) return;
    setSaving(true);
    try { const updated = await submitDiagnostic(preparation.id); onComplete(updated); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Não foi possível avaliar agora."); }
    finally { setSaving(false); }
  }

  return <main className="diagnostic page-shell"><header className="topbar"><Brand /><span>Diagnóstico técnico inicial</span></header><section className="diagnostic-card">
    <div className="diagnostic-progress"><strong>{index + 1} de 4</strong><span><i style={{ width: `${(index + 1) * 25}%` }} /></span></div>
    <p className="eyebrow">{question.categoria} · {question.competencia}</p><h1>{question.texto}</h1>
    <p className="safe-note"><LockKeyhole size={16} /> Isto serve somente para sua preparação, não para contratação. Suas respostas são privadas.</p>
    <textarea maxLength={1000} disabled={type !== "texto"} value={text} onChange={(event) => { setText(event.target.value); setType("texto"); }} placeholder="Explique brevemente seu raciocínio..." />
    <div className="answer-options"><label><input type="radio" checked={type === "nao_sei"} onChange={() => { setType("nao_sei"); setText(""); }} /> Não sei responder</label><label><input type="radio" checked={type === "nao_se_aplica"} onChange={() => { setType("nao_se_aplica"); setText(""); }} /> Esta pergunta não se aplica</label></div>
    {error && <p className="form-error">{error}</p>}<div className="diagnostic-actions"><button className="secondary-button" disabled={index === 0 || saving} onClick={() => saveAndMove(index - 1)}><ArrowLeft size={18} />Voltar</button>{index < 3 ? <button className="primary-button" disabled={saving} onClick={() => saveAndMove(index + 1)}>Salvar e continuar<ArrowRight size={18} /></button> : <button className="primary-button" disabled={saving} onClick={finish}>Confirmar e enviar<Check size={18} /></button>}</div>
  </section></main>;
}

function EvaluationRecovery({ preparation, onComplete }: { preparation: Preparation; onComplete: (value: Preparation) => void }) {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  async function retry() {
    setPending(true); setError("");
    try { onComplete(await retryDiagnostic(preparation.id)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Não foi possível retomar a avaliação."); }
    finally { setPending(false); }
  }
  return <main className="loading page-shell"><header className="topbar"><Brand /></header><section className="loading__content"><h1>A avaliação precisa ser retomada</h1><p>Suas quatro respostas estão salvas. Você pode tentar concluir o diagnóstico sem respondê-las novamente.</p>{error && <p className="form-error">{error}</p>}<button className="primary-button" type="button" disabled={pending} onClick={retry}><RefreshCw size={18} />{pending ? "Avaliando..." : "Retomar avaliação"}</button></section></main>;
}

type Story = {
  title: string;
  description: string;
  visual: ReactNode;
  action?: string;
};

function shortLabel(value: string, limit = 28) {
  return value.length > limit ? `${value.slice(0, limit - 1).trim()}…` : value;
}

function conciseSummary(value: string, limit = 125) {
  const normalized = value.replace(/\s+/g, " ").trim();
  if (normalized.length <= limit) return normalized;

  const firstSentenceEnd = normalized.search(/[.!?](?:\s|$)/);
  if (firstSentenceEnd >= 0 && firstSentenceEnd + 1 <= limit) {
    return normalized.slice(0, firstSentenceEnd + 1);
  }

  const excerpt = normalized.slice(0, limit + 1);
  const lastSpace = excerpt.lastIndexOf(" ");
  return `${excerpt.slice(0, lastSpace > limit * 0.65 ? lastSpace : limit).trim()}…`;
}

function buildStories(preparation: Preparation): Story[] {
  const { candidate, match, questions } = preparation;
  const readiness = preparation.readiness;
  const observed = preparation.assessments;
  const strengths = match.pontos_fortes.length
    ? match.pontos_fortes.slice(0, 3)
    : candidate.habilidades.slice(0, 3).length
      ? candidate.habilidades.slice(0, 3)
      : ["Perfil profissional processado"];
  const gaps = match.lacunas.slice(0, 3);
  const firstGap = gaps[0]?.requisito ?? match.focos_de_preparacao[0] ?? "entrevista técnica";
  const firstStrength = candidate.habilidades[0] ?? match.pontos_fortes[0] ?? "Sua experiência";
  const firstFocus = match.focos_de_preparacao[0] ?? `Revisar ${firstGap}`;
  const attentionItems = gaps.length
    ? gaps.map((gap) => gap.requisito)
    : match.focos_de_preparacao.slice(0, 3).length
      ? match.focos_de_preparacao.slice(0, 3)
      : ["Revisão geral da vaga"];

  return [
    {
      title: `Você tem ${match.aderencia}% de aderência com esta vaga.`,
      description: match.resumo,
      visual: (
        <div className="score-orbit" style={{ "--score": `${match.aderencia * 3.6}deg` } as CSSProperties}>
          <span>{match.aderencia}%</span><small>aderência</small>
        </div>
      ),
    },
    {
      title: readiness?.indice_preparacao != null ? `Seu Índice de preparação é ${readiness.indice_preparacao}.` : "Seu diagnóstico técnico ainda está incompleto.",
      description: readiness?.indice_preparacao != null ? `Baseline específico para esta vaga: ${readiness.aderencia_curricular}% de aderência curricular e ${readiness.prontidao_tecnica}% de prontidão técnica. É uma estimativa preparatória, não uma nota ou probabilidade de contratação.` : "Há evidência insuficiente para publicar prontidão técnica ou um índice composto.",
      visual: <div className="score-orbit" style={{ "--score": `${(readiness?.indice_preparacao ?? 0) * 3.6}deg` } as CSSProperties}><span>{readiness?.indice_preparacao ?? "—"}</span><small>baseline</small></div>,
    },
    {
      title: "Sua experiência já oferece bons pontos de conexão.",
      description: "Estes são os pontos mais relevantes encontrados no seu currículo para esta vaga.",
      visual: (
        <div className="story-list story-list--positive">
          {strengths.map((item) => <div key={item}><Check size={18} />{item}</div>)}
        </div>
      ),
    },
    {
      title: `${attentionItems.length} assuntos merecem atenção.`,
      description: "Eles aparecem na vaga e precisam ficar mais claros na sua preparação.",
      visual: (
        <div className="gap-stack">
          {attentionItems.map((item) => <div key={item}><strong>{item}</strong></div>)}
        </div>
      ),
    },
    {
      title: "Seu primeiro foco já está claro.",
      description: firstFocus,
      visual: <div className="path-visual"><span>{shortLabel(firstStrength)}</span><ArrowRight size={22} /><span>{shortLabel(firstGap)}</span><ArrowRight size={22} /><span>Entrevista</span></div>,
    },
    {
      title: "O nível observado foi comparado somente com o esperado para a vaga.",
      description: "Evidência curricular e evidência técnica permanecem separadas; confiança baixa não entra no cálculo.",
      visual: <div className="story-list">{observed.slice(0, 4).map((item) => <div key={item.question_id}><strong>{item.competencia}: {item.nivel_observado}</strong> · esperado {item.nivel_esperado} · confiança {item.confianca}</div>)}</div>,
    },
    {
      title: "Sua preparação começa agora.",
      description: "Seu mentor já conhece a vaga, seu perfil e os assuntos que precisam de atenção.",
      visual: (
        <div className="ready-grid">
          <div><MessageCircle size={22} /><strong>Mentor contextual</strong></div>
          <div><BookOpen size={22} /><strong>{match.focos_de_preparacao.length} assuntos</strong></div>
          <div><Trophy size={22} /><strong>{questions.length} desafios</strong></div>
        </div>
      ),
      action: "Conversar com meu mentor",
    },
  ];
}

function StoriesScreen({ preparation, onComplete }: { preparation: Preparation; onComplete: () => void }) {
  const [index, setIndex] = useState(0);
  const [direction, setDirection] = useState<"forward" | "backward">("forward");
  const stories = useMemo(() => buildStories(preparation), [preparation]);
  const story = stories[index];

  const previous = useCallback(() => {
    setDirection("backward");
    setIndex((current) => Math.max(0, current - 1));
  }, []);
  const next = useCallback(() => {
    if (index === stories.length - 1) onComplete();
    else {
      setDirection("forward");
      setIndex((current) => current + 1);
    }
  }, [index, onComplete, stories.length]);

  function openStory(itemIndex: number) {
    setDirection(itemIndex < index ? "backward" : "forward");
    setIndex(itemIndex);
  }

  useEffect(() => {
    function handleKey(event: KeyboardEvent) {
      if (event.key === "ArrowLeft") previous();
      if (event.key === "ArrowRight") next();
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [next, previous]);

  return (
    <main className="stories page-shell">
      <header className="topbar"><Brand /></header>
      <div className="story-progress">
        {stories.map((item, itemIndex) => <button key={item.title} type="button" className={itemIndex <= index ? "is-filled" : ""} onClick={() => openStory(itemIndex)} aria-label={`Abrir resumo ${itemIndex + 1}`} aria-current={itemIndex === index ? "step" : undefined} />)}
      </div>

      <section className={`story-card story-card--${direction}`} key={story.title}>
        <div className="story-copy">
          <h1>{story.title}</h1>
          <p>{story.description}</p>
        </div>
        <div className="story-visual">{story.visual}</div>
      </section>

      <div className="story-controls">
        <button className="icon-button" type="button" onClick={previous} disabled={index === 0} aria-label="Resumo anterior"><ArrowLeft size={20} /></button>
        <button className={story.action ? "primary-button story-action" : "next-button"} type="button" onClick={next}>
          {story.action ?? "Continuar"} <ArrowRight size={19} />
        </button>
      </div>
    </main>
  );
}

function MentorIcon() {
  return <span className="mentor-icon"><img src="/codecrew-robot.webp" alt="" /></span>;
}

function ChatPanel({ preparation, challengeSlug }: { preparation: Preparation; challengeSlug: string }) {
  const firstGap = preparation.match.lacunas[0]?.requisito;
  const welcomeMessage = useMemo(() => [
    `Analisei sua candidatura para **${preparation.job.titulo}**.`,
    preparation.match.resumo,
    firstGap
      ? `Sugiro começarmos por **${firstGap}**. Como você quer treinar?`
      : "Como você quer começar sua preparação?",
  ].join("\n\n"), [firstGap, preparation.job.titulo, preparation.match.resumo]);
  const quickActions = useMemo(() => [
    {
      label: firstGap ? `Revisar ${shortLabel(firstGap, 22)}` : "Revisar pontos principais",
      prompt: firstGap ? `Quero revisar ${firstGap}.` : "Quero revisar os principais pontos da vaga.",
      icon: BookOpen,
    },
    { label: "Simular entrevista", prompt: "Simule uma entrevista comigo.", icon: MessageCircle },
    { label: "Montar plano de estudo", prompt: "Monte um plano de estudo para mim.", icon: CircleGauge },
    { label: "Resolver um desafio", prompt: "Quero resolver um desafio.", icon: Trophy },
  ], [firstGap]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [typing, setTyping] = useState(false);
  const [historyReady, setHistoryReady] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let active = true;
    setHistoryReady(false);
    getMentorship(preparation.id, challengeSlug)
      .then((value) => { if (active) setMessages(value.messages.map(({ role, content }) => ({ role, content }))); })
      .catch(() => { if (active) setMessages([]); })
      .finally(() => { if (active) setHistoryReady(true); });
    return () => { active = false; };
  }, [challengeSlug, preparation.id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, typing]);

  async function send(content = draft) {
    const message = content.trim();
    if (!message || typing || !historyReady) return;
    const nextMessages: ChatMessage[] = [...messages, { role: "user", content: message }];
    setMessages(nextMessages);
    setDraft("");
    setTyping(true);
    try {
      const reply = await sendMentorMessage(preparation.id, challengeSlug, message);
      setMessages((current) => [...current, { role: "assistant", content: reply }]);
    } catch (error) {
      const content = error instanceof Error ? error.message : "Não foi possível falar com o mentor agora.";
      setMessages((current) => [...current, { role: "assistant", content }]);
    } finally {
      setTyping(false);
    }
  }

  return (
    <section className="chat-panel">
      <div className="chat-header"><MentorIcon /><strong>Crew</strong></div>
      <div className="messages">
        <div className="message-row message-row--assistant">
          <MentorIcon />
          <div className="message">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{welcomeMessage}</ReactMarkdown>
          </div>
        </div>
        {messages.map((message, index) => (
          <div className={`message-row message-row--${message.role}`} key={`${message.role}-${index}`}>
            {message.role === "assistant" && <MentorIcon />}
            <div className="message">
              {message.role === "assistant" ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
              ) : message.content}
            </div>
          </div>
        ))}
        {typing && <div className="message-row message-row--assistant"><MentorIcon /><div className="typing"><i /><i /><i /></div></div>}
        <div ref={messagesEndRef} aria-hidden="true" />
      </div>

      <div className="quick-actions">
        {quickActions.map((action) => {
          const Icon = action.icon;
          return <button key={action.label} type="button" disabled={!historyReady} onClick={() => send(action.prompt)}><Icon size={15} />{action.label}</button>;
        })}
      </div>

      <form className="chat-input" onSubmit={(event) => { event.preventDefault(); send(); }}>
        <input disabled={!historyReady} value={draft} onChange={(event) => setDraft(event.target.value)} placeholder={historyReady ? "Pergunte ou escolha uma atividade..." : "Carregando histórico..."} />
        <button className="send-button" type="submit" aria-label="Enviar mensagem" title="Enviar mensagem" disabled={!draft.trim() || typing || !historyReady}><Send size={19} /></button>
      </form>
    </section>
  );
}

const topicIcons = [Code2, BrainCircuit, CircleGauge, MessageCircle];

function TopicsPanel({ preparation, onDiscuss }: { preparation: Preparation; onDiscuss: () => void }) {
  const source = preparation.match.focos_de_preparacao.length
    ? preparation.match.focos_de_preparacao
    : preparation.match.lacunas.length
      ? preparation.match.lacunas.map((gap) => gap.requisito)
      : ["Revisar requisitos principais da vaga"];
  const topics = source.slice(0, 4).map((title, index) => ({
    title,
    description: preparation.match.lacunas[index]?.evidencia || "Foco definido a partir da comparação entre a vaga e o currículo.",
    icon: topicIcons[index % topicIcons.length],
  }));

  return (
    <section className="content-panel">
      <div className="section-heading"><h2>Assuntos prioritários</h2></div>
      <div className="topic-grid">
        {topics.map((topic, index) => {
          const Icon = topic.icon;
          return <article className="topic-card" key={topic.title}><div className="topic-card__number">0{index + 1}</div><span className="topic-card__icon"><Icon size={22} /></span><h3>{topic.title}</h3><p>{topic.description}</p><footer><button className="compact-icon-button" type="button" onClick={onDiscuss} aria-label={`Conversar sobre ${topic.title}`} title="Conversar sobre este assunto"><MessageCircle size={18} /></button></footer></article>;
        })}
      </div>
    </section>
  );
}

function ChallengesPanel({ preparation, onMentor }: { preparation: Preparation; onMentor: (slug: string) => void }) {
  const [expanded, setExpanded] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const questions = expanded ? preparation.questions : preparation.questions.slice(0, 4);

  if (selectedQuestion) {
    return (
      <section className="content-panel challenge-reader">
        <button className="icon-button icon-button--ghost reader-back" type="button" onClick={() => setSelectedQuestion(null)} aria-label="Voltar aos desafios" title="Voltar aos desafios"><ArrowLeft size={19} /></button>
        <header className="challenge-reader__header">
          <div>
            <p>{selectedQuestion.difficulty} · {selectedQuestion.tags.join(" · ")}</p>
            <h2>{selectedQuestion.title}</h2>
          </div>
          <a href={`https://leetcode.com/problems/${selectedQuestion.slug}/`} target="_blank" rel="noreferrer"><ExternalLink size={17} /><span>Abrir no LeetCode</span></a>
        </header>
        <article className="markdown-content">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{selectedQuestion.content_md}</ReactMarkdown>
        </article>
        <button className="primary-button" type="button" onClick={() => onMentor(selectedQuestion.slug)}><MessageCircle size={18} />Iniciar mentoria deste desafio</button>
      </section>
    );
  }

  return (
    <section className="content-panel">
      <div className="section-heading"><h2>Desafios recomendados</h2></div>
      <div className="challenge-list">
        {questions.map((question, index) => { const recommendation = preparation.recommendations[index]; return <article className="challenge-row" key={question.slug}><span className="challenge-index">{String(index + 1).padStart(2, "0")}</span><span className="challenge-title"><strong>{recommendation?.papel}: {question.title}</strong><small>{recommendation?.justificativa ?? question.tags.join(" · ")}</small></span><button className="compact-icon-button" type="button" onClick={() => setSelectedQuestion(question)} aria-label={`Abrir desafio ${question.title}`} title="Abrir desafio"><ArrowRight size={18} /></button></article>; })}
      </div>
      {preparation.questions.length > 4 && <button className="outline-button" type="button" onClick={() => setExpanded((current) => !current)}>{expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}<span>{expanded ? "Mostrar menos" : "Ver todos os desafios"}</span></button>}
    </section>
  );
}

function Workspace({ preparation, onReset }: { preparation: Preparation; onReset: () => void }) {
  const [tab, setTab] = useState<WorkspaceTab>("chat");
  const [challengeSlug, setChallengeSlug] = useState(preparation.recommendations[0]?.desafio.slug ?? "");
  const gaps = preparation.match.lacunas.slice(0, 3);
  const summary = conciseSummary(preparation.match.resumo);

  return (
    <main className="workspace">
      <header className="workspace-topbar">
        <Brand />
        <div className="current-role"><Target size={17} /> {preparation.job.titulo}</div>
        <button className="text-button topbar-action" type="button" onClick={onReset} aria-label="Iniciar nova análise"><RotateCcw size={18} /><span>Nova análise</span></button>
      </header>

      <div className="workspace-layout">
        <aside className="sidebar">
          <div className="sidebar__heading"><h2>Seu diagnóstico</h2><strong>{preparation.match.aderencia}%</strong><span>de aderência</span><p title={preparation.match.resumo}>{summary}</p></div>
          <div className="sidebar__gaps"><h3>Principais lacunas</h3>{gaps.map((gap) => <div key={gap.requisito} title={gap.requisito}>{gap.requisito}</div>)}</div>
          <nav>
            <button type="button" className={tab === "chat" ? "is-active" : ""} aria-current={tab === "chat" ? "page" : undefined} onClick={() => setTab("chat")}><MessageCircle size={19} />Conversa</button>
            <button type="button" className={tab === "topics" ? "is-active" : ""} aria-current={tab === "topics" ? "page" : undefined} onClick={() => setTab("topics")}><BookOpen size={19} />Assuntos</button>
            <button type="button" className={tab === "challenges" ? "is-active" : ""} aria-current={tab === "challenges" ? "page" : undefined} onClick={() => setTab("challenges")}><Trophy size={19} />Desafios</button>
          </nav>
        </aside>

        <div className="workspace-view" key={tab}>
          {tab === "chat" && challengeSlug && <ChatPanel preparation={preparation} challengeSlug={challengeSlug} />}
          {tab === "topics" && <TopicsPanel preparation={preparation} onDiscuss={() => setTab("chat")} />}
          {tab === "challenges" && <ChallengesPanel preparation={preparation} onMentor={(slug) => { setChallengeSlug(slug); setTab("chat"); }} />}
        </div>
      </div>
    </main>
  );
}

export default function App() {
  const [screen, setScreen] = useState<Screen>("onboarding");
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [preparation, setPreparation] = useState<Preparation | null>(null);
  const [loadStatus, setLoadStatus] = useState<LoadStatus>("pending");
  const [loadError, setLoadError] = useState("");

  const runPreparation = useCallback(async (input: Submission) => {
    setSubmission(input);
    setPreparation(null);
    setLoadStatus("pending");
    setLoadError("");
    setScreen("loading");

    try {
      const result = await createPreparation(input.jobUrl, input.cv);
      setPreparation(result);
      window.history.replaceState(null, "", `?preparation=${result.id}`);
      setLoadStatus("success");
      window.setTimeout(() => setScreen("diagnostic"), 650);
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : "Não foi possível concluir a preparação.");
      setLoadStatus("error");
    }
  }, []);

  useEffect(() => {
    const id = new URLSearchParams(window.location.search).get("preparation");
    if (!id) return;
    getPreparation(id).then((value) => { setPreparation(value); setScreen(value.status === "aguardando_diagnostico" ? "diagnostic" : value.status === "avaliacao_em_processamento" ? "evaluation-recovery" : "stories"); }).catch(() => window.history.replaceState(null, "", window.location.pathname));
  }, []);

  function reset() {
    setSubmission(null);
    setPreparation(null);
    setLoadError("");
    setLoadStatus("pending");
    setScreen("onboarding");
    window.history.replaceState(null, "", window.location.pathname);
  }

  if (screen === "onboarding") return <Onboarding onSubmit={runPreparation} />;
  if (screen === "loading" && submission) return <LoadingScreen submission={submission} preparation={preparation} status={loadStatus} error={loadError} onRetry={() => runPreparation(submission)} onBack={reset} />;
  if (screen === "diagnostic" && preparation) return <DiagnosticScreen preparation={preparation} onChange={setPreparation} onComplete={(value) => { setPreparation(value); setScreen("stories"); }} />;
  if (screen === "evaluation-recovery" && preparation) return <EvaluationRecovery preparation={preparation} onComplete={(value) => { setPreparation(value); setScreen("stories"); }} />;
  if (screen === "stories" && preparation) return <StoriesScreen preparation={preparation} onComplete={() => setScreen("workspace")} />;
  if (preparation) return <Workspace preparation={preparation} onReset={reset} />;
  return <Onboarding onSubmit={runPreparation} />;
}
