export const AXIS_ICONS: Record<string, string> = {
  Agua: "💧",
  Economia: "💼",
  "Economía": "💼",
  Salud: "🏥",
  Educacion: "📚",
  "Educación": "📚",
  Seguridad: "🛡️",
  "Medio Ambiente": "🌿",
};

export const PROMISE_STYLES: Record<string, { label: string; className: string }> = {
  cumplida: { label: "Cumplida", className: "badge-kept" },
  pendiente: { label: "Pendiente", className: "badge-pending" },
  incumplida: { label: "Incumplida", className: "badge-broken" },
  parcial: { label: "Parcial", className: "badge-partial" },
};

export function initialsFromName(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

export function colorFromId(id: number): string {
  const colors = ["#1A4D8F", "#C0522A", "#2D6A4F", "#6B3F8C", "#B5451B", "#14617A", "#8B4513", "#1E5C3A"];
  return colors[id % colors.length];
}

export function displayName(value: string): string {
  const upper = value.trim().toUpperCase();
  if (!upper) return value;

  const keepUpper = new Set(["IA", "JNE", "APP", "SIS", "ESSALUD", "PRIN"]);
  return upper
    .split(" ")
    .filter(Boolean)
    .map((part) => {
      if (keepUpper.has(part)) return part;
      if (part.length <= 2 && /^[A-Z0-9]+$/.test(part)) return part;
      return `${part[0]}${part.slice(1).toLowerCase()}`;
    })
    .join(" ");
}
