// Drone Rush · share-record
// Recibe la carta de récord (imagen) y:
//  · mode "group": el bot la publica en @dronerushchat
//  · mode "friend": prepara un mensaje para que el jugador lo mande al chat que elija (WebApp.shareMessage)
import { createClient } from "npm:@supabase/supabase-js@2";

const GROUP = "@dronerushchat";
const BOT_USER = "dronerushhbot";
const LIMITS = { group: { perDay: 3, gapMin: 10 }, friend: { perDay: 30, gapMin: 0 } };

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const json = (b: unknown, status = 200) =>
  new Response(JSON.stringify(b), { status, headers: { ...cors, "Content-Type": "application/json" } });

const enc = new TextEncoder();
async function hmac(key: Uint8Array, data: string) {
  const k = await crypto.subtle.importKey("raw", key, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return new Uint8Array(await crypto.subtle.sign("HMAC", k, enc.encode(data)));
}
const hex = (b: Uint8Array) => [...b].map((x) => x.toString(16).padStart(2, "0")).join("");
async function verifyInitData(initData: string, botToken: string, maxAgeSec = 86400) {
  const p = new URLSearchParams(initData);
  const hash = p.get("hash");
  if (!hash) return null;
  p.delete("hash");
  const dcs = [...p.entries()].sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0)).map(([k, v]) => `${k}=${v}`).join("\n");
  const secret = await hmac(enc.encode("WebAppData"), botToken);
  if (hex(await hmac(secret, dcs)) !== hash) return null;
  const authDate = Number(p.get("auth_date") || 0);
  if (!authDate || Date.now() / 1000 - authDate > maxAgeSec) return null;
  const user = JSON.parse(p.get("user") || "null");
  return user && user.id ? user : null;
}

const fmt = (n: number, en: boolean) => Math.floor(n).toLocaleString(en ? "en-US" : "es-ES");
const clean = (s: unknown, max: number) => String(s ?? "").replace(/[\u0000-\u001f<>]/g, "").trim().slice(0, max);

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  try {
    const BOT = Deno.env.get("TELEGRAM_BOT_TOKEN");
    if (!BOT) return json({ error: "falta TELEGRAM_BOT_TOKEN" }, 500);
    const body = await req.json();
    const mode = body.mode === "friend" ? "friend" : "group";
    const tg = await verifyInitData(String(body.initData || ""), BOT);
    if (!tg) return json({ error: "telegram_no_valido" }, 401);

    const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
    const jwt = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
    const { data: { user } } = await admin.auth.getUser(jwt);
    if (!user) return json({ error: "sin_sesion" }, 401);

    // el récord tiene que coincidir con el guardado en la nube
    const { data: pl } = await admin.from("players").select("name,best").eq("id", user.id).maybeSingle();
    const m = Math.floor(Number(body.m) || 0);
    if (!pl || m <= 0 || m > Number(pl.best || 0)) return json({ error: "record_no_valido" });

    // límites anti-spam
    const lim = LIMITS[mode];
    const since = new Date(Date.now() - 86400000).toISOString();
    const { data: logs } = await admin.from("record_shares").select("created_at").eq("tg_id", tg.id).eq("kind", mode).gte("created_at", since).order("created_at", { ascending: false });
    if ((logs?.length || 0) >= lim.perDay) return json({ error: "limite" });
    if (lim.gapMin && logs?.length && Date.now() - new Date(logs[0].created_at).getTime() < lim.gapMin * 60000) return json({ error: "espera" });

    // imagen
    const b64 = String(body.img || "");
    if (!b64 || b64.length > 2_000_000) return json({ error: "imagen_no_valida" });
    const img = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
    if (!(img[0] === 0xff && img[1] === 0xd8) && !(img[0] === 0x89 && img[1] === 0x50)) return json({ error: "imagen_no_valida" });
    const isJpg = img[0] === 0xff;

    const en = body.lang === "en";
    const name = clean(pl.name, 20) || "Piloto";
    const skin = clean(body.skin, 30);
    const ref = /^[A-Za-z0-9_-]{3,40}$/.test(String(body.ref || "")) ? String(body.ref) : "";
    const playUrl = `https://t.me/${BOT_USER}${ref ? `?startapp=${ref}` : "?startapp"}`;
    const markup = { inline_keyboard: [[{ text: en ? "🚁 Beat it" : "🚁 Supérame", url: playUrl }]] };

    if (mode === "group") {
      const caption = en
        ? `🏆 ${name} just set a new record: ${fmt(m, true)} m${skin ? ` with ${skin}` : ""}!\nWho can beat it? 👇`
        : `🏆 ¡${name} ha batido su récord: ${fmt(m, false)} m${skin ? ` con ${skin}` : ""}!\n¿Quién le supera? 👇`;
      const fd = new FormData();
      fd.append("chat_id", GROUP);
      fd.append("caption", caption);
      fd.append("reply_markup", JSON.stringify(markup));
      fd.append("photo", new Blob([img], { type: isJpg ? "image/jpeg" : "image/png" }), isJpg ? "record.jpg" : "record.png");
      const r = await fetch(`https://api.telegram.org/bot${BOT}/sendPhoto`, { method: "POST", body: fd }).then((x) => x.json());
      if (!r.ok) return json({ error: "telegram", detail: r.description }, 502);
      await admin.from("record_shares").insert({ tg_id: tg.id, kind: mode, meters: m });
      return json({ ok: true, msg: r.result?.message_id || null });
    }

    // friend: subimos la carta (una por jugador, se sobrescribe) y preparamos el mensaje
    const path = `${tg.id}.${isJpg ? "jpg" : "png"}`;
    const up = await admin.storage.from("cards").upload(path, img, { contentType: isJpg ? "image/jpeg" : "image/png", upsert: true });
    if (up.error) return json({ error: "storage", detail: up.error.message }, 500);
    const url = admin.storage.from("cards").getPublicUrl(path).data.publicUrl + `?v=${Date.now()}`;
    const caption = en
      ? `⚔️ I flew ${fmt(m, true)} m in Drone Rush${skin ? ` with ${skin}` : ""}. Can you beat me?`
      : `⚔️ He volado ${fmt(m, false)} m en Drone Rush${skin ? ` con ${skin}` : ""}. ¿Me superas?`;
    const result = { type: "photo", id: crypto.randomUUID().replace(/-/g, "").slice(0, 32), photo_url: url, thumbnail_url: url, caption, reply_markup: markup };
    const r = await fetch(`https://api.telegram.org/bot${BOT}/savePreparedInlineMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: tg.id, result, allow_user_chats: true, allow_group_chats: true, allow_channel_chats: true, allow_bot_chats: false }),
    }).then((x) => x.json());
    if (!r.ok) return json({ error: "telegram", detail: r.description }, 502);
    await admin.from("record_shares").insert({ tg_id: tg.id, kind: mode, meters: m });
    return json({ ok: true, id: r.result.id });
  } catch (e) {
    return json({ error: String(e) }, 500);
  }
});
