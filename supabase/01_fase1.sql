-- Drone Rush · Fase 1: guardado en la nube, nombres únicos y ranking
-- Pegar entero en Supabase > SQL Editor > New query > Run

-- 1) Tabla de jugadores
create table if not exists public.players (
  id uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  name text not null,
  tg_id bigint,
  best integer not null default 0,
  trophies integer not null default 0,
  frame text not null default 'none',
  save jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint name_format check (name ~ '^[A-Za-z0-9_.ÁÉÍÓÚÜÑáéíóúüñ]{3,16}$'),
  constraint best_ok check (best between 0 and 10000000),
  constraint trophies_ok check (trophies between 0 and 1000000)
);

-- Nombres únicos (sin distinguir mayúsculas)
create unique index if not exists players_name_lower on public.players (lower(name));

-- updated_at automático
create or replace function public.touch_updated_at() returns trigger
language plpgsql as $$ begin new.updated_at = now(); return new; end $$;
drop trigger if exists players_touch on public.players;
create trigger players_touch before update on public.players
  for each row execute function public.touch_updated_at();

-- 2) Seguridad: cada jugador solo ve y cambia SU fila
alter table public.players enable row level security;
drop policy if exists "leer mi jugador" on public.players;
drop policy if exists "crear mi jugador" on public.players;
drop policy if exists "actualizar mi jugador" on public.players;
create policy "leer mi jugador" on public.players for select to authenticated using (id = auth.uid());
create policy "crear mi jugador" on public.players for insert to authenticated with check (id = auth.uid());
create policy "actualizar mi jugador" on public.players for update to authenticated using (id = auth.uid()) with check (id = auth.uid());
grant select, insert, update on public.players to authenticated;

-- 3) ¿Está libre este nombre?
create or replace function public.name_available(n text) returns boolean
language sql stable security definer set search_path = public as $$
  select not exists (select 1 from public.players where lower(name) = lower(n));
$$;
revoke all on function public.name_available(text) from public;
grant execute on function public.name_available(text) to anon, authenticated;

-- 4) Ranking público (solo nombre, récord, trofeos y marco)
create or replace function public.top_players(kind text default 'best', lim int default 50)
returns table(name text, best int, trophies int, frame text)
language sql stable security definer set search_path = public as $$
  select p.name, p.best, p.trophies, p.frame from public.players p
  order by case when kind = 'trophies' then p.trophies else p.best end desc, p.updated_at asc
  limit least(greatest(lim, 1), 100);
$$;
revoke all on function public.top_players(text, int) from public;
grant execute on function public.top_players(text, int) to anon, authenticated;
