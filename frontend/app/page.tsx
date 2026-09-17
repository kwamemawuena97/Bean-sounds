"use client";

import { FormEvent, useEffect, useState } from "react";
import {
  Song,
  SongListItem,
  Vibe,
  absoluteAudioUrl,
  generateAudio,
  generateSong,
  listSongs,
  getSong,
} from "./lib/api";

const VIBES: Vibe[] = ["Afro-fusion", "Afrobeats", "Highlife", "Gospel", "House"];

const PROMPT_SUGGESTIONS: Record<Vibe, string[]> = {
  "Afro-fusion": ["Sunset in Accra with a deep afrobeat groove", "Lagos rooftop after the rain"],
  Afrobeats: ["Summer party by the ocean", "Late-night ride through the city"],
  Highlife: ["Palm-wine session with old friends", "Village festival at dawn"],
  Gospel: ["Sunday morning gratitude", "Choir rising after the storm"],
  House: ["Neon warehouse at 2am", "Sunrise beach set in Cape Town"],
};

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
      setError(err instanceof Error ? err.message : "Something went wrong");
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
      setError(err instanceof Error ? err.message : "Audio generation failed");
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

  return (
    <main className="page">
      <div className="container">
        <header className="header">
          <h1>Bean-sounds</h1>
          <p>AI-powered song generation inspired by Afro rhythms and modern production.</p>
        </header>

        <div className="grid">
          <form onSubmit={handleSubmit} className="panel form">
            <label className="field">
              <span className="label">Prompt</span>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
                required
                maxLength={2000}
              />
              <div className="chips">
                {PROMPT_SUGGESTIONS[vibe].map((s) => (
                  <button key={s} type="button" className="chip" onClick={() => setPrompt(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </label>

            <label className="field">
              <span className="label">Vibe</span>
              <select value={vibe} onChange={(e) => setVibe(e.target.value as Vibe)}>
                {VIBES.map((v) => (
                  <option key={v}>{v}</option>
                ))}
              </select>
            </label>

            <label className="field">
              <span className="label">Duration (seconds)</span>
              <input
                type="number"
                min={30}
                max={240}
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
              />
            </label>

            <label className="checkbox">
              <input type="checkbox" checked={withAudio} onChange={(e) => setWithAudio(e.target.checked)} />
              <span>Generate audio preview</span>
            </label>

            <button type="submit" disabled={loading} className="primary">
              {loading ? "Generating..." : "Generate Song"}
            </button>

            {error && <div className="error" role="alert">{error}</div>}
          </form>

          <section className="panel track">
            <div className="eyebrow">Current track</div>
            {song ? (
              <>
                <div className="pills">
                  <span>{song.bpm} BPM</span>
                  <span>{song.duration}s</span>
                  <span>Key {song.key}</span>
                  <span>{song.energy}</span>
                  <span className="pill-muted">{song.generated_by}</span>
                </div>
                <h2>{song.title}</h2>
                {audioSrc ? (
                  <audio controls src={audioSrc} className="player" />
                ) : (
                  <button className="secondary" onClick={handleAddAudio} disabled={audioLoading}>
                    {audioLoading ? "Rendering audio..." : "Generate audio preview"}
                  </button>
                )}
                <div className="lyrics">{song.lyrics}</div>
                {song.sections.length > 0 && (
                  <div className="sections">
                    <div className="eyebrow">Structure</div>
                    {song.sections.map((s, i) => (
                      <div key={i} className="section">{s}</div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <div className="empty">Compose your first song to hear it come alive.</div>
            )}
          </section>
        </div>

        {history.length > 0 && (
          <section className="history">
            <div className="eyebrow dark">Recent tracks</div>
            <div className="history-grid">
              {history.map((h) => (
                <button key={h.id} className="history-card" onClick={() => loadFromHistory(h.id)}>
                  <div className="history-title">{h.title}</div>
                  <div className="history-meta">
                    <span>{h.vibe}</span>
                    {h.audio_url && <span className="dot">audio</span>}
                  </div>
                </button>
              ))}
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
