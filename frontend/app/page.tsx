import Link from "next/link";
import { Footer } from "@/components/Footer";
import { FormulasExplorer } from "@/components/FormulasExplorer";
import { AssistantPanel } from "@/components/AssistantPanel";
import { getFormulas } from "@/lib/api";
import { PresidentialFormula } from "@/lib/types";

export default async function HomePage() {
  let formulas: PresidentialFormula[] = [];
  try {
    formulas = await getFormulas();
  } catch {
    // Muestra vacío — el explorer maneja el estado
  }

  return (
    <>
      {/* ── HERO COMPACTO ─────────────────────────────── */}
      <section className="home-hero">
        <div className="home-hero-inner">
          <div className="home-hero-layout">
            <div className="home-hero-copy">
              <div className="hero-eyebrow">Perú · Elecciones Generales 2026</div>
              <h1 className="home-hero-title">Consulta, compara y entiende candidaturas con fuentes públicas.</h1>
              <p className="home-hero-sub">
                Pulso Cívico te permite revisar {formulas.length > 0 ? formulas.length : 35} fórmulas presidenciales, explorar candidatos,
                comparar propuestas y preguntar al asistente IA sin recomendación editorial.
              </p>
              <div className="home-hero-pills">
                <span className="home-pill">
                  <span className="home-pill-dot" />
                  Datos: JNE oficial
                </span>
                <span className="home-pill">
                  <span className="home-pill-dot" />
                  Sin sesgo editorial
                </span>
                <span className="home-pill">
                  <span className="home-pill-dot" />
                  Fuentes verificables
                </span>
              </div>
            </div>

            <div className="home-value-panel">
              <div className="home-value-kicker">Qué puedes hacer aquí</div>
              <div className="home-value-list">
                <div className="home-value-item">
                  <strong>Ver fórmulas presidenciales</strong>
                  <span>Haz clic en un partido y revisa quiénes integran la fórmula.</span>
                </div>
                <div className="home-value-item">
                  <strong>Explorar candidatos</strong>
                  <span>Consulta propuestas, hoja de vida, resúmenes y documentos.</span>
                </div>
                <div className="home-value-item">
                  <strong>Comparar propuestas</strong>
                  <span>Contrasta dos candidaturas por tema con lectura guiada.</span>
                </div>
                <div className="home-value-item">
                  <strong>Preguntar a la IA</strong>
                  <span>Resuelve dudas temáticas con evidencia recuperada del corpus.</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="home-actions">
        <div className="home-tools-inner">
          <div className="home-tools-header home-tools-header--tight">
            <h2 className="home-tools-title">Explora la plataforma</h2>
            <p className="home-tools-sub">
              Elige una ruta de entrada. Todo el producto queda visible desde aquí, sin depender de mucho scroll.
            </p>
          </div>
          <div className="home-tools-grid">
            <Link href="/formulas" className="home-tool-card home-tool-card--primary">
              <div className="tool-icon tool-icon--navy">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" width="22" height="22">
                  <path d="M4 19V5l7 4 9-5v14l-9 5-7-4Z" strokeLinejoin="round" />
                  <path d="M11 9v10" />
                </svg>
              </div>
              <div className="tool-info">
                <div className="tool-name">Fórmulas presidenciales</div>
                <div className="tool-desc">Revisa partidos y quiénes integran cada fórmula en una vista interactiva.</div>
              </div>
              <svg className="tool-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                <path d="m9 18 6-6-6-6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </Link>

            <Link href="/candidates" className="home-tool-card">
              <div className="tool-icon tool-icon--blue">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" width="22" height="22">
                  <circle cx="12" cy="8" r="4" />
                  <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" strokeLinecap="round" />
                </svg>
              </div>
              <div className="tool-info">
                <div className="tool-name">Explorar candidatos</div>
                <div className="tool-desc">Propuestas por eje, hoja de vida y seguimiento de promesas.</div>
              </div>
              <svg className="tool-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                <path d="m9 18 6-6-6-6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </Link>

            <Link href="/compare" className="home-tool-card">
              <div className="tool-icon tool-icon--terra">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" width="22" height="22">
                  <rect x="3" y="3" width="8" height="18" rx="2" />
                  <rect x="13" y="3" width="8" height="18" rx="2" />
                </svg>
              </div>
              <div className="tool-info">
                <div className="tool-name">Comparar dos candidatos</div>
                <div className="tool-desc">Lado a lado por eje temático. Listo para compartir.</div>
              </div>
              <svg className="tool-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                <path d="m9 18 6-6-6-6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </Link>

            <Link href="/asistente" className="home-tool-card">
              <div className="tool-icon tool-icon--gold">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" width="22" height="22">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" strokeLinejoin="round" />
                </svg>
              </div>
              <div className="tool-info">
                <div className="tool-name">Asistente IA</div>
                <div className="tool-desc">Pregunta por tema: "¿Qué propone X sobre agua en Piura?"</div>
              </div>
              <svg className="tool-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                <path d="m9 18 6-6-6-6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </Link>

          </div>
        </div>
      </section>

      <section className="home-overview">
        <div className="home-overview-inner">
          <div className="home-overview-card">
            <div className="home-overview-metric">{formulas.length > 0 ? formulas.length : 35}</div>
            <div className="home-overview-label">fórmulas presidenciales cargadas</div>
          </div>
          <div className="home-overview-card">
            <div className="home-overview-metric">4</div>
            <div className="home-overview-label">formas principales de explorar el voto informado</div>
          </div>
          <div className="home-overview-card">
            <div className="home-overview-metric">0</div>
            <div className="home-overview-label">puntajes editoriales o recomendación de voto</div>
          </div>
        </div>
      </section>

      {/* ── FÓRMULAS (contenido principal) ────────────── */}
      <FormulasExplorer formulas={formulas} />

      {/* ── ASISTENTE IA ──────────────────────────────── */}
      <AssistantPanel />

      {/* ── NOTA METODOLÓGICA ──────────────────────────── */}
      <section className="home-method">
        <div className="home-method-inner">
          <div className="method-note">
            <span className="method-icon">ℹ️</span>
            <span>
              Pulso Cívico usa fuentes oficiales: JNE, Voto Informado e INFOGOB.
              No editorializa ni recomienda voto. Toda respuesta del asistente IA
              expone la fuente del fragmento utilizado.
            </span>
          </div>
        </div>
      </section>

      <Footer />
    </>
  );
}
