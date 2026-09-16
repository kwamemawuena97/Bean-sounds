"use client";

import { FormEvent, useState } from "react";

const initialPrompt = "Sunset in Accra with a deep afrobeat groove";

export default function Home() {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [vibe, setVibe] = useState("Afro-fusion");
  const [duration, setDuration] = useState(90);
  const [title, setTitle] = useState("AfroSong AI");
  const [lyrics, setLyrics] = useState("Compose your first song and let the rhythm come alive.");
  const [sections, setSections] = useState<string[]>([]);
  const [bpm, setBpm] = useState(110);
  const [key, setKey] = useState("A");
  const [energy, setEnergy] = useState("Medium");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, vibe, duration }),
      });

      const data = await response.json();
      setTitle(data.title || "New Track");
      setLyrics(data.lyrics || "No lyrics generated yet.");
      setSections(Array.isArray(data.sections) ? data.sections : []);
      setBpm(data.bpm || 110);
      setKey(data.key || "A");
      setEnergy(data.energy || "Medium");
    } catch (error) {
      setLyrics("The backend isn’t running yet. Start the FastAPI server to enable generation.");
      setSections([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main
      style={{
        fontFamily: "Arial, sans-serif",
        minHeight: "100vh",
        padding: 32,
        background: "linear-gradient(135deg, #fef3c7 0%, #f0fdf4 40%, #ecfeff 100%)",
        color: "#111827",
      }}
    >
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <header style={{ marginBottom: 28 }}>
          <h1 style={{ fontSize: 42, margin: 0 }}>Bean-sounds</h1>
          <p style={{ fontSize: 18, color: "#4b5563", marginTop: 10, marginBottom: 0 }}>
            AI-powered song generation inspired by Afro rhythms and modern production.
          </p>
        </header>

        <div style={{ display: "grid", gridTemplateColumns: "1.05fr 1.45fr", gap: 24 }}>
          <form
            onSubmit={handleSubmit}
            style={{
              background: "rgba(255,255,255,0.72)",
              border: "1px solid rgba(15, 118, 110, 0.15)",
              padding: 20,
              borderRadius: 18,
              boxShadow: "0 10px 30px rgba(15, 23, 42, 0.06)",
            }}
          >
            <label style={{ display: "block", marginBottom: 16 }}>
              <div style={{ marginBottom: 8, fontWeight: 700 }}>Prompt</div>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={5}
                style={{
                  width: "100%",
                  padding: 12,
                  borderRadius: 10,
                  border: "1px solid #d1d5db",
                  background: "#fff",
                  resize: "vertical",
                  fontSize: 15,
                }}
              />
            </label>

            <label style={{ display: "block", marginBottom: 16 }}>
              <div style={{ marginBottom: 8, fontWeight: 700 }}>Vibe</div>
              <select
                value={vibe}
                onChange={(e) => setVibe(e.target.value)}
                style={{
                  width: "100%",
                  padding: 12,
                  borderRadius: 10,
                  border: "1px solid #d1d5db",
                  background: "#fff",
                  fontSize: 15,
                }}
              >
                <option>Afro-fusion</option>
                <option>Afrobeats</option>
                <option>Highlife</option>
                <option>Gospel</option>
                <option>House</option>
              </select>
            </label>

            <label style={{ display: "block", marginBottom: 20 }}>
              <div style={{ marginBottom: 8, fontWeight: 700 }}>Duration (seconds)</div>
              <input
                type="number"
                min={30}
                max={240}
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                style={{
                  width: "100%",
                  padding: 12,
                  borderRadius: 10,
                  border: "1px solid #d1d5db",
                  background: "#fff",
                  fontSize: 15,
                }}
              />
            </label>

            <button
              type="submit"
              disabled={loading}
              style={{
                width: "100%",
                background: "linear-gradient(135deg, #16a34a, #15803d)",
                color: "white",
                border: "none",
                padding: "14px 20px",
                borderRadius: 12,
                cursor: loading ? "not-allowed" : "pointer",
                fontSize: 16,
                fontWeight: 700,
                boxShadow: "0 6px 18px rgba(22, 163, 74, 0.25)",
              }}
            >
              {loading ? "Generating..." : "Generate Song"}
            </button>
          </form>

          <section
            style={{
              background: "#111827",
              color: "white",
              padding: 24,
              borderRadius: 18,
              boxShadow: "0 12px 36px rgba(17, 24, 39, 0.2)",
            }}
          >
            <div style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: 1, color: "#a7f3d0" }}>
              Current track
            </div>

            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: 12,
                margin: "18px 0 12px",
              }}
            >
              <span style={{ background: "#1f2937", padding: "8px 12px", borderRadius: 999 }}>{bpm} BPM</span>
              <span style={{ background: "#1f2937", padding: "8px 12px", borderRadius: 999 }}>{duration}s</span>
              <span style={{ background: "#1f2937", padding: "8px 12px", borderRadius: 999 }}>Key {key}</span>
              <span style={{ background: "#1f2937", padding: "8px 12px", borderRadius: 999 }}>{energy}</span>
            </div>

            <h2 style={{ fontSize: 30, margin: "8px 0 14px" }}>{title}</h2>

            <div style={{ whiteSpace: "pre-line", lineHeight: 1.8, fontSize: 18 }}>{lyrics}</div>

            {sections.length > 0 && (
              <div style={{ marginTop: 24 }}>
                <div style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: 1, color: "#a7f3d0", marginBottom: 10 }}>
                  Structure
                </div>
                <div style={{ display: "grid", gap: 10 }}>
                  {sections.map((section, index) => (
                    <div key={index} style={{ background: "#1f2937", padding: 12, borderRadius: 10, whiteSpace: "pre-line" }}>
                      {section}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
