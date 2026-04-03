import Link from "next/link";
import { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <>
      <header className="topbar">
        <Link className="topbar-logo" href="/">
          <div className="logo-mark">
            <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="8" cy="8" r="6" stroke="white" strokeWidth="1.5" />
              <path d="M5 8h6M8 5v6" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </div>
          <span className="logo-text">Pulso Cívico</span>
        </Link>

        <nav className="topbar-nav">
          <Link className="nav-btn" href="/">
            Fórmulas 2026
          </Link>
          <Link className="nav-btn" href="/candidates">
            Candidatos
          </Link>
          <Link className="nav-btn" href="/compare">
            Comparar
          </Link>
          <Link className="nav-btn nav-btn--highlight" href="/asistente">
            Asistente IA
          </Link>
        </nav>
      </header>
      {children}
    </>
  );
}

