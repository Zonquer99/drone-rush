-- Drone Rush · Avisos diarios del bot de Telegram
-- Pegar entero en Supabase > SQL Editor > New query > Run
-- (la función `daily-notify` y el cron se explican en functions/daily-notify/LEEME.md)

alter table public.players add column if not exists notify boolean not null default true;
alter table public.players add column if not exists notified_on date;
grant update (notify) on public.players to authenticated;
create index if not exists players_notify on public.players (tg_id) where tg_id is not null and notify;
