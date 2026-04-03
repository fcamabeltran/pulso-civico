"use client";

import { useEffect, useMemo, useRef, useState, useTransition } from "react";

import { CandidateCard } from "@/components/CandidateCard";
import { compareCandidates, getShareImageUrl } from "@/lib/api";
import { Candidate, CompareResponse, Proposal } from "@/lib/types";
import { AXIS_ICONS, colorFromId, displayName, initialsFromName } from "@/lib/ui";

type CompareBuilderProps = {
  candidates: Candidate[];
};

type ThemeKey =
  | "seguridad"
  | "salud"
  | "educacion"
  | "economia"
  | "corrupcion"
  | "gobernabilidad"
  | "ambiente"
  | "infraestructura";

type StateKey = "none" | "general" | "concrete" | "mechanisms" | "insufficient";

type ThemeDefinition = {
  key: ThemeKey;
  label: string;
  keywords: string[];
};

type CandidateThemeSummary = {
  status: StateKey;
  statusLabel: string;
  summary: string;
  highlights: string[];
  proposals: Proposal[];
};

const THEME_DEFINITIONS: ThemeDefinition[] = [
  { key: "seguridad", label: "Seguridad", keywords: ["seguridad", "delincu", "polic", "extorsi", "crimen", "violencia"] },
  { key: "salud", label: "Salud", keywords: ["salud", "hospital", "sis", "essalud", "medic", "sanitario"] },
  { key: "educacion", label: "Educación", keywords: ["educa", "escuela", "coleg", "docent", "universi", "beca"] },
  { key: "economia", label: "Economía y empleo", keywords: ["econom", "emple", "empresa", "inversion", "formal", "tribut"] },
  { key: "corrupcion", label: "Corrupción", keywords: ["corrup", "transparen", "contralor", "integridad", "anticorr"] },
  { key: "gobernabilidad", label: "Gobernabilidad", keywords: ["institu", "estado", "justicia", "reforma", "gestion publica", "gobern"] },
  { key: "ambiente", label: "Ambiente", keywords: ["ambient", "clima", "forest", "agua", "mineria", "contamina"] },
  { key: "infraestructura", label: "Infraestructura / servicios", keywords: ["infraestructura", "carretera", "puente", "transporte", "saneamiento", "vivienda"] },
];

const STATUS_META: Record<StateKey, { label: string; className: string }> = {
  none: { label: "No propone", className: "state-none" },
  general: { label: "Propuesta general", className: "state-general" },
  concrete: { label: "Propuesta con medidas concretas", className: "state-concrete" },
  mechanisms: { label: "Incluye metas o mecanismos", className: "state-mechanisms" },
  insufficient: { label: "Sin evidencia suficiente", className: "state-insufficient" },
};

function normalizeText(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function truncateText(text: string, maxLength: number) {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength).trim()}...`;
}

function proposalBelongsToTheme(proposal: Proposal, theme: ThemeDefinition) {
  const haystack = normalizeText(`${proposal.axis} ${proposal.title} ${proposal.content}`);
  return theme.keywords.some((keyword) => haystack.includes(keyword));
}

function inferState(proposals: Proposal[]): StateKey {
  if (!proposals.length) return "insufficient";

  const joined = normalizeText(proposals.map((proposal) => `${proposal.title} ${proposal.content}`).join(" "));
  const hasMechanisms = ["meta", "indicador", "mecanismo", "plazo", "financ", "implement", "objetivo"].some((token) =>
    joined.includes(token),
  );
  const hasConcreteActions = ["creara", "fortalecer", "constru", "programa", "servicio", "sistema", "reforma"].some((token) =>
    joined.includes(token),
  );

  if (hasMechanisms) return "mechanisms";
  if (hasConcreteActions || proposals.length >= 2) return "concrete";
  return "general";
}

function buildThemeSummary(candidate: Candidate, proposals: Proposal[], theme: ThemeDefinition): CandidateThemeSummary {
  const status = inferState(proposals);
  if (!proposals.length) {
    return {
      status,
      statusLabel: STATUS_META[status].label,
      summary: `${candidate.name} no presenta fragmentos suficientes sobre ${theme.label.toLowerCase()} en los documentos comparados.`,
      highlights: [],
      proposals,
    };
  }

  const firstProposal = proposals[0];
  const highlights = proposals.slice(0, 2).map((proposal) => proposal.title);
  return {
    status,
    statusLabel: STATUS_META[status].label,
    summary: `${candidate.name} concentra su propuesta de ${theme.label.toLowerCase()} en ${truncateText(firstProposal.content, 170)}`,
    highlights,
    proposals,
  };
}

function compareNarrative(left: CandidateThemeSummary, right: CandidateThemeSummary, theme: ThemeDefinition) {
  if (left.status === "insufficient" && right.status === "insufficient") {
    return `No se encontró evidencia suficiente para comparar ${theme.label.toLowerCase()} entre ambos candidatos.`;
  }
  if (left.status === right.status) {
    return `Ambos candidatos muestran un nivel similar de desarrollo en ${theme.label.toLowerCase()}: ${left.statusLabel.toLowerCase()}.`;
  }
  return `En ${theme.label.toLowerCase()}, la comparación muestra niveles distintos de desarrollo programático entre ambos candidatos.`;
}

function buildExecutiveSummary(
  leftName: string,
  rightName: string,
  summaries: Record<ThemeKey, { left: CandidateThemeSummary; right: CandidateThemeSummary; theme: ThemeDefinition }>,
) {
  const entries = Object.values(summaries);
  const differences = entries
    .filter((entry) => entry.left.status !== entry.right.status)
    .slice(0, 3)
    .map((entry) => entry.theme.label);
  const coincidences = entries
    .filter((entry) => entry.left.status === entry.right.status && entry.left.status !== "insufficient")
    .slice(0, 3)
    .map((entry) => entry.theme.label);
  const highDetail = entries
    .filter((entry) => entry.left.status === "mechanisms" || entry.right.status === "mechanisms")
    .slice(0, 3)
    .map((entry) => entry.theme.label);
  const evidenceGaps = entries
    .filter((entry) => entry.left.status === "insufficient" || entry.right.status === "insufficient")
    .slice(0, 3)
    .map((entry) => entry.theme.label);

  return {
    differences:
      differences.length > 0
        ? `Las diferencias más visibles aparecen en ${differences.join(", ")}.`
        : `${leftName} y ${rightName} muestran patrones similares en los temas principales del corpus.`,
    coincidences:
      coincidences.length > 0
        ? `Coinciden en el nivel de desarrollo de ${coincidences.join(", ")}.`
        : "No se observan coincidencias fuertes en el nivel de desarrollo temático.",
    highDetail:
      highDetail.length > 0
        ? `Los mayores niveles de detalle aparecen en ${highDetail.join(", ")}.`
        : "Ninguno de los dos planes destaca por incluir metas o mecanismos claros en los temas priorizados.",
      evidenceGaps:
      evidenceGaps.length > 0
        ? `Persisten vacíos o evidencia limitada en ${evidenceGaps.join(", ")}.`
        : "No se detectan vacíos relevantes de evidencia en los temas priorizados.",
  };
}

export function CompareBuilder({ candidates }: CompareBuilderProps) {
  const [selected, setSelected] = useState<number[]>([]);
  const [result, setResult] = useState<CompareResponse | null>(null);
  const [activeTheme, setActiveTheme] = useState<ThemeKey>("seguridad");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const resultRef = useRef<HTMLDivElement | null>(null);
  const pickerRef = useRef<HTMLDivElement | null>(null);

  const selectedCandidates = useMemo(
    () => selected.map((id) => candidates.find((item) => item.id === id)).filter((item): item is Candidate => Boolean(item)),
    [candidates, selected],
  );

  const selectionCount = selected.length;
  const selectionLabel =
    selectionCount === 0 ? "0 de 2 candidatos seleccionados" : selectionCount === 1 ? "1 de 2 candidatos seleccionados" : "2 candidatos listos";
  const helperLabel =
    selectionCount === 0
      ? "Selecciona dos candidatos para activar la comparación."
      : selectionCount === 1
        ? "Te falta 1 candidato para comparar."
        : "Revisa tu selección y continúa al comparador.";
  const actionLabel =
    selectionCount < 2 ? (selectionCount === 0 ? "Selecciona 2 candidatos" : "Falta 1 candidato") : isPending ? "Comparando..." : "Comparar candidatos";

  useEffect(() => {
    if (!result || !resultRef.current) return;
    resultRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [result]);

  function toggleCandidate(id: number) {
    setError(null);
    setResult(null);
    setSelected((current) => {
      if (current.includes(id)) return current.filter((item) => item !== id);
      if (current.length >= 2) return current;
      return [...current, id];
    });
  }

  function compare() {
    if (selected.length !== 2) {
      setError("Selecciona exactamente 2 candidatos.");
      return;
    }

    startTransition(async () => {
      try {
        const response = await compareCandidates(selected[0], selected[1]);
        setResult(response);
      } catch {
        setError("No se pudo generar la comparación.");
      }
    });
  }

  const themeData = useMemo(() => {
    if (!result) return null;

    const summaries = Object.fromEntries(
      THEME_DEFINITIONS.map((theme) => {
        const leftProposals = result.left_proposals.filter((proposal) => proposalBelongsToTheme(proposal, theme));
        const rightProposals = result.right_proposals.filter((proposal) => proposalBelongsToTheme(proposal, theme));
        return [
          theme.key,
          {
            theme,
            left: buildThemeSummary(result.left_candidate, leftProposals, theme),
            right: buildThemeSummary(result.right_candidate, rightProposals, theme),
          },
        ];
      }),
    ) as Record<ThemeKey, { theme: ThemeDefinition; left: CandidateThemeSummary; right: CandidateThemeSummary }>;

    return {
      summaries,
      executive:
        result.insights ?? buildExecutiveSummary(result.left_candidate.name, result.right_candidate.name, summaries),
    };
  }, [result]);

  const activeThemeBlock = themeData ? themeData.summaries[activeTheme] : null;

  return (
    <section className="section">
      <h1 className="section-title page-title">Comparación de candidatos</h1>
      <p className="page-subtitle">Organiza propuestas, vacíos y fuentes para facilitar una lectura comparativa más clara.</p>

      <div className="method-note">
        <span className="method-icon">💡</span>
        <span>Esta comparación no califica candidatos: resume diferencias, coincidencias y evidencia disponible por tema.</span>
      </div>

      <div className="cards-grid compare-grid" ref={pickerRef}>
        {candidates.map((candidate) => (
          <CandidateCard
            candidate={candidate}
            containerClassName={selected.includes(candidate.id) ? "cand-card--selected" : undefined}
            key={candidate.id}
            compareAction={
              <button
                className={`btn-ghost ${selected.includes(candidate.id) ? "selected compare-btn" : ""}`}
                onClick={() => toggleCandidate(candidate.id)}
                type="button"
              >
                {selected.includes(candidate.id) ? `Seleccionado ${selected.indexOf(candidate.id) + 1}` : "Seleccionar para comparar"}
              </button>
            }
          />
        ))}
      </div>

      <div className="compare-toolbar compare-toolbar--summary">
        <div className="compare-summary-text">
          <div className="compare-label">{selectionLabel}</div>
          <div className="compare-helper">{helperLabel}</div>
        </div>
        <div className="compare-selected">
          {selectedCandidates.length ? (
            selectedCandidates.map((candidate, index) => (
              <span className="compare-chip" key={candidate.id}>
                <span className="compare-chip-order">{index + 1}</span>
                <span className="chip-avatar" style={{ background: colorFromId(candidate.id) }}>
                  {initialsFromName(displayName(candidate.name))}
                </span>
                {displayName(candidate.name)}
                <button className="compare-chip-remove" onClick={() => toggleCandidate(candidate.id)} type="button">
                  Quitar
                </button>
              </span>
            ))
          ) : (
            <span className="compare-empty-inline">Aún no has elegido candidatos.</span>
          )}
        </div>
      </div>

      {error ? <div className="empty-state"><div className="empty-sub">{error}</div></div> : null}

      {result && themeData ? (
        <div className="compare-experience" ref={resultRef}>
          <section className="compare-hero-panel">
            <div className="compare-hero-top">
              <div>
                <div className="compare-eyebrow">Comparación guiada</div>
                <h2 className="compare-hero-title">Resumen comparativo</h2>
                <p className="compare-hero-sub">Primero entiende las diferencias principales y luego abre el detalle por tema.</p>
              </div>
              <button
                className="btn-ghost compare-change-btn"
                onClick={() => pickerRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })}
                type="button"
              >
                Cambiar candidatos
              </button>
            </div>

            <div className="compare-hero-heads">
              {[result.left_candidate, result.right_candidate].map((candidate) => (
                <article className="compare-hero-card" key={candidate.id}>
                  <div className="compare-head-line">
                    {candidate.metadata?.photo_url ? (
                      <img alt={candidate.name} className="avatar compare-avatar compare-photo" src={candidate.metadata.photo_url} />
                    ) : (
                      <div className="avatar compare-avatar" style={{ background: colorFromId(candidate.id) }}>
                        {initialsFromName(displayName(candidate.name))}
                      </div>
                    )}
                    <div>
                      <div className="compare-head-name">{displayName(candidate.name)}</div>
                      <div className="compare-head-party">{displayName(candidate.party)} · {candidate.region}</div>
                    </div>
                  </div>
                </article>
              ))}
            </div>

            <div className="compare-meta-note">
              Fuente del corpus: propuestas comparadas desde documentos públicos procesados por el sistema. La ausencia de evidencia se muestra explícitamente.
            </div>
          </section>

          <section className="compare-summary-grid">
            <article className="compare-summary-card">
              <div className="compare-summary-kicker">Diferencias principales</div>
              <p>{themeData.executive.differences}</p>
            </article>
            <article className="compare-summary-card">
              <div className="compare-summary-kicker">Coincidencias</div>
              <p>{themeData.executive.coincidences}</p>
            </article>
            <article className="compare-summary-card">
              <div className="compare-summary-kicker">Mayor nivel de detalle</div>
              <p>{themeData.executive.highDetail}</p>
            </article>
            <article className="compare-summary-card">
              <div className="compare-summary-kicker">Ausencia de evidencia</div>
              <p>{themeData.executive.evidenceGaps}</p>
            </article>
          </section>

          <section className="compare-matrix-panel">
            <div className="compare-section-head">
              <div>
                <div className="compare-eyebrow">Matriz descriptiva</div>
                <h3 className="compare-section-title">Temas clave</h3>
              </div>
              <p className="compare-section-sub">Estados descriptivos para leer rápido sin convertir la comparación en un ranking.</p>
            </div>

            <div className="compare-matrix">
              <div className="compare-matrix-header">Dimensión</div>
              <div className="compare-matrix-header">{displayName(result.left_candidate.name)}</div>
              <div className="compare-matrix-header">{displayName(result.right_candidate.name)}</div>
              {THEME_DEFINITIONS.map((theme) => {
                const row = themeData.summaries[theme.key];
                return (
                  <div className="compare-matrix-row" key={theme.key}>
                    <button className="compare-matrix-theme" onClick={() => setActiveTheme(theme.key)} type="button">
                      {theme.label}
                    </button>
                    <span className={`compare-state-badge ${STATUS_META[row.left.status].className}`}>{row.left.statusLabel}</span>
                    <span className={`compare-state-badge ${STATUS_META[row.right.status].className}`}>{row.right.statusLabel}</span>
                  </div>
                );
              })}
            </div>
          </section>

          <section className="compare-topic-panel">
            <div className="compare-section-head">
              <div>
                <div className="compare-eyebrow">Detalle por tema</div>
                <h3 className="compare-section-title">Explora por bloque temático</h3>
              </div>
              <p className="compare-section-sub">Abre el detalle solo donde quieras profundizar. La evidencia completa queda al final de cada bloque.</p>
            </div>

            <div className="eje-filter">
              {THEME_DEFINITIONS.map((theme) => (
                <button
                  className={`filter-chip ${activeTheme === theme.key ? "active" : ""}`}
                  key={theme.key}
                  onClick={() => setActiveTheme(theme.key)}
                  type="button"
                >
                  {theme.label}
                </button>
              ))}
            </div>

            {activeThemeBlock ? (
              <article className="compare-topic-card">
                <div className="compare-topic-intro">
                  <div className="compare-row-eje">{activeThemeBlock.theme.label}</div>
                  <p>{compareNarrative(activeThemeBlock.left, activeThemeBlock.right, activeThemeBlock.theme)}</p>
                </div>

                <div className="compare-topic-columns">
                  {[
                    { candidate: result.left_candidate, data: activeThemeBlock.left },
                    { candidate: result.right_candidate, data: activeThemeBlock.right },
                  ].map(({ candidate, data }) => (
                    <section className="compare-topic-column" key={candidate.id}>
                      <div className="compare-topic-head">
                        <div>
                          <div className="compare-col-name">{displayName(candidate.name)}</div>
                          <span className={`compare-state-badge ${STATUS_META[data.status].className}`}>{data.statusLabel}</span>
                        </div>
                      </div>

                      <p className="compare-topic-summary">{data.summary}</p>

                      {data.highlights.length ? (
                        <div className="compare-highlights">
                          <div className="compare-highlights-title">Highlights</div>
                          {data.highlights.map((highlight) => (
                            <div className="compare-highlight-item" key={highlight}>
                              {highlight}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="compare-empty-detail">No se encontró propuesta en este tema.</div>
                      )}

                      <details className="compare-evidence-block" open={data.proposals.length > 0}>
                        <summary>Fuente y evidencia</summary>
                        {data.proposals.length ? (
                          <div className="compare-points">
                            {data.proposals.map((proposal) => (
                              <article className="compare-point" key={proposal.id}>
                                <div className="compare-point-title">{proposal.title}</div>
                                <div className="compare-col-text">{proposal.content}</div>
                                <div className="compare-col-source">
                                  <a href={proposal.source_url} rel="noreferrer" target="_blank">
                                    Ver fuente
                                  </a>
                                </div>
                              </article>
                            ))}
                          </div>
                        ) : (
                          <div className="compare-empty-detail">Sin evidencia suficiente.</div>
                        )}
                      </details>
                    </section>
                  ))}
                </div>
              </article>
            ) : null}
          </section>

          <div className="share-row">
            <a className="btn-share whatsapp" href={getShareImageUrl(result.left_candidate.id, result.right_candidate.id)} rel="noreferrer" target="_blank">
              📱 Abrir imagen para WhatsApp
            </a>
          </div>
        </div>
      ) : null}

      <div className="compare-sticky-bar">
        <div className="compare-sticky-copy">
          <div className="compare-sticky-count">{selectionLabel}</div>
          <div className="compare-sticky-note">{helperLabel}</div>
        </div>
        <div className="compare-sticky-selected">
          {selectedCandidates.map((candidate, index) => (
            <span className="compare-chip compare-chip--sticky" key={candidate.id}>
              <span className="compare-chip-order">{index + 1}</span>
              <span className="chip-avatar" style={{ background: colorFromId(candidate.id) }}>
                {initialsFromName(displayName(candidate.name))}
              </span>
              <span className="compare-chip-name">{displayName(candidate.name)}</span>
            </span>
          ))}
        </div>
        <div className="compare-sticky-actions">
          {selectedCandidates.length ? (
            <button className="btn-ghost compare-clear-btn" onClick={() => setSelected([])} type="button">
              Limpiar
            </button>
          ) : null}
          <button className="btn-compare-now compare-sticky-cta" disabled={selectionCount !== 2 || isPending} onClick={compare} type="button">
            {actionLabel}
          </button>
        </div>
      </div>
    </section>
  );
}
