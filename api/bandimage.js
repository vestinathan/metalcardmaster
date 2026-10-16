// Vercel Serverless Function — recherche d'image de groupe via Wikipedia/Wikimedia
// GET /api/bandimage?band=<nom du groupe> -> { name, image, sourceUrl, license }
//
// Pourquoi Wikipedia plutôt que Spotify : pas de clé API à protéger (endpoints publics),
// et beaucoup de groupes ont une vraie image (photo ou logo) rattachée à leur page, avec un
// statut de licence affiché sur Commons (contrairement à une photo promo Spotify arbitraire).
//
// Stratégie : 1) on cherche la page Wikipedia (FR puis EN en repli), 2) on prend l'image
// "page image" de l'infobox (REST summary endpoint), qui est le plus souvent le logo ou la
// photo officielle du groupe utilisée dans l'infobox.

const UA = "MetalCardMaster/1.0 (https://github.com/vestinathan/metalcardmaster)";

async function fetchSummary(lang, title) {
  const url =
    `https://${lang}.wikipedia.org/api/rest_v1/page/summary/` +
    encodeURIComponent(title);
  const res = await fetch(url, { headers: { "User-Agent": UA, Accept: "application/json" } });
  if (!res.ok) return null;
  const data = await res.json();
  if (data.type === "disambiguation") return null;
  return data;
}

async function searchTitle(lang, query) {
  const url =
    `https://${lang}.wikipedia.org/w/api.php?action=query&list=search&srsearch=` +
    encodeURIComponent(query) +
    "&format=json&srlimit=1&origin=*";
  const res = await fetch(url, { headers: { "User-Agent": UA, Accept: "application/json" } });
  if (!res.ok) return null;
  const data = await res.json();
  const hit = data.query && data.query.search && data.query.search[0];
  return hit ? hit.title : null;
}

async function findBandImage(bandName) {
  // on essaie FR puis EN ; sur chaque langue, titre exact d'abord, recherche en repli
  const langs = ["fr", "en"];
  for (const lang of langs) {
    let summary = await fetchSummary(lang, bandName);
    if (!summary) {
      const foundTitle = await searchTitle(lang, bandName + " groupe metal");
      if (foundTitle) summary = await fetchSummary(lang, foundTitle);
    }
    if (summary) {
      const img =
        (summary.originalimage && summary.originalimage.source) ||
        (summary.thumbnail && summary.thumbnail.source) ||
        null;
      if (img) {
        return {
          name: summary.title,
          image: img,
          sourceUrl: summary.content_urls && summary.content_urls.desktop
            ? summary.content_urls.desktop.page
            : `https://${lang}.wikipedia.org/wiki/${encodeURIComponent(summary.title)}`,
          license: "Voir la page Wikimedia Commons de l'image pour la licence exacte",
        };
      }
    }
  }
  return null;
}

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.status(204).end();
    return;
  }

  const bandName = req.query.band;
  if (!bandName) {
    res.status(400).json({ error: "missing_band_param" });
    return;
  }

  try {
    const result = await findBandImage(bandName);
    if (!result) {
      res.status(404).json({ error: "image_not_found" });
      return;
    }
    res.setHeader("Cache-Control", "public, max-age=86400"); // 24h
    res.status(200).json(result);
  } catch (err) {
    res.status(502).json({ error: String(err.message || err) });
  }
}
