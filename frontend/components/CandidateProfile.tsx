"use client";

import { useMemo, useState } from "react";

import { CandidateDetail, FormulaMemberDetail } from "@/lib/types";
import { ImageLightbox } from "@/components/ImageLightbox";
import { HojaVidaPanel } from "@/components/HojaVidaPanel";
import { AXIS_ICONS, PROMISE_STYLES, colorFromId, displayName, initialsFromName } from "@/lib/ui";

type CandidateProfileProps = {
  candidate: CandidateDetail;
  hvMember?: FormulaMemberDetail | null;
};

export function CandidateProfile({ candidate, hvMember }: CandidateProfileProps) {
  const [activeTab, setActiveTab] = useState<"propuestas" | "promesas" | "perfil">("propuestas");
  const [zoomImage, setZoomImage] = useState<{ alt: string; src: string } | null>(null);
  const candidateName = displayName(candidate.name);
  const partyName = displayName(candidate.party);
  const grouped = useMemo(() => {
    return candidate.proposals.reduce<Record<string, typeof candidate.proposals>>((acc, proposal) => {
      if (!acc[proposal.axis]) acc[proposal.axis] = [];
      acc[proposal.axis].push(proposal);
      return acc;
    }, {});
  }, [candidate.proposals]);

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
        {activeTab === "propuestas" ? (
          <section className="section">
            <p className="section-note">Propuestas extraídas de fuentes públicas y agrupadas por eje temático.</p>
            <div className="proposal-list">
              {Object.entries(grouped).map(([axis, proposals]) => (
                <details className="proposal-item" key={axis}>
                  <summary className="proposal-header">
                    <div className="eje-icon">{AXIS_ICONS[axis] ?? "•"}</div>
                    <span className="proposal-eje">{axis}</span>
                  </summary>
                  <div className="proposal-body open-body">
                    {proposals.map((proposal) => (
                      <article key={proposal.id}>
                        <p className="proposal-title">{proposal.title}</p>
                        <p className="proposal-text">{proposal.content}</p>
                        <div className="proposal-source">
                          <span>📄 Fuente:</span>
                          <a href={proposal.source_url} rel="noreferrer" target="_blank">
                            {proposal.source_name}
                          </a>
                        </div>
                      </article>
                    ))}
                  </div>
                </details>
              ))}
            </div>
          </section>
        ) : null}

        {activeTab === "promesas" ? (
          <section className="section">
            <div className="promise-list">
              {candidate.promises.map((promise) => {
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
          </section>
        ) : null}

        {activeTab === "perfil" ? (
          <section className="section">
            {hvMember && <HojaVidaPanel member={hvMember} />}
            <div className="info-grid">
              <div className="info-card">
                <div className="info-label">Partido</div>
                <div className="info-value">{partyName}</div>
              </div>
              <div className="info-card">
                <div className="info-label">Región</div>
                <div className="info-value">{candidate.region}</div>
              </div>
              <div className="info-card">
                <div className="info-label">Cargo</div>
                <div className="info-value">{candidate.office ?? "No especificado"}</div>
              </div>
              <div className="info-card">
                <div className="info-label">Hoja de vida</div>
                <div className="info-value smaller">
                  {candidate.metadata?.hoja_vida_url ? (
                    <a href={candidate.metadata.hoja_vida_url} rel="noreferrer" target="_blank">
                      Abrir hoja de vida oficial
                    </a>
                  ) : (
                    "No disponible todavía"
                  )}
                </div>
              </div>
              <div className="info-card">
                <div className="info-label">Biografía</div>
                <div className="info-value smaller">{candidate.biography ?? "Sin resumen biográfico cargado."}</div>
              </div>
              <div className="info-card">
                <div className="info-label">Resumen del plan</div>
                <div className="info-value smaller">
                  {candidate.metadata?.summary_pdf_url ? (
                    <a href={candidate.metadata.summary_pdf_url} rel="noreferrer" target="_blank">
                      Abrir resumen oficial
                    </a>
                  ) : (
                    "No disponible todavía"
                  )}
                </div>
              </div>
              <div className="info-card">
                <div className="info-label">Plan completo</div>
                <div className="info-value smaller">
                  {candidate.metadata?.full_plan_pdf_url ? (
                    <a href={candidate.metadata.full_plan_pdf_url} rel="noreferrer" target="_blank">
                      Abrir documento completo
                    </a>
                  ) : (
                    "No disponible todavía"
                  )}
                </div>
              </div>
              <div className="info-card">
                <div className="info-label">Origen</div>
                <div className="info-value smaller">{String(candidate.metadata?.imported_from ?? "Carga manual")}</div>
              </div>
              <div className="info-card">
                <div className="info-label">Resumen documental</div>
                <div className="info-value smaller">
                  {candidate.metadata?.hoja_vida_summary ? (
                    <>
                      <div>Experiencia laboral: {candidate.metadata.hoja_vida_summary.experiencia_laboral_registros ?? 0}</div>
                      <div>Sentencias penales: {candidate.metadata.hoja_vida_summary.sentencias_penales_registros ?? 0}</div>
                      <div>Sentencias civiles: {candidate.metadata.hoja_vida_summary.sentencias_civiles_registros ?? 0}</div>
                      <div>Bienes declarados: {candidate.metadata.hoja_vida_summary.declaracion_bienes_registros ?? 0}</div>
                    </>
                  ) : (
                    "Resumen de hoja de vida no cargado."
                  )}
                </div>
              </div>
            </div>
          </section>
        ) : null}
      </div>

      {zoomImage ? <ImageLightbox alt={zoomImage.alt} onClose={() => setZoomImage(null)} src={zoomImage.src} /> : null}
    </>
  );
}
