// Vercel Serverless Function — proxy Spotify pour Metal Card Master
// GET /api/spotify?artist=<nom du groupe> -> { name, image, spotifyUrl, genres }
// Le Client ID/Secret Spotify restent cote serveur (variables d'environnement Vercel),
// jamais exposes au navigateur.

let cachedToken = null;
let cachedTokenExpiry = 0;

async function getSpotifyToken() {
  const now = Date.now();
  if (cachedToken && now < cachedTokenExpiry) return cachedToken;

  const clientId = process.env.SPOTIFY_CLIENT_ID;
  const clientSecret = process.env.SPOTIFY_CLIENT_SECRET;
  if (!clientId || !clientSecret) {
    throw new Error("missing_spotify_credentials");
  }

  const creds = Buffer.from(`${clientId}:${clientSecret}`).toString("base64");
  const res = await fetch("https://accounts.spotify.com/api/token", {
    method: "POST",
    headers: {
      Authorization: `Basic ${creds}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: "grant_type=client_credentials",
  });
  if (!res.ok) throw new Error("spotify_token_failed:" + res.status);
  const data = await res.json();
  cachedToken = data.access_token;
  cachedTokenExpiry = now + (data.expires_in - 60) * 1000; // marge de 60s
  return cachedToken;
}

async function searchArtist(name) {
  const token = await getSpotifyToken();
  const url =
    "https://api.spotify.com/v1/search?type=artist&limit=1&q=" +
    encodeURIComponent(name);
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error("spotify_search_failed:" + res.status);
  const data = await res.json();
  const artist = data.artists && data.artists.items && data.artists.items[0];
  if (!artist) return null;
  const image = artist.images && artist.images[0] ? artist.images[0].url : null;
  return {
    name: artist.name,
    image,
    spotifyUrl: artist.external_urls ? artist.external_urls.spotify : null,
    genres: artist.genres || [],
  };
}

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.status(204).end();
    return;
  }

  const artistName = req.query.artist;
  if (!artistName) {
    res.status(400).json({ error: "missing_artist_param" });
    return;
  }

  try {
    const result = await searchArtist(artistName);
    if (!result) {
      res.status(404).json({ error: "artist_not_found" });
      return;
    }
    res.setHeader("Cache-Control", "public, max-age=86400"); // 24h
    res.status(200).json(result);
  } catch (err) {
    res.status(502).json({ error: String(err.message || err) });
  }
}
