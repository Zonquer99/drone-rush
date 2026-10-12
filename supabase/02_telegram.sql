-- Drone Rush · Fase 2: partida ligada a la cuenta de Telegram
-- Pegar entero en Supabase > SQL Editor > New query > Run

-- Una cuenta de Telegram = un jugador
create unique index if not exists players_tg_id on public.players (tg_id) where tg_id is not null;

-- El juego NO puede escribir tg_id por su cuenta: solo lo pone el servidor tras verificar Telegram
revoke insert, update on public.players from authenticated;
grant insert (id, name, best, trophies, frame, save) on public.players to authenticated;
grant update (name, best, trophies, frame, save) on public.players to authenticated;
