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

export function HojaVidaPanel({ member }: Props) {
  // Education level chip
  let educationLabel = "Sin registro universitario";
  if (member.university_education_count > 0) {
    educationLabel = "Superior universitario";
  } else if ((member.academic_records_count ?? 0) > 0) {
    educationLabel = "Técnico superior";
  }

  // Elected experience chip
  const electedLabel =
    member.elected_offices_count > 0
      ? "Con cargo electo"
      : "Sin cargo electo registrado";

  // Penal chip
  const penalLabel =
    member.penal_sentences_count === 0
      ? "Sin sentencias penales"
      : `${member.penal_sentences_count} sentencia(s) penal(es)`;

  // Civil chip
  const civilLabel =
    member.civil_sentences_count === 0
      ? "Sin sentencias civiles"
      : `${member.civil_sentences_count} sentencia(s) civil(es)`;

  // Income chip
  const incomeLabel =
    member.annual_income_total != null
      ? `Ingresos declarados: ${formatCurrency(member.annual_income_total)}`
      : "Sin ingresos declarados";

  const hasAcademic =
    member.university_education.length > 0 ||
    member.postgraduate_education.length > 0;

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

  const EMPTY_MSG = "Sin registros en esta categoría según la Hoja de Vida del JNE.";

  return (
    <div>
      {/* Synthesis chips */}
      <div className="hv-synthesis">
        <span className="hv-chip">{educationLabel}</span>
        <span className="hv-chip">{electedLabel}</span>
        <span className={`hv-chip${member.penal_sentences_count > 0 ? " hv-chip--alert" : ""}`}>
          {penalLabel}
        </span>
        <span className={`hv-chip${member.civil_sentences_count > 0 ? " hv-chip--alert" : ""}`}>
          {civilLabel}
        </span>
        <span className="hv-chip">{incomeLabel}</span>
      </div>

      {/* Section 1: Formación académica */}
      <details className="hv-section">
        <summary>
          Formación académica
          <span>({member.university_education_count + member.postgraduate_records_count} registros)</span>
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
                        {rec.degree} — {rec.completed ? "Concluido" : "No concluido"}
                        {rec.year ? ` (${rec.year})` : ""}
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
                        {rec.degree}
                        {rec.year ? ` (${rec.year})` : ""}
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
          Trayectoria
          <span>
            ({member.elected_offices_count + member.labor_records_count + member.party_roles_count} registros)
          </span>
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
          Patrimonio declarado
          <span>
            ({member.movable_assets_count + member.immovable_assets_count} bienes)
          </span>
        </summary>
        <div className="hv-section-body">
          {!hasPatrimony ? (
            <p className="hv-empty">{EMPTY_MSG}</p>
          ) : (
            <>
              <div className="hv-patrimony-grid">
                {member.annual_income_total != null && (
                  <div className="hv-patrimony-card">
                    <div className="hv-patrimony-value">{formatCurrency(member.annual_income_total)}</div>
                    <div className="hv-patrimony-label">Ingresos anuales totales</div>
                  </div>
                )}
                {member.public_income_total != null && (
                  <div className="hv-patrimony-card">
                    <div className="hv-patrimony-value">{formatCurrency(member.public_income_total)}</div>
                    <div className="hv-patrimony-label">Ingresos del sector público</div>
                  </div>
                )}
                {member.private_income_total != null && (
                  <div className="hv-patrimony-card">
                    <div className="hv-patrimony-value">{formatCurrency(member.private_income_total)}</div>
                    <div className="hv-patrimony-label">Ingresos del sector privado</div>
                  </div>
                )}
                {member.assets_declared_value != null && (
                  <div className="hv-patrimony-card">
                    <div className="hv-patrimony-value">{formatCurrency(member.assets_declared_value)}</div>
                    <div className="hv-patrimony-label">Valor declarado total de bienes</div>
                  </div>
                )}
                <div className="hv-patrimony-card">
                  <div className="hv-patrimony-value">{member.immovable_assets_count}</div>
                  <div className="hv-patrimony-label">Bienes inmuebles</div>
                </div>
                <div className="hv-patrimony-card">
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
      <details className="hv-section">
        <summary>
          Antecedentes documentales
          <span>
            ({member.penal_sentences_count + member.civil_sentences_count + member.obligations_count + member.marginal_annotations_count} registros)
          </span>
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
            Información extraída de la Hoja de Vida oficial presentada ante el JNE. No constituye antecedentes penales ni civiles definitivos.
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
          Ver hoja de vida completa en JNE →
        </a>
      )}
    </div>
  );
}
