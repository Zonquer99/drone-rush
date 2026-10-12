// Drone Rush · tg-auth
// Comprueba con la firma de Telegram que el jugador es quien dice ser
// y liga su partida a su cuenta de Telegram (o se la devuelve si cambia de móvil).
import { createClient } from "npm:@supabase/supabase-js@2";

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

// Verificación oficial de initData de Telegram Mini Apps
export async function verifyInitData(initData: string, botToken: string, maxAgeSec = 86400) {
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

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  try {
    const BOT = Deno.env.get("TELEGRAM_BOT_TOKEN");
    if (!BOT) return json({ error: "falta TELEGRAM_BOT_TOKEN" }, 500);
    const { initData } = await req.json();
    const tg = await verifyInitData(String(initData || ""), BOT);
    if (!tg) return json({ error: "telegram_no_valido" }, 401);

    const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
    const jwt = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
    const { data: { user }, error: uErr } = await admin.auth.getUser(jwt);
    if (uErr || !user) return json({ error: "sin_sesion" }, 401);
    const uid = user.id;

    const { data: owner } = await admin.from("players").select("id,name,save").eq("tg_id", tg.id).maybeSingle();
    const { data: mine } = await admin.from("players").select("id,name,save").eq("id", uid).maybeSingle();

    // Primera vez con esta cuenta de Telegram (o ya es la misma sesión): la ligamos
    if (!owner || owner.id === uid) {
      if (mine) await admin.from("players").update({ tg_id: tg.id }).eq("id", uid);
      return json({ status: mine ? "linked" : "no_row" });
    }

    // Esta cuenta de Telegram ya tenía partida en otra sesión (otro móvil, datos borrados…)
    const ownerGames = Number(owner.save?.games || 0), mineGames = Number(mine?.save?.games || 0);
    if (mine && mineGames > ownerGames) {
      // la sesión actual va más avanzada: se queda esta y se borra la vieja
      await admin.from("players").delete().eq("id", owner.id);
      await admin.from("players").update({ tg_id: tg.id }).eq("id", uid);
      return json({ status: "linked" });
    }
    // se recupera la partida guardada y pasa a esta sesión
    if (mine) await admin.from("players").delete().eq("id", uid);
    const { error: mvErr } = await admin.from("players").update({ id: uid }).eq("id", owner.id);
    if (mvErr) return json({ error: mvErr.message }, 500);
    return json({ status: "restored", name: owner.name, save: owner.save });
  } catch (e) {
    return json({ error: String(e) }, 500);
  }
});
