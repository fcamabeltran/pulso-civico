"use client";

import { useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";

import { CandidateDetail, FormulaMemberDetail } from "@/lib/types";
import { ImageLightbox } from "@/components/ImageLightbox";
import { HojaVidaPanel } from "@/components/HojaVidaPanel";
import { AXIS_ICONS, PROMISE_STYLES, colorFromId, displayName, initialsFromName } from "@/lib/ui";
import { simplifyText } from "@/lib/api";

type CandidateProfileProps = {
  candidate: CandidateDetail;
  hvMember?: FormulaMemberDetail | null;
};

type Tab = "propuestas" | "promesas" | "perfil";

// ── Parsers ──────────────────────────────────────────────

interface ParsedProposal {
  objetivo: string;
  problema?: string;
  indicador?: string;
  meta?: string;
}

function parseProposalContent(content: string): ParsedProposal {
  const clean = content.replace(/\n+/g, " ").trim();

  const extract = (label: RegExp, next: RegExp): string | undefined => {
    const m = clean.match(label);
    if (!m) return undefined;
    const start = (m.index ?? 0) + m[0].length;
    const nextMatch = clean.slice(start).search(next);
    const chunk = nextMatch !== -1 ? clean.slice(start, start + nextMatch) : clean.slice(start);
    return chunk.trim().replace(/\.$/, "").trim() || undefined;
  };

  const problema = extract(
    /Problema identificado\s*:/i,
    /Objetivo\s*:|Indicador\s*:|Meta\s*:/i,
  );
  const objetivo = extract(
    /Objetivo\s*:/i,
    /Indicador\s*:|Meta\s*:|Problema identificado\s*:/i,
  );
  const indicador = extract(/Indicador\s*:/i, /Meta\s*:|Objetivo\s*:/i);
  const meta = extract(/Meta\s*:/i, /Objetivo\s*:|Indicador\s*:/i);

  return {
    objetivo: objetivo ?? clean,
    problema,
    indicador,
    meta,
  };
}

function cleanTitle(title: string): string {
  const flat = title.replace(/\n+/g, " ").trim();
  const noNum = flat.replace(/^\d+\.\s*/, "");
  if (!noNum) return flat;
  return noNum.charAt(0).toUpperCase() + noNum.slice(1).toLowerCase();
}

// ── Sub-components ───────────────────────────────────────

function PropChevron() {
  return (
    <svg className="prop-chevron" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

type SimplifyState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "done"; text: string }
  | { status: "error" };

function ProposalCard({ proposal }: { proposal: CandidateDetail["proposals"][number] }) {
  const [simplify, setSimplify] = useState<SimplifyState>({ status: "idle" });
  const parsed = useMemo(() => parseProposalContent(proposal.content), [proposal.content]);
  const title = useMemo(() => cleanTitle(proposal.title), [proposal.title]);

  async function handleSimplify() {
    setSimplify({ status: "loading" });
    try {
      const res = await simplifyText(proposal.content);
      setSimplify({ status: "done", text: res.simplified });
    } catch {
      setSimplify({ status: "error" });
    }
  }

  return (
    <div className="prop-card">
      <div className="prop-card-title">{title}</div>

      {simplify.status === "done" ? (
        <div className="prop-simplified-box">
          <div className="prop-simplified-header">
            <span className="prop-simplified-label">✨ Versión simplificada</span>
            <button className="prop-back-link" onClick={() => setSimplify({ status: "idle" })} type="button">
              Ver original
            </button>
          </div>
          {simplify.text}
        </div>
      ) : (
        <>
          <div className="prop-section">
            <div className="prop-section-label">🎯 Objetivo</div>
            <div className="prop-section-text">{parsed.objetivo}</div>
          </div>
          {parsed.problema && (
            <div className="prop-section">
              <div className="prop-section-label">⚠️ Problema identificado</div>
              <div className="prop-section-text">{parsed.problema}</div>
            </div>
          )}
          {parsed.meta && (
            <div className="prop-section">
              <div className="prop-section-label">📊 Meta</div>
              <div className="prop-section-text">{parsed.meta}</div>
            </div>
          )}
        </>
      )}

      <div className="prop-footer">
        <div className="prop-source">
          📄
          <a href={proposal.source_url} rel="noreferrer" target="_blank">
            {proposal.source_name}
          </a>
        </div>
        {simplify.status !== "done" && (
          <button
            className="prop-simplify-btn"
            disabled={simplify.status === "loading"}
            onClick={handleSimplify}
            type="button"
          >
            {simplify.status === "loading" ? "Simplificando…" : "✨ Simplificar"}
          </button>
        )}
        {simplify.status === "error" && (
          <span style={{ fontSize: 11, color: "#c0392b" }}>Error. Intenta de nuevo.</span>
        )}
      </div>
    </div>
  );
}

// ── Main component ───────────────────────────────────────

export function CandidateProfile({ candidate, hvMember }: CandidateProfileProps) {
  const searchParams = useSearchParams();
  const initialTab = (searchParams.get("tab") as Tab | null) ?? "propuestas";
  const [activeTab, setActiveTab] = useState<Tab>(initialTab);
  const [zoomImage, setZoomImage] = useState<{ alt: string; src: string } | null>(null);
  const [promiseFilter, setPromiseFilter] = useState<string | null>(null);

  const candidateName = displayName(candidate.name);
  const partyName = displayName(candidate.party);

  const grouped = useMemo(() => {
    return candidate.proposals.reduce<Record<string, typeof candidate.proposals>>((acc, p) => {
      if (!acc[p.axis]) acc[p.axis] = [];
      acc[p.axis].push(p);
      return acc;
    }, {});
  }, [candidate.proposals]);

  // Promise stats
  const promiseCounts = useMemo(() => {
    const counts: Record<string, number> = { cumplida: 0, pendiente: 0, incumplida: 0, parcial: 0 };
    for (const p of candidate.promises) counts[p.status] = (counts[p.status] ?? 0) + 1;
    return counts;
  }, [candidate.promises]);

  const filteredPromises = useMemo(() => {
    if (!promiseFilter) return candidate.promises;
    return candidate.promises.filter((p) => p.status === promiseFilter);
  }, [candidate.promises, promiseFilter]);

  return (
    <>
      <section className="profile-hero">
        <div className="profile-hero-inner">
          <div className="profile-header">
            {candidate.metadata?.photo_url ? (
              <button
                aria-label={`Ampliar foto de ${candidateName}`}
                className="image-zoom-trigger avatar-button"
                onClick={() => setZoomImage({ alt: candidateName, src: candidate.metadata?.photo_url ?? "" })}
                type="button"
              >
                <img alt={candidateName} className="profile-avatar profile-photo" src={candidate.metadata.photo_url} />
              </button>
            ) : (
              <div className="profile-avatar" style={{ background: colorFromId(candidate.id) }}>
                {initialsFromName(candidateName)}
              </div>
            )}
            <div className="profile-info">
              <h1 className="profile-name">{candidateName}</h1>
              <p className="profile-party">{partyName}</p>
              {candidate.metadata?.party_logo_url ? (
                <button
                  aria-label={`Ampliar logo de ${partyName}`}
                  className="image-zoom-trigger profile-logo-button"
                  onClick={() => setZoomImage({ alt: `Logo de ${partyName}`, src: candidate.metadata?.party_logo_url ?? "" })}
                  type="button"
                >
                  <img alt={`Logo de ${partyName}`} className="profile-party-logo" src={candidate.metadata.party_logo_url} />
                </button>
              ) : null}
              <div className="profile-tags">
                <span className="profile-tag">📍 {candidate.region}</span>
                {candidate.office ? <span className="profile-tag">{candidate.office}</span> : null}
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="tabs">
        <button className={`tab-btn ${activeTab === "propuestas" ? "active" : ""}`} onClick={() => setActiveTab("propuestas")} type="button">
          Propuestas
        </button>
        <button className={`tab-btn ${activeTab === "promesas" ? "active" : ""}`} onClick={() => setActiveTab("promesas")} type="button">
          Seguimiento
        </button>
        <button className={`tab-btn ${activeTab === "perfil" ? "active" : ""}`} onClick={() => setActiveTab("perfil")} type="button">
          Perfil documentado
        </button>
      </div>

      <div className="profile-body">

        {/* ── TAB: PROPUESTAS ── */}
        {activeTab === "propuestas" ? (
          <section className="section">
            <p className="section-note">
              {candidate.proposals.length} propuestas extraídas de fuentes públicas y agrupadas por eje temático.
            </p>
            <div className="proposal-list">
              {Object.entries(grouped).map(([axis, proposals]) => (
                <details className="proposal-item" key={axis}>
                  <summary className="prop-axis-summary">
                    <div className="prop-axis-left">
                      <div className="prop-axis-icon">{AXIS_ICONS[axis] ?? "📋"}</div>
                      <span className="prop-axis-name">{axis}</span>
                    </div>
                    <div className="prop-axis-right">
                      <span className="prop-count-badge">{proposals.length} propuesta{proposals.length !== 1 ? "s" : ""}</span>
                      <PropChevron />
                    </div>
                  </summary>
                  <div className="proposal-body open-body">
                    {proposals.map((proposal) => (
                      <ProposalCard key={proposal.id} proposal={proposal} />
                    ))}
                  </div>
                </details>
              ))}
            </div>
          </section>
        ) : null}

        {/* ── TAB: SEGUIMIENTO ── */}
        {activeTab === "promesas" ? (
          <section className="section">
            {candidate.promises.length === 0 ? (
              <div className="seg-empty">
                <span className="seg-empty-icon">📋</span>
                <div className="seg-empty-title">Sin promesas en seguimiento aún</div>
                <p className="seg-empty-sub">
                  El seguimiento de promesas estará disponible durante y después del período de gobierno. Por ahora, revisa el perfil documentado del candidato.
                </p>
                <button className="seg-empty-cta" onClick={() => setActiveTab("perfil")} type="button">
                  Ver perfil documentado →
                </button>
              </div>
            ) : (
              <>
                {/* Stats */}
                <div className="seg-stats">
                  {(["cumplida", "pendiente", "incumplida", "parcial"] as const).map((status) => {
                    const ui = PROMISE_STYLES[status];
                    return (
                      <div
                        key={status}
                        className={`seg-stat ${promiseFilter === status ? "seg-stat--active" : ""}`}
                        onClick={() => setPromiseFilter(promiseFilter === status ? null : status)}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => e.key === "Enter" && setPromiseFilter(promiseFilter === status ? null : status)}
                      >
                        <div className="seg-stat-num">{promiseCounts[status] ?? 0}</div>
                        <div className="seg-stat-label">{ui.label}</div>
                      </div>
                    );
                  })}
                </div>

                {/* List */}
                <div className="promise-list">
                  {filteredPromises.map((promise) => {
                    const ui = PROMISE_STYLES[promise.status];
                    return (
                      <article className="promise-item" key={promise.id}>
                        <span className={`promise-badge ${ui.className}`}>{ui.label}</span>
                        <div>
                          <div className="promise-text">{promise.title}</div>
                          <div className="promise-date">{promise.description}</div>
                          {promise.evidence_note ? <div className="promise-evidence">📋 {promise.evidence_note}</div> : null}
                          <div className="proposal-source">
                            <a href={promise.source_url} rel="noreferrer" target="_blank">
                              {promise.source_name}
                            </a>
                          </div>
                        </div>
                      </article>
                    );
                  })}
                </div>
              </>
            )}
          </section>
        ) : null}

        {/* ── TAB: PERFIL DOCUMENTADO ── */}
        {activeTab === "perfil" ? (
          <section className="section">
            <div className="hv-meta-row">
              <span className="hv-meta-pill">🏛️ <strong>{partyName}</strong></span>
              <span className="hv-meta-pill">📍 <strong>{candidate.region}</strong></span>
              {candidate.office ? <span className="hv-meta-pill">🎯 <strong>{candidate.office}</strong></span> : null}
            </div>

            {candidate.biography ? (
              <div className="hv-bio-card">
                <div className="hv-bio-label">📖 Biografía</div>
                {candidate.biography}
              </div>
            ) : null}

            <div className="hv-section-divider">Documentos oficiales</div>
            <div className="hv-docs-grid">
              {candidate.metadata?.hoja_vida_url ? (
                <a className="hv-doc-card" href={candidate.metadata.hoja_vida_url} rel="noreferrer" target="_blank">
                  <span className="hv-doc-icon">📋</span>
                  <div className="hv-doc-text">
                    <span className="hv-doc-name">Hoja de vida</span>
                    <span className="hv-doc-meta">JNE oficial</span>
                  </div>
                </a>
              ) : (
                <div className="hv-doc-card hv-doc-card--disabled">
                  <span className="hv-doc-icon">📋</span>
                  <div className="hv-doc-text">
                    <span className="hv-doc-name">Hoja de vida</span>
                    <span className="hv-doc-meta">No disponible</span>
                  </div>
                </div>
              )}
              {candidate.metadata?.summary_pdf_url ? (
                <a className="hv-doc-card" href={candidate.metadata.summary_pdf_url} rel="noreferrer" target="_blank">
                  <span className="hv-doc-icon">📄</span>
                  <div className="hv-doc-text">
                    <span className="hv-doc-name">Resumen del plan</span>
                    <span className="hv-doc-meta">PDF oficial</span>
                  </div>
                </a>
              ) : (
                <div className="hv-doc-card hv-doc-card--disabled">
                  <span className="hv-doc-icon">📄</span>
                  <div className="hv-doc-text">
                    <span className="hv-doc-name">Resumen del plan</span>
                    <span className="hv-doc-meta">No disponible</span>
                  </div>
                </div>
              )}
              {candidate.metadata?.full_plan_pdf_url ? (
                <a className="hv-doc-card" href={candidate.metadata.full_plan_pdf_url} rel="noreferrer" target="_blank">
                  <span className="hv-doc-icon">📑</span>
                  <div className="hv-doc-text">
                    <span className="hv-doc-name">Plan de gobierno</span>
                    <span className="hv-doc-meta">Documento completo</span>
                  </div>
                </a>
              ) : (
                <div className="hv-doc-card hv-doc-card--disabled">
                  <span className="hv-doc-icon">📑</span>
                  <div className="hv-doc-text">
                    <span className="hv-doc-name">Plan de gobierno</span>
                    <span className="hv-doc-meta">No disponible</span>
                  </div>
                </div>
              )}
            </div>

            {hvMember ? (
              <>
                <div className="hv-section-divider">Hoja de vida — JNE</div>
                <HojaVidaPanel member={hvMember} />
              </>
            ) : null}
          </section>
        ) : null}
      </div>

      {zoomImage ? <ImageLightbox alt={zoomImage.alt} onClose={() => setZoomImage(null)} src={zoomImage.src} /> : null}
    </>
  );
}
