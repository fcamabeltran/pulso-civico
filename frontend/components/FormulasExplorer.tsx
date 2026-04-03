"use client";

import Link from "next/link";
import { useState, useMemo } from "react";
import { PresidentialFormula, FormulaCandidate } from "@/lib/types";
import { ImageLightbox } from "@/components/ImageLightbox";

const ROLES: Record<number, { label: string; color: string }> = {
  1: { label: "Presidente/a",         color: "var(--c-navy)"  },
  2: { label: "1.° Vicepresidente/a", color: "var(--c-blue)"  },
  3: { label: "2.° Vicepresidente/a", color: "#2a7d6e"         },
};

function toTitleCase(s: string) {
  return s.toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
}

function CandidateRow({ c }: { c: FormulaCandidate }) {
  const [zoomOpen, setZoomOpen] = useState(false);
  const role = ROLES[c.id_cargo] ?? ROLES[1];
  const isPresident = c.id_cargo === 1;
  const name = toTitleCase(c.nombre);

  return (
    <>
      <div className={`formula-cand-row${isPresident ? " formula-cand-row--president" : ""}`} style={{ borderLeftColor: role.color }}>
        <div className="formula-photo-wrap">
          <button
            aria-label={`Ampliar foto de ${name}`}
            className="image-zoom-trigger formula-photo-button"
            onClick={() => setZoomOpen(true)}
            type="button"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              className="formula-photo"
              src={c.foto_url}
              alt={c.nombre}
              onError={(e) => {
                (e.currentTarget as HTMLImageElement).style.display = "none";
                (e.currentTarget.nextElementSibling as HTMLElement).style.display = "flex";
              }}
            />
            <div className="formula-photo-ph" style={{ display: "none" }}>👤</div>
          </button>
          <span className="formula-pos-dot" style={{ background: role.color }}>
            {c.posicion}
          </span>
        </div>

        <div className="formula-cand-info">
          <div className="formula-role" style={{ color: role.color }}>{role.label}</div>

          {c.candidate_id ? (
            <Link className="formula-name formula-name--link" href={`/candidates/${c.candidate_id}`}>
              {name}
            </Link>
          ) : (
            <div className="formula-name">{name}</div>
          )}

          <div className="formula-dni">DNI {c.dni}</div>

          {c.candidate_id && isPresident && (
            <Link className="formula-profile-btn" href={`/candidates/${c.candidate_id}?tab=perfil`}>
              Ver perfil completo
              <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" width="13" height="13" aria-hidden="true">
                <path d="m6 3 5 5-5 5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </Link>
          )}

          {c.candidate_id && !isPresident && (
            <Link className="formula-profile-link" href={`/candidates/${c.candidate_id}?tab=perfil`}>
              Ver perfil →
            </Link>
          )}
        </div>
      </div>
      {zoomOpen ? <ImageLightbox alt={name} onClose={() => setZoomOpen(false)} src={c.foto_url} /> : null}
    </>
  );
}

function PartyCard({ formula }: { formula: PresidentialFormula }) {
  const [open, setOpen] = useState(false);
  const [zoomOpen, setZoomOpen] = useState(false);
  const pres = formula.candidatos.find((c) => c.id_cargo === 1);
  const sorted = [...formula.candidatos].sort((a, b) => a.posicion - b.posicion);
  const initials = formula.nombre_partido.split(" ").slice(0, 2).map((w) => w[0]).join("");

  return (
    <>
      <div className={`formula-card${open ? " formula-card--open" : ""}`}>
        <div className="formula-trigger">
          <button
            aria-label={`Ampliar logo de ${formula.nombre_partido}`}
            className="image-zoom-trigger formula-logo formula-logo-button"
            onClick={(event) => {
              event.stopPropagation();
              setZoomOpen(true);
            }}
            type="button"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={formula.logo_url}
              alt={formula.nombre_partido}
              onError={(e) => {
                (e.currentTarget as HTMLImageElement).style.display = "none";
                (e.currentTarget.nextElementSibling as HTMLElement).style.display = "flex";
              }}
            />
            <span className="formula-logo-fb" style={{ display: "none" }}>{initials}</span>
          </button>
          <button
            aria-expanded={open}
            className="formula-trigger-main"
            onClick={() => setOpen((v) => !v)}
            type="button"
          >
            <div className="formula-party-meta">
              <div className="formula-party-name">{formula.nombre_partido}</div>
              {pres && (
                <div className="formula-party-preview">{toTitleCase(pres.nombre)}</div>
              )}
            </div>
            <svg
              className="formula-chevron"
              viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2.5" width="18" height="18"
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
        </div>

        {open && (
          <div className="formula-panel">
            <div className="formula-panel-label">Fórmula presidencial</div>
            <div className="formula-cands">
              {sorted.map((c) => (
                <CandidateRow key={c.id_cargo} c={c} />
              ))}
            </div>
          </div>
        )}
      </div>
      {zoomOpen ? <ImageLightbox alt={`Logo de ${formula.nombre_partido}`} onClose={() => setZoomOpen(false)} src={formula.logo_url} /> : null}
    </>
  );
}

export function FormulasExplorer({ formulas }: { formulas: PresidentialFormula[] }) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    if (!query.trim()) return formulas;
    const q = query.toLowerCase();
    return formulas.filter(
      (f) =>
        f.nombre_partido.toLowerCase().includes(q) ||
        f.candidatos.some((c) => c.nombre.toLowerCase().includes(q))
    );
  }, [query, formulas]);

  return (
    <>
      {/* Toolbar */}
      <div className="formulas-toolbar">
        <div className="formulas-search-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-4.35-4.35" strokeLinecap="round" />
          </svg>
          <input
            type="text"
            placeholder="Busca un partido o candidato…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoComplete="off"
          />
        </div>
        <span className="formulas-count">
          <strong>{filtered.length}</strong> de {formulas.length} partidos
        </span>
      </div>

      {/* Grid */}
      <div className="formulas-wrap">
        {filtered.length === 0 ? (
          <div className="formulas-empty">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="40" height="40" opacity={0.35}>
              <circle cx="11" cy="11" r="7" /><path d="m20 20-4.35-4.35" />
            </svg>
            <p>Sin resultados para &ldquo;{query}&rdquo;</p>
          </div>
        ) : (
          <div className="formulas-grid">
            {filtered.map((f) => (
              <PartyCard key={f.id} formula={f} />
            ))}
          </div>
        )}
      </div>
    </>
  );
}
