"use client";

import { FormulaMemberDetail } from "@/lib/types";

type Props = {
  member: FormulaMemberDetail;
};

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("es-PE", {
    style: "currency",
    currency: "PEN",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatYearRange(from?: string | null, to?: string | null): string {
  if (from && to) return `${from} – ${to}`;
  if (from) return `Desde ${from}`;
  if (to) return `Hasta ${to}`;
  return "";
}

function Chevron() {
  return (
    <svg className="hv-chevron" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function HojaVidaPanel({ member }: Props) {
  // Education chip
  let educationLabel = "Sin universitaria";
  let educationVariant = "hv-chip--neutral";
  if (member.university_education_count > 0) {
    educationLabel = "Universitario";
    educationVariant = "";
  } else if ((member.academic_records_count ?? 0) > 0) {
    educationLabel = "Técnico superior";
    educationVariant = "";
  }

  // Elected chip
  const electedLabel = member.elected_offices_count > 0
    ? `${member.elected_offices_count} cargo${member.elected_offices_count > 1 ? "s" : ""} electo${member.elected_offices_count > 1 ? "s" : ""}`
    : "Sin cargo electo";
  const electedVariant = member.elected_offices_count > 0 ? "" : "hv-chip--neutral";

  // Penal chip
  const penalLabel = member.penal_sentences_count === 0
    ? "Sin sentencias penales"
    : `${member.penal_sentences_count} sentencia${member.penal_sentences_count > 1 ? "s" : ""} penal${member.penal_sentences_count > 1 ? "es" : ""}`;
  const penalVariant = member.penal_sentences_count > 0 ? "hv-chip--alert" : "hv-chip--ok";

  // Civil chip
  const civilLabel = member.civil_sentences_count === 0
    ? "Sin sentencias civiles"
    : `${member.civil_sentences_count} sentencia${member.civil_sentences_count > 1 ? "s" : ""} civil${member.civil_sentences_count > 1 ? "es" : ""}`;
  const civilVariant = member.civil_sentences_count > 0 ? "hv-chip--alert" : "hv-chip--ok";

  const hasAcademic =
    member.university_education.length > 0 || member.postgraduate_education.length > 0;

  const hasTrajectory =
    member.elected_offices.length > 0 ||
    member.work_experience.length > 0 ||
    member.party_roles.length > 0;

  const hasPatrimony =
    member.annual_income_total != null ||
    member.immovable_assets.length > 0 ||
    member.movable_assets.length > 0;

  const hasSentences =
    member.penal_sentences.length > 0 ||
    member.civil_sentences.length > 0 ||
    member.obligations_count > 0 ||
    member.marginal_annotations_count > 0;

  const totalSentences =
    member.penal_sentences_count + member.civil_sentences_count +
    member.obligations_count + member.marginal_annotations_count;

  const totalTrajectory =
    member.elected_offices_count + member.labor_records_count + member.party_roles_count;

  const totalAcademic =
    member.university_education_count + member.postgraduate_records_count;

  const EMPTY_MSG = "Sin registros en esta categoría según la Hoja de Vida del JNE.";

  return (
    <div>
      {/* Synthesis chips */}
      <div className="hv-synthesis">
        <span className={`hv-chip ${educationVariant}`}>🎓 {educationLabel}</span>
        <span className={`hv-chip ${electedVariant}`}>🏛️ {electedLabel}</span>
        {member.labor_records_count > 0 && (
          <span className="hv-chip">💼 {member.labor_records_count} exp. laboral</span>
        )}
        <span className={`hv-chip ${penalVariant}`}>⚖️ {penalLabel}</span>
        <span className={`hv-chip ${civilVariant}`}>📋 {civilLabel}</span>
        {member.annual_income_total != null && (
          <span className="hv-chip">💰 {formatCurrency(member.annual_income_total)}/año</span>
        )}
      </div>

      {/* Section 1: Formación académica */}
      <details className="hv-section">
        <summary>
          <div className="hv-summary-left">
            <span className="hv-summary-icon">🎓</span>
            <span className="hv-summary-title">Formación académica</span>
          </div>
          <div className="hv-summary-right">
            <span className={`hv-badge ${totalAcademic === 0 ? "hv-badge--zero" : ""}`}>
              {totalAcademic}
            </span>
            <Chevron />
          </div>
        </summary>
        <div className="hv-section-body">
          {!hasAcademic ? (
            <p className="hv-empty">{EMPTY_MSG}</p>
          ) : (
            <>
              {member.university_education.length > 0 && (
                <>
                  <div className="hv-subgroup-title">Educación universitaria</div>
                  {member.university_education.map((rec, i) => (
                    <div className="hv-record" key={i}>
                      <div className="hv-record-title">{rec.institution}</div>
                      <div className="hv-record-sub">
                        {rec.degree} · {rec.completed ? "✅ Concluido" : "⬜ No concluido"}
                        {rec.year ? ` · ${rec.year}` : ""}
                      </div>
                      {rec.comment && <div className="hv-record-comment">{rec.comment}</div>}
                    </div>
                  ))}
                </>
              )}
              {member.postgraduate_education.length > 0 && (
                <>
                  <div className="hv-subgroup-title">Posgrado</div>
                  {member.postgraduate_education.map((rec, i) => (
                    <div className="hv-record" key={i}>
                      <div className="hv-record-title">{rec.institution}</div>
                      <div className="hv-record-sub">
                        {rec.degree}{rec.year ? ` · ${rec.year}` : ""}
                      </div>
                      {rec.comment && <div className="hv-record-comment">{rec.comment}</div>}
                    </div>
                  ))}
                </>
              )}
            </>
          )}
        </div>
      </details>

      {/* Section 2: Trayectoria */}
      <details className="hv-section">
        <summary>
          <div className="hv-summary-left">
            <span className="hv-summary-icon">🏛️</span>
            <span className="hv-summary-title">Trayectoria</span>
          </div>
          <div className="hv-summary-right">
            <span className={`hv-badge ${totalTrajectory === 0 ? "hv-badge--zero" : ""}`}>
              {totalTrajectory}
            </span>
            <Chevron />
          </div>
        </summary>
        <div className="hv-section-body">
          {!hasTrajectory ? (
            <p className="hv-empty">{EMPTY_MSG}</p>
          ) : (
            <>
              {member.elected_offices.length > 0 && (
                <>
                  <div className="hv-subgroup-title">Cargos de elección popular</div>
                  {member.elected_offices.map((rec, i) => (
                    <div className="hv-record" key={i}>
                      <div className="hv-record-title">{rec.office}</div>
                      <div className="hv-record-sub">
                        {rec.party}
                        {formatYearRange(rec.year_from, rec.year_to)
                          ? ` · ${formatYearRange(rec.year_from, rec.year_to)}`
                          : ""}
                      </div>
                      {rec.comment && <div className="hv-record-comment">{rec.comment}</div>}
                    </div>
                  ))}
                </>
              )}
              {member.party_roles.length > 0 && (
                <>
                  <div className="hv-subgroup-title">Cargos partidarios</div>
                  {member.party_roles.map((rec, i) => (
                    <div className="hv-record" key={i}>
                      <div className="hv-record-title">{rec.role}</div>
                      <div className="hv-record-sub">
                        {rec.party}
                        {formatYearRange(rec.year_from, rec.year_to)
                          ? ` · ${formatYearRange(rec.year_from, rec.year_to)}`
                          : ""}
                      </div>
                    </div>
                  ))}
                </>
              )}
              {member.work_experience.length > 0 && (
                <>
                  <div className="hv-subgroup-title">Experiencia laboral</div>
                  {member.work_experience.map((rec, i) => (
                    <div className="hv-record" key={i}>
                      <div className="hv-record-title">{rec.organization}</div>
                      <div className="hv-record-sub">
                        {rec.position}
                        {formatYearRange(rec.year_from, rec.year_to)
                          ? ` · ${formatYearRange(rec.year_from, rec.year_to)}`
                          : ""}
                        {rec.country ? ` · ${rec.country}` : ""}
                      </div>
                    </div>
                  ))}
                </>
              )}
            </>
          )}
        </div>
      </details>

      {/* Section 3: Patrimonio declarado */}
      <details className="hv-section">
        <summary>
          <div className="hv-summary-left">
            <span className="hv-summary-icon">💰</span>
            <span className="hv-summary-title">Patrimonio declarado</span>
          </div>
          <div className="hv-summary-right">
            <span className={`hv-badge ${member.movable_assets_count + member.immovable_assets_count === 0 ? "hv-badge--zero" : ""}`}>
              {member.movable_assets_count + member.immovable_assets_count} bienes
            </span>
            <Chevron />
          </div>
        </summary>
        <div className="hv-section-body">
          {!hasPatrimony ? (
            <p className="hv-empty">{EMPTY_MSG}</p>
          ) : (
            <>
              {member.annual_income_total != null && (
                <div className="hv-patrimony-hero">
                  <div className="hv-patrimony-hero-label">Ingresos anuales declarados</div>
                  <div className="hv-patrimony-hero-value">{formatCurrency(member.annual_income_total)}</div>
                </div>
              )}

              <div className="hv-patrimony-grid">
                {member.public_income_total != null && member.public_income_total > 0 && (
                  <div className="hv-patrimony-card">
                    <div className="hv-patrimony-icon">🏛️</div>
                    <div className="hv-patrimony-value">{formatCurrency(member.public_income_total)}</div>
                    <div className="hv-patrimony-label">Sector público</div>
                  </div>
                )}
                {member.private_income_total != null && member.private_income_total > 0 && (
                  <div className="hv-patrimony-card">
                    <div className="hv-patrimony-icon">🏢</div>
                    <div className="hv-patrimony-value">{formatCurrency(member.private_income_total)}</div>
                    <div className="hv-patrimony-label">Sector privado</div>
                  </div>
                )}
                {member.assets_declared_value != null && (
                  <div className="hv-patrimony-card">
                    <div className="hv-patrimony-icon">📊</div>
                    <div className="hv-patrimony-value">{formatCurrency(member.assets_declared_value)}</div>
                    <div className="hv-patrimony-label">Valor total declarado</div>
                  </div>
                )}
                <div className="hv-patrimony-card">
                  <div className="hv-patrimony-icon">🏠</div>
                  <div className="hv-patrimony-value">{member.immovable_assets_count}</div>
                  <div className="hv-patrimony-label">Bienes inmuebles</div>
                </div>
                <div className="hv-patrimony-card">
                  <div className="hv-patrimony-icon">🚗</div>
                  <div className="hv-patrimony-value">{member.movable_assets_count}</div>
                  <div className="hv-patrimony-label">Bienes muebles</div>
                </div>
              </div>

              {member.immovable_assets.length > 0 && (
                <>
                  <div className="hv-subgroup-title">Bienes inmuebles</div>
                  {member.immovable_assets.map((asset, i) => (
                    <div className="hv-record" key={i}>
                      <div className="hv-record-title">{asset.description}</div>
                      <div className="hv-record-sub">
                        {asset.value != null ? formatCurrency(asset.value) : "Valor no declarado"}
                        {asset.location ? ` · ${asset.location}` : ""}
                      </div>
                    </div>
                  ))}
                </>
              )}

              {member.movable_assets.length > 0 && (
                <>
                  <div className="hv-subgroup-title">Bienes muebles</div>
                  {member.movable_assets.map((asset, i) => (
                    <div className="hv-record" key={i}>
                      <div className="hv-record-title">{asset.description}</div>
                      <div className="hv-record-sub">
                        {asset.value != null ? formatCurrency(asset.value) : "Valor no declarado"}
                      </div>
                    </div>
                  ))}
                </>
              )}
            </>
          )}
        </div>
      </details>

      {/* Section 4: Antecedentes documentales */}
      <details className={`hv-section ${totalSentences > 0 ? "hv-section--alert" : "hv-section--ok"}`}>
        <summary>
          <div className="hv-summary-left">
            <span className="hv-summary-icon">{totalSentences > 0 ? "🚨" : "✅"}</span>
            <span className="hv-summary-title">Antecedentes documentales</span>
          </div>
          <div className="hv-summary-right">
            <span className={`hv-badge ${totalSentences > 0 ? "hv-badge--alert" : "hv-badge--zero"}`}>
              {totalSentences}
            </span>
            <Chevron />
          </div>
        </summary>
        <div className="hv-section-body">
          {!hasSentences ? (
            <p className="hv-empty">{EMPTY_MSG}</p>
          ) : (
            <>
              {member.penal_sentences.length > 0 && (
                <>
                  <div className="hv-subgroup-title">Sentencias penales</div>
                  {member.penal_sentences.map((rec, i) => (
                    <div className="hv-record" key={i}>
                      <div className="hv-record-title">{rec.description}</div>
                      {rec.year && <div className="hv-record-sub">{rec.year}</div>}
                      {rec.comment && <div className="hv-record-comment">{rec.comment}</div>}
                    </div>
                  ))}
                </>
              )}
              {member.civil_sentences.length > 0 && (
                <>
                  <div className="hv-subgroup-title">Sentencias civiles</div>
                  {member.civil_sentences.map((rec, i) => (
                    <div className="hv-record" key={i}>
                      <div className="hv-record-title">{rec.description}</div>
                      {rec.year && <div className="hv-record-sub">{rec.year}</div>}
                      {rec.comment && <div className="hv-record-comment">{rec.comment}</div>}
                    </div>
                  ))}
                </>
              )}
              {member.obligations_count > 0 && (
                <div className="hv-record">
                  <div className="hv-record-title">Obligaciones registradas</div>
                  <div className="hv-record-sub">{member.obligations_count} registro(s)</div>
                </div>
              )}
              {member.marginal_annotations_count > 0 && (
                <div className="hv-record">
                  <div className="hv-record-title">Anotaciones marginales</div>
                  <div className="hv-record-sub">{member.marginal_annotations_count} registro(s)</div>
                </div>
              )}
            </>
          )}
          <p className="hv-disclaimer">
            ℹ️ Información extraída de la Hoja de Vida oficial presentada ante el JNE. No constituye antecedentes penales ni civiles definitivos.
          </p>
        </div>
      </details>

      {member.hoja_vida_url && (
        <a
          className="hv-source-link"
          href={member.hoja_vida_url}
          rel="noreferrer"
          target="_blank"
        >
          📄 Ver hoja de vida completa en JNE →
        </a>
      )}
    </div>
  );
}
