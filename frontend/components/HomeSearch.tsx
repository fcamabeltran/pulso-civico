"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

export function HomeSearch() {
  const router = useRouter();
  const [query, setQuery] = useState("");

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const target = query.trim();
    if (!target) {
      router.push("/candidates");
      return;
    }
    router.push(`/candidates?q=${encodeURIComponent(target)}`);
  }

  return (
    <form className="hero-search" onSubmit={onSubmit}>
      <input
        className="search-input"
        placeholder="Buscar candidato, partido, región o eje..."
        value={query}
        onChange={(event) => setQuery(event.target.value)}
      />
      <button className="btn-primary" type="submit">
        Buscar
      </button>
    </form>
  );
}

