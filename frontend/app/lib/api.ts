export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

export type Vibe = "Afro-fusion" | "Afrobeats" | "Highlife" | "Gospel" | "House";
export type Energy = "Low" | "Medium" | "High" | "Peak";

export interface Song {
  id: string;
  title: string;
  lyrics: string;
  sections: string[];
  mood: string;
  bpm: number;
  duration: number;
  key: string;
  energy: Energy;
  generated_by: string;
  audio_url: string | null;
  audio_provider: string | null;
  prompt: string;
  vibe: Vibe;
  created_at: string;
}

export interface SongListItem {
  id: string;
  title: string;
  vibe: Vibe;
  created_at: string;
  audio_url: string | null;
}

function headers(): Record<string, string> {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (API_KEY) h["X-API-Key"] = API_KEY;
  return h;
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {}
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export async function generateSong(input: {
  prompt: string;
  vibe: Vibe;
  duration: number;
  with_audio?: boolean;
}): Promise<Song> {
  const res = await fetch(`${API_URL}/api/generate`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(input),
  });
  return handle<Song>(res);
}

export async function generateAudio(songId: string): Promise<Song> {
  const res = await fetch(`${API_URL}/api/generate-audio`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ song_id: songId }),
  });
  return handle<Song>(res);
}

export async function listSongs(limit = 20): Promise<SongListItem[]> {
  const res = await fetch(`${API_URL}/api/songs?limit=${limit}`, { headers: headers() });
  return handle<SongListItem[]>(res);
}

export async function getSong(id: string): Promise<Song> {
  const res = await fetch(`${API_URL}/api/songs/${id}`, { headers: headers() });
  return handle<Song>(res);
}

export function absoluteAudioUrl(url: string | null): string | null {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  return `${API_URL}${url}`;
}
