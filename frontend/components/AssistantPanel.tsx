"use client";

import { FormEvent, useMemo, useRef, useState, useTransition } from "react";

import { askAssistant, simplifyText } from "@/lib/api";
import { ChatResponse, ChatStructuredResponse, SimplifyResponse } from "@/lib/types";
import { displayName } from "@/lib/ui";

type SuggestedGroup = {
  label: string;
  description: string;
  questions: string[];
};

const SUGGESTED_GROUPS: SuggestedGroup[] = [
  {
    label: "Seguridad",
    description: "Crimen, policía, extorsiones y prevención.",
    questions: [
      "¿Qué propone [candidato] para reducir la inseguridad?",
      "¿Qué dice [candidato] sobre crimen organizado y extorsiones?",
      "¿Algún candidato propone reformar la policía?",
    ],
  },
  {
    label: "Salud",
    description: "SIS, Essalud, hospitales y cobertura territorial.",
    questions: [
      "¿Qué propone [candidato] para mejorar el sistema de salud pública?",
      "¿Qué candidatos proponen fortalecer el SIS o Essalud?",
      "¿Qué dicen sobre salud rural o atención primaria?",
    ],
  },
  {
    label: "Educación",
    description: "Calidad, docentes, educación técnica y acceso.",
    questions: [
      "¿Qué propone [candidato] para mejorar la calidad educativa?",
      "¿Qué dice el plan de [candidato] sobre docentes y sueldos?",
      "¿Qué candidatos plantean educación técnica o universitaria?",
    ],
  },
  {
    label: "Economía",
    description: "Empleo, empresa, formalización e inversión.",
    questions: [
      "¿Cómo piensa [candidato] crear empleo formal?",
      "¿Qué propone [candidato] para pequeños negocios y emprendedores?",
      "¿Qué diferencias hay entre [candidato A] y [candidato B] en economía?",
    ],
  },
  {
    label: "Institucionalidad",
    description: "Corrupción, Estado, justicia y gobernabilidad.",
    questions: [
      "¿Qué propone [candidato] para combatir la corrupción?",
      "¿Qué medidas plantea sobre transparencia en el gasto público?",
      "¿Qué dice el plan sobre justicia o reforma institucional?",
    ],
  },
];

const STARTER_PROMPTS = [
  "¿Qué propone George Forsyth sobre seguridad?",
  "¿Qué diferencias hay entre Keiko Fujimori y Rafael López Aliaga en economía?",
  "¿Qué dicen los planes sobre agua potable en zonas rurales?",
  "¿Qué candidato plantea más detalle en salud pública?",
];

function normalizeQuestion(input: string): string {
  const trimmed = input.trim();
  if (!trimmed) return "";
  if (trimmed.includes(" ") || trimmed.includes("?")) return trimmed;
  return `¿Qué proponen sobre ${trimmed}?`;
}

function splitFallbackItems(answer: string): string[] {
  return answer
    .split(/\n+/)
    .map((item) => item.replace(/\[(EVIDENCIA DOCUMENTAL|AUSENCIA DE EVIDENCIA|INFERENCIA)\]\s*/gi, "").trim())
    .map((item) => item.replace(/^\d+[.)]\s*/, "").replace(/^[-*•]\s*/, "").trim())
    .filter(Boolean);
}

function buildStructuredFallback(result: ChatResponse): ChatStructuredResponse {
  const items = splitFallbackItems(result.answer);
  const summary = items[0] ?? (result.evidence_found
    ? "Se encontraron fragmentos documentales relevantes para responder la consulta."
    : "No se encontró evidencia suficiente en los documentos disponibles.");

  return {
    summary,
    findings: result.evidence_found ? items.slice(0, 4) : [],
    evidence_gaps: result.evidence_found ? [] : [summary],
    inferences: items.filter((item) => /infer/i.test(item)).slice(0, 2),
    follow_ups: [
      "¿Quieres profundizar en este mismo tema?",
      "¿Quieres comparar este tema con otro candidato?",
    ],
  };
}

function resultTone(result: ChatResponse) {
  if (!result.evidence_found) return { className: "assistant-badge--gap", label: "Sin evidencia suficiente" };
  if ((result.structured?.inferences.length ?? 0) > 0) {
    return { className: "assistant-badge--inference", label: "Incluye inferencias marcadas" };
  }
  return { className: "assistant-badge--evidence", label: "Evidencia documental" };
}

function comparisonSummary(structured: ChatStructuredResponse): string | null {
  const match = structured.summary.match(/^Diferencia principal:\s*(.+)$/i);
  if (match) return match[1]?.trim() ?? null;
  return null;
}

function comparisonSections(answer: string, candidates: string[]) {
  const sections = candidates.map((candidate) => {
    const escaped = candidate.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp(`${escaped}:\\s*([\\s\\S]*?)(?=\\n[A-ZÁÉÍÓÚÑ][^\\n]*:|$)`, "i");
    const match = answer.match(regex);
    return {
      candidate,
      text: match?.[1]?.trim() ?? "",
    };
  });

  const gapMatch = answer.match(/Vac[ií]os de evidencia:\s*([\s\S]*?)(?=\nCierre:|$)/i);
  return {
    sections,
    gaps: gapMatch?.[1]?.trim() ?? "",
  };
}

export function AssistantPanel() {
  const [question, setQuestion] = useState("¿Qué proponen sobre agua potable en zonas rurales?");
  const [submittedQuestion, setSubmittedQuestion] = useState("¿Qué proponen sobre agua potable en zonas rurales?");
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [simplified, setSimplified] = useState<SimplifyResponse | null>(null);
  const [showSimplified, setShowSimplified] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [simplifyError, setSimplifyError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [isSimplifying, startSimplifyTransition] = useTransition();
  const [activeGroup, setActiveGroup] = useState<string>(SUGGESTED_GROUPS[0].label);
  const resultRef = useRef<HTMLDivElement | null>(null);

  const structured = useMemo(
    () => (result ? result.structured ?? buildStructuredFallback(result) : null),
    [result],
  );
  const comparisonCandidates = useMemo(() => {
    if (!result) return [];
    return Array.from(new Set(result.sources.map((source) => displayName(source.candidate_name)).filter(Boolean))).slice(0, 2);
  }, [result]);
  const comparisonSources = useMemo(() => {
    if (!result || comparisonCandidates.length < 2) return [];
    return comparisonCandidates.map((candidateName) => ({
      candidateName,
      sources: result.sources.filter((source) => displayName(source.candidate_name) === candidateName).slice(0, 3),
    }));
  }, [comparisonCandidates, result]);
  const isComparisonView = comparisonCandidates.length >= 2;
  const comparisonBlock = useMemo(
    () => (result && isComparisonView ? comparisonSections(result.answer, comparisonCandidates) : null),
    [comparisonCandidates, isComparisonView, result],
  );
  const comparisonLead = structured ? comparisonSummary(structured) : null;

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setResult(null);
    setSimplified(null);
    setShowSimplified(false);
    const normalizedQuestion = normalizeQuestion(question);
    if (!normalizedQuestion) {
      setError("Escribe una consulta para el asistente.");
      return;
    }

    startTransition(async () => {
      try {
        const response = await askAssistant(normalizedQuestion);
        setSubmittedQuestion(normalizedQuestion);
        setResult(response);
        requestAnimationFrame(() => {
          resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      } catch {
        setError("No se pudo consultar el asistente en este momento.");
      }
    });
  }

  function onSimplify() {
    if (!result?.answer) return;
    setSimplifyError(null);
    setSimplified(null);
    setShowSimplified(true);

    startSimplifyTransition(async () => {
      try {
        const response = await simplifyText(result.answer);
        setSimplified(response);
      } catch {
        setSimplifyError("No se pudo simplificar la respuesta en este momento.");
      }
    });
  }

  const activeSuggestions = SUGGESTED_GROUPS.find((group) => group.label === activeGroup) ?? SUGGESTED_GROUPS[0];
  const tone = result ? resultTone(result) : null;
  const hasEvidenceGaps = (structured?.evidence_gaps.length ?? 0) > 0;
  const hasInferences = (structured?.inferences.length ?? 0) > 0;

  return (
    <section className="section">
      <div className="section-header">
        <h2 className="section-title">Asistente IA con fuentes</h2>
      </div>

      <div className="assistant-intro-shell">
        <div className="method-note assistant-disclaimer assistant-disclaimer--hero">
          <span className="method-icon">🔒</span>
          <span>
            <strong>Consulta electoral con evidencia visible.</strong> Pulso Cívico no recomienda candidatos. El
            asistente responde con fragmentos del corpus indexado, marca inferencias y deja explícitos los vacíos
            documentales.
          </span>
        </div>

        <div className="assistant-orientation-grid">
          <article className="assistant-guide-card">
            <div className="assistant-guide-kicker">Antes de preguntar</div>
            <h3>Qué sí hace este asistente</h3>
            <ul className="assistant-guide-list">
              <li>Resume propuestas y trayectorias a partir de documentos indexados.</li>
              <li>Distingue evidencia documental, inferencia y ausencia de evidencia.</li>
              <li>Permite abrir fuentes y seguir explorando por tema o candidato.</li>
            </ul>
          </article>

          <article className="assistant-guide-card assistant-guide-card--compact">
            <div className="assistant-guide-kicker">Cómo empezar</div>
            <h3>Preguntas útiles</h3>
            <div className="assistant-starter-list">
              {STARTER_PROMPTS.map((prompt) => (
                <button
                  className="assistant-starter-chip"
                  key={prompt}
                  onClick={() => setQuestion(prompt)}
                  type="button"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </article>
        </div>
      </div>

      <div className="assistant-panel assistant-panel--structured">
        <div className="assistant-entry-grid">
          <aside className="assistant-category-panel">
            <div className="assistant-panel-label">Temas sugeridos</div>
            <div className="assistant-category-list" role="tablist" aria-label="Temas sugeridos">
              {SUGGESTED_GROUPS.map((group) => (
                <button
                  aria-selected={activeGroup === group.label}
                  className={`assistant-category-tab${activeGroup === group.label ? " active" : ""}`}
                  key={group.label}
                  onClick={() => setActiveGroup(group.label)}
                  role="tab"
                  type="button"
                >
                  <span className="assistant-category-name">{group.label}</span>
                  <span className="assistant-category-desc">{group.description}</span>
                </button>
              ))}
            </div>
          </aside>

          <div className="assistant-workspace">
            <div className="assistant-query-guide">
              <div className="assistant-panel-label">Consulta guiada</div>
              <p className="assistant-panel-copy">
                Formula una pregunta concreta por tema, candidato o comparación. La respuesta prioriza
                comprensión rápida y luego baja al detalle con fuente.
              </p>
              <div className="assistant-suggested-questions">
                {activeSuggestions.questions.map((q) => (
                  <button
                    className="assistant-question-chip"
                    key={q}
                    onClick={() => setQuestion(q)}
                    type="button"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

            <form className="assistant-form assistant-form--stacked" onSubmit={onSubmit}>
              <label className="assistant-input-label" htmlFor="assistant-question">
                Tu pregunta
              </label>
              <textarea
                className="assistant-input assistant-input--structured"
                id="assistant-question"
                rows={4}
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ejemplo: ¿Qué propone George Forsyth sobre seguridad ciudadana?"
              />
              <div className="assistant-form-actions">
                <button className="btn-primary assistant-submit" disabled={isPending} type="submit">
                  {isPending ? "Consultando…" : "Preguntar con fuentes"}
                </button>
                <div className="assistant-form-meta">
                  Respuesta breve arriba, evidencia y vacíos debajo.
                </div>
              </div>
            </form>
          </div>
        </div>

        {error ? <div className="empty-state"><div className="empty-sub">{error}</div></div> : null}

        {result && structured ? (
          <div className="assistant-response-shell" ref={resultRef}>
            <article className="assistant-query-card">
              <div className="assistant-panel-label">Consulta realizada</div>
              <h3>{submittedQuestion}</h3>
              <div className="assistant-response-meta">
                <span className={`assistant-badge ${tone?.className ?? ""}`}>{tone?.label}</span>
                <span className="assistant-badge assistant-badge--neutral">
                  {result.sources.length} fuente{result.sources.length === 1 ? "" : "s"} visibles
                </span>
                <span className="assistant-badge assistant-badge--neutral">Proveedor: {result.provider}</span>
              </div>
            </article>

            <article className="assistant-brief-card">
              <div className="assistant-result-head">
                <div className="info-label">Respuesta breve</div>
                <div className="info-sub">
                  {isComparisonView
                    ? "Primero el contraste principal, luego la evidencia por candidatura."
                    : "Primero el hallazgo principal, luego el detalle verificable."}
                </div>
              </div>
              <p className="assistant-summary">{comparisonLead ?? structured.summary}</p>

              {result.evidence_found ? (
                <div className="simplify-row">
                  <button
                    className="btn-simplify"
                    disabled={isSimplifying}
                    onClick={onSimplify}
                    type="button"
                  >
                    {isSimplifying ? "Simplificando…" : "Explicámelo fácil"}
                  </button>
                  <span className="simplify-hint">Versión en lenguaje simple, sin perder trazabilidad.</span>
                </div>
              ) : null}
            </article>

            <div className="assistant-insight-grid">
              <article className="assistant-insight-card">
                <div className="assistant-insight-label">Hallazgos documentales</div>
                {structured.findings.length > 0 ? (
                  <ul className="assistant-insight-list">
                    {structured.findings.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="assistant-muted-copy">No hay hallazgos documentales claros para mostrar en este bloque.</p>
                )}
              </article>

              {hasEvidenceGaps ? (
                <article className="assistant-insight-card assistant-insight-card--warn">
                  <div className="assistant-insight-label">Vacíos de evidencia</div>
                  <ul className="assistant-insight-list">
                    {structured.evidence_gaps.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </article>
              ) : null}

              {hasInferences ? (
                <article className="assistant-insight-card assistant-insight-card--soft">
                  <div className="assistant-insight-label">Inferencias marcadas</div>
                  <ul className="assistant-insight-list">
                    {structured.inferences.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </article>
              ) : null}
            </div>

            {!hasEvidenceGaps && !hasInferences ? (
              <div className="assistant-response-note">
                La respuesta se sostuvo en hallazgos documentales sin vacíos principales ni inferencias explícitas.
              </div>
            ) : null}

            {isComparisonView ? (
              <section className="assistant-compare-shell">
                <div className="assistant-panel-label">Lectura comparativa</div>
                <div className="assistant-compare-grid">
                  {comparisonSources.map((entry) => (
                    <article className="assistant-compare-card" key={entry.candidateName}>
                      <div className="assistant-compare-name">{entry.candidateName}</div>
                      {comparisonBlock?.sections.find((section) => section.candidate === entry.candidateName)?.text ? (
                        <div className="assistant-compare-editorial">
                          {comparisonBlock.sections.find((section) => section.candidate === entry.candidateName)?.text}
                        </div>
                      ) : null}
                      {entry.sources.length > 0 ? (
                        <div className="assistant-compare-points">
                          {entry.sources.map((source, index) => (
                            <div className="assistant-compare-point" key={`${entry.candidateName}-${source.source_url}-${index}`}>
                              <div className="assistant-compare-axis">{source.axis}</div>
                              <p>{source.excerpt}</p>
                              <div className="assistant-compare-meta">
                                <span>{source.page_number ? `Página ${source.page_number}` : "Sin página exacta"}</span>
                                <a href={source.source_url} rel="noreferrer" target="_blank">
                                  Ver fuente
                                </a>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="assistant-muted-copy">No se recuperaron fragmentos visibles para esta candidatura.</p>
                      )}
                    </article>
                  ))}
                </div>
                {comparisonBlock?.gaps ? (
                  <div className="assistant-response-note">
                    <strong>Vacíos de evidencia:</strong> {comparisonBlock.gaps}
                  </div>
                ) : null}
              </section>
            ) : null}

            {showSimplified ? (
              <div className="simplified-block">
                <div className="simplified-header">
                  <span className="simplified-label">Versión simplificada</span>
                  <button
                    className="btn-ghost simplified-close"
                    onClick={() => setShowSimplified(false)}
                    type="button"
                  >
                    Cerrar
                  </button>
                </div>
                {simplifyError ? (
                  <div className="empty-sub">{simplifyError}</div>
                ) : isSimplifying ? (
                  <div className="empty-sub">Generando versión simplificada…</div>
                ) : simplified ? (
                  <>
                    <p className="simplified-text">{simplified.simplified}</p>
                    <div className="simplified-disclaimer">
                      Este bloque simplifica el lenguaje, pero no reemplaza la lectura de la fuente original.
                    </div>
                  </>
                ) : null}
              </div>
            ) : null}

            {result.sources.length > 0 ? (
              <section className="assistant-sources-block">
                <div className="assistant-sources-head">
                  <div>
                    <div className="sources-label">Fuente y evidencia</div>
                    <p className="assistant-panel-copy">
                      Fragmentos recuperados del corpus indexado para sustentar la respuesta.
                    </p>
                  </div>
                </div>
                <div className="assistant-sources">
                  {result.sources.map((source, index) => (
                    <article className="source-card assistant-source-card" key={`${source.source_url}-${index}`}>
                      <div className="source-card-topline">
                        <span className="assistant-source-chip">{displayName(source.candidate_name)}</span>
                        <span className="assistant-source-chip assistant-source-chip--axis">{source.axis}</span>
                      </div>
                      <div className="source-card-title">{source.title}</div>
                      <div className="assistant-source-locator">
                        {source.page_number ? `Página ${source.page_number}` : "Ubicación exacta no disponible"}
                      </div>
                      <p>{source.excerpt}</p>
                      <div className="assistant-source-footer">
                        <span className="assistant-source-name">{source.source_name}</span>
                        <a href={source.source_url} rel="noreferrer" target="_blank">
                          Ver fuente
                        </a>
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            ) : null}

            {structured.follow_ups.length > 0 ? (
              <section className="assistant-followup-block">
                <div className="assistant-panel-label">Siguientes preguntas sugeridas</div>
                <div className="assistant-followup-list">
                  {structured.follow_ups.map((followUp) => (
                    <button
                      className="assistant-followup-chip"
                      key={followUp}
                      onClick={() => setQuestion(followUp)}
                      type="button"
                    >
                      {followUp}
                    </button>
                  ))}
                </div>
              </section>
            ) : null}

            <details className="assistant-raw-answer">
              <summary>Ver respuesta completa generada</summary>
              <p className="assistant-answer">{result.answer}</p>
            </details>
          </div>
        ) : null}
      </div>
    </section>
  );
}
