// Drone Rush · daily-notify
// Lo llama un cron una vez al día. Manda por el bot de Telegram un aviso corto
// (casilla del Adviento, fin de temporada…) a quien tiene Telegram ligado, no ha jugado hoy
// y no ha desactivado los avisos. Como mucho 1 aviso al día por jugador.
import { createClient } from "npm:@supabase/supabase-js@2";
import { pickMsg } from "./msgs.ts";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

Deno.serve(async (req) => {
  const SECRET = Deno.env.get("CRON_SECRET");
  if (!SECRET || req.headers.get("x-cron-secret") !== SECRET) return new Response("no", { status: 401 });
  const BOT = Deno.env.get("TELEGRAM_BOT_TOKEN");
  if (!BOT) return new Response("falta TELEGRAM_BOT_TOKEN", { status: 500 });
  const GAME = Deno.env.get("GAME_URL") || "https://t.me/dronerushhbot";
  const dry = new URL(req.url).searchParams.get("dry") === "1";

  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
  const fmt = new Intl.DateTimeFormat("sv-SE", { timeZone: "Europe/Madrid" }); // YYYY-MM-DD
  const day = fmt.format(new Date());
  const since = new Date(Date.now() - 14 * 86400e3).toISOString();

  const { data, error } = await sb.from("players")
    .select("id,tg_id,updated_at,save,notified_on")
    .not("tg_id", "is", null).eq("notify", true)
    .gt("updated_at", since)
    .or(`notified_on.is.null,notified_on.lt.${day}`)
    .limit(3000);
  if (error) return new Response(error.message, { status: 500 });

  let sent = 0, skipped = 0, blocked = 0, failed = 0;
  for (const p of data || []) {
    const idle = Math.floor((Date.now() - new Date(p.updated_at).getTime()) / 86400e3);
    if (fmt.format(new Date(p.updated_at)) === day) { skipped++; continue; } // ya jugó hoy
    const en = (p.save && p.save.lang) === "en";
    const m = pickMsg(day, idle, en);
    if (!m) { skipped++; continue; }
    if (dry) { sent++; continue; }
    try {
      const r = await fetch(`https://api.telegram.org/bot${BOT}/sendMessage`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: p.tg_id, text: m.text, reply_markup: { inline_keyboard: [[{ text: en ? "▶ Play" : "▶ Jugar", url: GAME }]] } }),
      });
      if (r.ok) { sent++; await sb.from("players").update({ notified_on: day }).eq("id", p.id); }
      else if (r.status === 403 || r.status === 400) { blocked++; await sb.from("players").update({ notify: false }).eq("id", p.id); } // bloqueó el bot o nunca lo abrió
      else { failed++; if (r.status === 429) await sleep(1500); }
    } catch (_e) { failed++; }
    await sleep(60); // ~16 mensajes/s, por debajo del límite de Telegram
  }
  return new Response(JSON.stringify({ day, candidates: (data || []).length, sent, skipped, blocked, failed, dry }), { headers: { "Content-Type": "application/json" } });
});
