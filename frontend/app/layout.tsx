import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Bean-sounds",
  description: "AI song generator for Afro-inspired music",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
