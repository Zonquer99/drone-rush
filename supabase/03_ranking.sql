-- Drone Rush · Fase 3: torneo semanal y ranking con jugadores reales
-- Pegar entero en Supabase > SQL Editor > New query > Run

-- Semana actual (lunes, hora de España), igual que en el juego
create or replace function public.tour_week() returns text
language sql stable set search_path = public as $$
  select to_char(date_trunc('week', now() at time zone 'Europe/Madrid'), 'YYYY-MM-DD');
$$;

-- Mejor distancia de cada jugador en cada semana
create table if not exists public.tour_scores (
  week text not null,
  player_id uuid not null references public.players(id) on delete cascade on update cascade,
  best integer not null check (best between 0 and 1000000),
  updated_at timestamptz not null default now(),
  primary key (week, player_id)
);
create index if not exists tour_scores_week_best on public.tour_scores (week, best desc);
alter table public.tour_scores enable row level security;   -- sin políticas: solo se usa a través de las funciones de abajo
grant select, insert, update, delete on public.tour_scores to service_role;

-- Guardar mi marca de esta semana (solo sube si mejora)
create or replace function public.submit_tour(score int) returns text
language plpgsql security definer set search_path = public as $$
declare wk text := public.tour_week();
begin
  if auth.uid() is null or score is null or score < 0 or score > 1000000 then return wk; end if;
  if not exists (select 1 from public.players where id = auth.uid()) then return wk; end if;
  insert into public.tour_scores (week, player_id, best) values (wk, auth.uid(), score)
  on conflict (week, player_id) do update set best = greatest(public.tour_scores.best, excluded.best), updated_at = now();
  return wk;
end $$;
revoke all on function public.submit_tour(int) from public;
grant execute on function public.submit_tour(int) to authenticated;

-- Tabla del torneo de una semana (top 100) + mi puesto
create or replace function public.tour_board(wk text default null)
returns table(pos bigint, name text, frame text, best int, me boolean)
language sql stable security definer set search_path = public as $$
  with r as (
    select row_number() over (order by s.best desc, s.updated_at asc) as pos, p.name, p.frame, s.best, (p.id = auth.uid()) as me
    from public.tour_scores s join public.players p on p.id = s.player_id
    where s.week = coalesce(wk, public.tour_week())
  )
  select * from r where pos <= 100 or me order by pos;
$$;
revoke all on function public.tour_board(text) from public;
grant execute on function public.tour_board(text) to anon, authenticated;

-- Cuántos jugadores hay (el torneo se abre solo al llegar a 500)
create or replace function public.player_count() returns bigint
language sql stable security definer set search_path = public as $$ select count(*) from public.players; $$;
revoke all on function public.player_count() from public;
grant execute on function public.player_count() to anon, authenticated;

-- Al mover la partida a otro móvil (tg-auth) el id cambia: que el torneo lo siga
-- (ya cubierto con "on update cascade")
