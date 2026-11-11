# daily-notify · avisos diarios del bot

Manda 1 mensaje al día por @dronerushhbot a quien tiene Telegram ligado, no ha jugado hoy y no los ha
desactivado (ajuste «Avisos» dentro del juego). Mensajes: casilla del Adviento (1–24 dic), fin de
temporada (29–30 nov y 5–6 ene), regalos en pista (25 dic–4 ene) y, el resto del año, un recordatorio
solo a quien lleva 3+ días sin jugar. Si alguien bloquea el bot, se le desactivan los avisos solo.

## Puesta en marcha (una vez)
1. Supabase > SQL Editor: pegar y ejecutar `supabase/12_avisos.sql`.
2. Desplegar (misma forma que `tg-auth`):
   `supabase functions deploy daily-notify --no-verify-jwt`
3. Secretos: `supabase secrets set CRON_SECRET=<una-clave-larga-inventada> GAME_URL=https://t.me/dronerushhbot/<tu-app>`
   (`TELEGRAM_BOT_TOKEN` ya lo tienes puesto por `tg-auth`).
4. Prueba sin enviar nada (devuelve cuántos recibirían aviso):
   `curl -X POST "https://tshsagnrcgvyixsouedv.supabase.co/functions/v1/daily-notify?dry=1" -H "x-cron-secret: <tu-clave>"`
5. Programarlo cada día (SQL Editor; Database > Extensions: activar `pg_cron` y `pg_net`):
```sql
select cron.schedule('daily-notify', '0 17 * * *', $$
  select net.http_post(
    url := 'https://tshsagnrcgvyixsouedv.supabase.co/functions/v1/daily-notify',
    headers := jsonb_build_object('x-cron-secret', '<tu-clave>', 'Content-Type', 'application/json'));
$$);
```
(17:00 UTC = 18:00/19:00 en España.) Para pararlo: `select cron.unschedule('daily-notify');`

## Ojo
Telegram solo deja escribir a quien ha abierto el bot alguna vez. Quien no, devuelve error y se
marca sin avisos: es normal que el primer día salgan «bloqueados».
