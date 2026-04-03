"use client";

import { useMemo, useState } from "react";

import { Candidate } from "@/lib/types";
import { CandidateCard } from "@/components/CandidateCard";

type CandidatesExplorerProps = {
  candidates: Candidate[];
  query?: string;
};

export function CandidatesExplorer({ candidates, query = "" }: CandidatesExplorerProps) {
  const [region, setRegion] = useState("todos");

  const regions = useMemo(
    () => ["todos", ...Array.from(new Set(candidates.map((candidate) => candidate.region))).sort()],
    [candidates],
  );

  const filtered = useMemo(() => {
    return candidates.filter((candidate) => {
      const byRegion = region === "todos" || candidate.region === region;
      const q = query.trim().toLowerCase();
      const byQuery =
        !q ||
        [candidate.name, candidate.party, candidate.region, candidate.office ?? "", candidate.biography ?? ""]
          .join(" ")
          .toLowerCase()
          .includes(q);

      return byRegion && byQuery;
    });
  }, [candidates, query, region]);

  return (
    <section className="section">
      <h1 className="section-title page-title">Candidatos</h1>
      <p className="page-subtitle">Explora perfiles sin opinión editorial y con enlaces a fuentes documentadas.</p>

      <div className="filters-bar">
        {regions.map((item) => (
          <button
            className={`filter-chip ${item === region ? "active" : ""}`}
            key={item}
            onClick={() => setRegion(item)}
            type="button"
          >
            {item === "todos" ? "Todos" : item}
          </button>
        ))}
      </div>

      <div className="results-count">
        Mostrando {filtered.length} candidato{filtered.length === 1 ? "" : "s"}
      </div>

      <div className="cards-grid">
        {filtered.map((candidate) => (
          <CandidateCard candidate={candidate} key={candidate.id} />
        ))}
      </div>
    </section>
  );
}

