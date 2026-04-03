export function Footer() {
  return (
    <footer className="site-footer">
      <div className="site-footer-inner">
        <div className="site-footer-top">
          <div className="site-footer-brand">
            <div className="footer-logo-mark">
              <svg viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="6" stroke="white" strokeWidth="1.5" />
                <path d="M5 8h6M8 5v6" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </div>
            <span className="footer-brand-name">Pulso Cívico</span>
          </div>
          <p className="footer-tagline">
            Información electoral estructurada para ciudadanos. Sin puntajes, sin sesgo editorial.
          </p>
        </div>

        <div className="site-footer-mid">
          <div className="footer-col">
            <div className="footer-col-label">Fuentes de datos</div>
            <ul className="footer-links">
              <li>
                <a href="https://votoinformado.jne.gob.pe" target="_blank" rel="noopener noreferrer">
                  JNE — Voto Informado
                </a>
              </li>
              <li>
                <a href="https://infogob.jne.gob.pe" target="_blank" rel="noopener noreferrer">
                  JNE — INFOGOB
                </a>
              </li>
            </ul>
          </div>
          <div className="footer-col">
            <div className="footer-col-label">Plataforma</div>
            <ul className="footer-links">
              <li><a href="/">Inicio</a></li>
              <li><a href="/candidates">Candidatos</a></li>
              <li><a href="/compare">Comparar</a></li>
            </ul>
          </div>
          <div className="footer-col">
            <div className="footer-col-label">Principios</div>
            <ul className="footer-text-list">
              <li>Sin scoring ni recomendación de voto</li>
              <li>Toda información tiene fuente visible</li>
              <li>Sin financiamiento de partidos políticos</li>
            </ul>
          </div>
        </div>

        <div className="site-footer-bottom">
          <span className="footer-neutral-badge">Sin financiamiento partidario</span>
          <span className="footer-separator">·</span>
          <span className="footer-data-source">Datos: JNE Perú · Elecciones Generales 2026</span>
        </div>
      </div>
    </footer>
  );
}
