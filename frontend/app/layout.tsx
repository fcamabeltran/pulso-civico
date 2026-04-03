import type { Metadata } from "next";
import { Playfair_Display, DM_Sans } from "next/font/google";

import { AppShell } from "@/components/AppShell";
import "./globals.css";

const display = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-display",
});

const body = DM_Sans({
  subsets: ["latin"],
  variable: "--font-body",
});

export const metadata: Metadata = {
  title: "Pulso Cívico",
  description: "Explora y compara candidatos con datos documentados, sin opinión editorial.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body className={`${display.variable} ${body.variable}`}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}

