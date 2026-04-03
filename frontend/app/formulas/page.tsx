import { FormulasExplorer } from "@/components/FormulasExplorer";
import { getFormulas } from "@/lib/api";
import { PresidentialFormula } from "@/lib/types";

export const metadata = {
  title: "Fórmulas Presidenciales 2026 — Pulso Cívico",
  description:
    "Conoce quiénes integran cada fórmula presidencial: presidente y vicepresidentes de los 35 partidos inscritos para las Elecciones Generales 2026.",
};

export default async function FormulasPage() {
  let formulas: PresidentialFormula[] = [];
  let error: string | null = null;

  try {
    formulas = await getFormulas();
  } catch {
    error = "No se pudo cargar la información. Intenta nuevamente en unos momentos.";
  }

  return (
    <>
      {/* Hero */}
      <section className="formulas-hero">
        <div className="formulas-hero-inner">
          <div className="hero-eyebrow">Guía electoral · Perú 2026</div>
          <h1 className="formulas-hero-title">
            ¿No sabes por quién{" "}
            <em className="formulas-hero-em">votar?</em>{" "}
            Empieza aquí.
          </h1>
          <p className="formulas-hero-sub">
            {formulas.length > 0 ? formulas.length : 35} partidos compiten por la
            presidencia. Haz clic en cualquiera para ver la fórmula completa: presidente
            y vicepresidentes.
          </p>
          <div className="formulas-steps">
            {[
              "Explora o busca un partido",
              "Haz clic para ver la fórmula",
              "Compara y decide con información",
            ].map((step, i) => (
              <div key={i} className="formulas-step">
                <span className="formulas-step-num">{i + 1}</span>
                {step}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Aviso neutralidad */}
      <div className="formulas-neutral-bar">
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" width="16" height="16">
          <circle cx="8" cy="8" r="6.5" />
          <path d="M8 5v3.5l2 1.5" strokeLinecap="round" />
        </svg>
        <span>
          <strong>Información neutral y verificada.</strong> Los datos provienen del
          Jurado Nacional de Elecciones (JNE). No promovemos ningún partido ni candidato.
        </span>
      </div>

      {error ? (
        <div className="formulas-error">
          <p>{error}</p>
        </div>
      ) : (
        <FormulasExplorer formulas={formulas} />
      )}
    </>
  );
}
