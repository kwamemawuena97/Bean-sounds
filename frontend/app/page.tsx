"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Song,
  SongListItem,
  Vibe,
  absoluteAudioUrl,
  generateAudio,
  generateSong,
  getSong,
  listSongs,
} from "./lib/api";

const VIBES: Vibe[] = ["Afro-fusion", "Afrobeats", "Highlife", "Gospel", "House"];

const PROMPT_SUGGESTIONS: Record<Vibe, string[]> = {
  "Afro-fusion": ["Sunset in Accra with a deep afrobeat groove", "Lagos rooftop after the rain"],
  Afrobeats: ["Summer party by the ocean", "Late-night ride through the city"],
  Highlife: ["Palm-wine session with old friends", "Village festival at dawn"],
  Gospel: ["Sunday morning gratitude", "Choir rising after the storm"],
  House: ["Neon warehouse at 2am", "Sunrise beach set in Cape Town"],
};

const PLACEHOLDER_TRACK = {
  title: "Your next track",
  hint: "Describe a moment, a place, or a feeling. We'll turn it into a song.",
  bpm: 110,
  duration: 90,
  key: "A",
  energy: "Medium" as const,
};

function isNetworkError(err: unknown): boolean {
  if (!(err instanceof Error)) return false;
  const msg = err.message.toLowerCase();
  return msg.includes("failed to fetch") || msg.includes("networkerror") || msg.includes("load failed");
}

export default function Home() {
  const [prompt, setPrompt] = useState(PROMPT_SUGGESTIONS["Afro-fusion"][0]);
  const [vibe, setVibe] = useState<Vibe>("Afro-fusion");
  const [duration, setDuration] = useState(90);
  const [withAudio, setWithAudio] = useState(true);
  const [song, setSong] = useState<Song | null>(null);
  const [loading, setLoading] = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<SongListItem[]>([]);

  const refreshHistory = () => {
    listSongs(20).then(setHistory).catch(() => {});
  };

  useEffect(() => {
    refreshHistory();
  }, []);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await generateSong({ prompt, vibe, duration, with_audio: withAudio });
      setSong(result);
      refreshHistory();
    } catch (err) {
      setError(
        isNetworkError(err)
          ? "The backend isn't running yet. Start the FastAPI server to enable generation."
          : err instanceof Error
            ? err.message
            : "Something went wrong",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAddAudio = async () => {
    if (!song) return;
    setAudioLoading(true);
    setError(null);
    try {
      const updated = await generateAudio(song.id);
      setSong(updated);
      refreshHistory();
    } catch (err) {
      setError(
        isNetworkError(err)
          ? "The backend isn't running yet. Start the FastAPI server to enable generation."
          : err instanceof Error
            ? err.message
            : "Audio generation failed",
      );
    } finally {
      setAudioLoading(false);
    }
  };

  const loadFromHistory = async (id: string) => {
    setError(null);
    try {
      const full = await getSong(id);
      setSong(full);
      setPrompt(full.prompt);
      setVibe(full.vibe);
      setDuration(full.duration);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load song");
    }
  };

  const audioSrc = absoluteAudioUrl(song?.audio_url ?? null);

  const preview = useMemo(
    () => ({
      title: song?.title ?? PLACEHOLDER_TRACK.title,
      bpm: song?.bpm ?? PLACEHOLDER_TRACK.bpm,
      duration: song?.duration ?? PLACEHOLDER_TRACK.duration,
      key: song?.key ?? PLACEHOLDER_TRACK.key,
      energy: song?.energy ?? PLACEHOLDER_TRACK.energy,
    }),
    [song],
  );

  return (
    <main className="page">
      <div className="container">
        <header className="header">
          <div className="brand">
            <div className="brand-mark" aria-hidden />
            <span>Bean-sounds</span>
          </div>
          <h1>AI song sketches with Afro soul</h1>
          <p>Describe a scene, choose a vibe, and get a full song idea with playable audio.</p>
        </header>

        <div className="grid">
          <form onSubmit={handleSubmit} className="panel form" aria-label="Song prompt">
            <label className="field">
              <span className="label">Prompt</span>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
                required
                maxLength={2000}
                placeholder="e.g. Sunset in Accra with a deep afrobeat groove"
              />
              <div className="chips" role="list" aria-label="Prompt suggestions">
                {PROMPT_SUGGESTIONS[vibe].map((s) => (
                  <button key={s} type="button" className="chip" onClick={() => setPrompt(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </label>

            <div className="row">
              <label className="field">
                <span className="label">Vibe</span>
                <select value={vibe} onChange={(e) => setVibe(e.target.value as Vibe)}>
                  {VIBES.map((v) => (
                    <option key={v}>{v}</option>
                  ))}
                </select>
              </label>

              <label className="field">
                <span className="label">Duration</span>
                <div className="input-suffix">
                  <input
                    type="number"
                    min={30}
                    max={240}
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                  />
                  <span>seconds</span>
                </div>
              </label>
            </div>

            <label className="toggle">
              <input type="checkbox" checked={withAudio} onChange={(e) => setWithAudio(e.target.checked)} />
              <span className="toggle-track" aria-hidden><span className="toggle-thumb" /></span>
              <span className="toggle-label">Generate audio preview</span>
            </label>

            <button type="submit" disabled={loading} className="primary">
              {loading ? "Generating…" : "Generate song"}
            </button>

            {error && (
              <div className="error" role="alert">
                <strong>Heads up.</strong> {error}
              </div>
            )}
          </form>

          <section className={`panel track ${song ? "" : "track-placeholder"}`} aria-label="Current track">
            <div className="track-head">
              <div className="eyebrow">Current track</div>
              {song && <div className="badge">{song.generated_by}</div>}
            </div>

            <div className="pills">
              <span>{preview.bpm} BPM</span>
              <span>{preview.duration}s</span>
              <span>Key {preview.key}</span>
              <span>{preview.energy}</span>
            </div>

            <h2>{preview.title}</h2>

            {song ? (
              audioSrc ? (
                <audio controls src={audioSrc} className="player" preload="metadata" />
              ) : (
                <button className="secondary" onClick={handleAddAudio} disabled={audioLoading}>
                  {audioLoading ? "Rendering audio…" : "Generate audio preview"}
                </button>
              )
            ) : (
              <div className="hint">{PLACEHOLDER_TRACK.hint}</div>
            )}

            {song && <div className="lyrics">{song.lyrics}</div>}

            {song && song.sections.length > 0 && (
              <div className="sections">
                <div className="eyebrow">Structure</div>
                {song.sections.map((s, i) => (
                  <div key={i} className="section">{s}</div>
                ))}
              </div>
            )}
          </section>
        </div>

        {history.length > 0 && (
          <section className="history" aria-label="Recent tracks">
            <div className="eyebrow dark">Recent tracks</div>
            <div className="history-grid">
              {history.map((h) => (
                <button key={h.id} className="history-card" onClick={() => loadFromHistory(h.id)}>
                  <div className="history-title">{h.title}</div>
                  <div className="history-meta">
                    <span className="tag">{h.vibe}</span>
                    {h.audio_url && <span className="dot">● audio</span>}
                  </div>
                </button>
              ))}
            </div>
          </section>
        )}

        <footer className="footer">
          Prototype · lyrics via Gemini · audio via Lyria (or built-in fallback)
        </footer>
      </div>
    </main>
  );
}
