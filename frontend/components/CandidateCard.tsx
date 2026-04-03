"use client";

import { ReactNode, useState } from "react";
import Link from "next/link";

import { Candidate } from "@/lib/types";
import { ImageLightbox } from "@/components/ImageLightbox";
import { colorFromId, displayName, initialsFromName } from "@/lib/ui";

type CandidateCardProps = {
  candidate: Candidate;
  preview?: string;
  compareAction?: ReactNode;
  containerClassName?: string;
};

export function CandidateCard({ candidate, preview, compareAction, containerClassName }: CandidateCardProps) {
  const [zoomImage, setZoomImage] = useState<{ alt: string; src: string } | null>(null);
  const avatarColor = colorFromId(candidate.id);
  const previewText = preview || candidate.biography || "Ficha en construccion con propuestas verificadas y fuentes publicas.";
  const candidateName = displayName(candidate.name);
  const partyName = displayName(candidate.party);

  return (
    <>
      <article className={`cand-card${containerClassName ? ` ${containerClassName}` : ""}`}>
        <div className="card-header">
          {candidate.metadata?.photo_url ? (
            <button
              aria-label={`Ampliar foto de ${candidateName}`}
              className="image-zoom-trigger avatar-button"
              onClick={() => setZoomImage({ alt: candidateName, src: candidate.metadata?.photo_url ?? "" })}
              type="button"
            >
              <img alt={candidateName} className="avatar photo-avatar" src={candidate.metadata.photo_url} />
            </button>
          ) : (
            <div className="avatar" style={{ background: avatarColor }}>
              {initialsFromName(candidateName)}
            </div>
          )}
          <div className="card-meta">
            <div className="card-name">{candidateName}</div>
            <div className="card-party">{partyName}</div>
            <div className="card-region">📍 {candidate.region}</div>
            {candidate.metadata?.party_logo_url ? (
              <button
                aria-label={`Ampliar logo de ${partyName}`}
                className="image-zoom-trigger party-logo-button"
                onClick={() => setZoomImage({ alt: `Logo de ${partyName}`, src: candidate.metadata?.party_logo_url ?? "" })}
                type="button"
              >
                <img alt={`Logo de ${partyName}`} className="party-logo-inline" src={candidate.metadata.party_logo_url} />
              </button>
            ) : null}
          </div>
        </div>

        <div className="card-proposal">
          <strong>Resumen</strong>
          {previewText}
        </div>

        {candidate.metadata?.full_plan_pdf_url || candidate.metadata?.summary_pdf_url ? (
          <div className="card-docs">
            {candidate.metadata?.summary_pdf_url ? (
              <a href={candidate.metadata.summary_pdf_url} rel="noreferrer" target="_blank">
                Resumen PDF
              </a>
            ) : null}
            {candidate.metadata?.full_plan_pdf_url ? (
              <a href={candidate.metadata.full_plan_pdf_url} rel="noreferrer" target="_blank">
                Plan completo
              </a>
            ) : null}
          </div>
        ) : null}

        <div className="card-actions">
          {compareAction}
          <Link className="btn-view" href={`/candidates/${candidate.id}`}>
            Ver ficha →
          </Link>
        </div>
      </article>

      {zoomImage ? <ImageLightbox alt={zoomImage.alt} onClose={() => setZoomImage(null)} src={zoomImage.src} /> : null}
    </>
  );
}
