-- Drone Rush · Fase 4: Batallas PvP contra fantasmas de jugadores reales
-- Pegar entero en Supabase > SQL Editor > New query > Run

create table if not exists public.ghosts (
  id bigserial primary key,
  player_id uuid not null references public.players(id) on delete cascade on update cascade,
  seed text not null check (length(seed) between 4 and 40),
  dist integer not null check (dist between 0 and 1000000),
  skin text not null default 'clasico' check (length(skin) <= 24),
  path jsonb not null,
  created_at timestamptz not null default now()
);
create index if not exists ghosts_player on public.ghosts (player_id, created_at desc);
create index if not exists ghosts_recent on public.ghosts (created_at desc);
alter table public.ghosts enable row level security;   -- sin políticas: solo a través de las funciones
grant select, insert, update, delete on public.ghosts to service_role;

-- Guardar la grabación de una partida (se quedan las 8 últimas de cada jugador)
create or replace function public.submit_ghost(seed text, dist int, skin text, path jsonb) returns boolean
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null or not exists (select 1 from public.players where id = auth.uid()) then return false; end if;
  if dist < 200 or dist > 1000000 or jsonb_typeof(path) <> 'array' or jsonb_array_length(path) > 12000 then return false; end if;
  insert into public.ghosts (player_id, seed, dist, skin, path) values (auth.uid(), seed, dist, coalesce(skin, 'clasico'), path);
  delete from public.ghosts where player_id = auth.uid() and id not in
    (select id from public.ghosts where player_id = auth.uid() order by created_at desc limit 8);
  return true;
end $$;
revoke all on function public.submit_ghost(text, int, text, jsonb) from public;
grant execute on function public.submit_ghost(text, int, text, jsonb) to authenticated;

-- Buscar un rival: fantasma de OTRO jugador con trofeos parecidos (si no hay, cualquiera)
create or replace function public.find_ghost(tro int)
returns table(seed text, dist int, skin text, path jsonb, name text, frame text, trophies int, best int)
language sql stable security definer set search_path = public as $$
  select g.seed, g.dist, g.skin, g.path, p.name, p.frame, p.trophies, p.best
  from public.ghosts g join public.players p on p.id = g.player_id
  where g.player_id <> coalesce(auth.uid(), '00000000-0000-0000-0000-000000000000'::uuid)
    and g.created_at > now() - interval '30 days'
  order by (abs(p.trophies - coalesce(tro, 0)) <= 150) desc, random()
  limit 1;
$$;
revoke all on function public.find_ghost(int) from public;
grant execute on function public.find_ghost(int) to authenticated;
