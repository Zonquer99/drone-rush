-- Drone Rush · Fase 5: copas del torneo (🏆 1.º · 🥈 2.º · 🥉 3.º)
-- Pegar entero en Supabase > SQL Editor > New query > Run

-- Podio de cada semana (lo rellena el servidor, nadie puede inventárselo)
create table if not exists public.tour_results (
  week text not null,
  rank int not null check (rank between 1 and 3),
  player_id uuid not null references public.players(id) on delete cascade on update cascade,
  primary key (week, rank)
);
alter table public.tour_results enable row level security;
grant select, insert, update, delete on public.tour_results to service_role;

-- Cierra una semana ya terminada y guarda su podio (solo si el torneo estaba abierto: 500+ jugadores)
create or replace function public.finalize_tour(wk text) returns void
language plpgsql security definer set search_path = public as $$
begin
  if wk is null or wk >= public.tour_week() then return; end if;
  if exists (select 1 from public.tour_results where week = wk) then return; end if;
  if (select count(*) from public.players) < 500 then return; end if;
  insert into public.tour_results (week, rank, player_id)
  select wk, r.rk, r.player_id from (
    select player_id, row_number() over (order by best desc, updated_at asc) as rk
    from public.tour_scores where week = wk
  ) r where r.rk <= 3
  on conflict do nothing;
end $$;
revoke all on function public.finalize_tour(text) from public;
grant execute on function public.finalize_tour(text) to authenticated;

-- Copas de un jugador: {oro, plata, bronce}
create or replace function public.cups_of(pid uuid) returns int[]
language sql stable security definer set search_path = public as $$
  select array[count(*) filter (where rank = 1), count(*) filter (where rank = 2), count(*) filter (where rank = 3)]::int[]
  from public.tour_results where player_id = pid;
$$;
revoke all on function public.cups_of(uuid) from public;

create or replace function public.my_cups() returns int[]
language sql stable security definer set search_path = public as $$ select public.cups_of(auth.uid()); $$;
revoke all on function public.my_cups() from public;
grant execute on function public.my_cups() to authenticated;

-- Las tablas públicas ahora devuelven también las copas
drop function if exists public.tour_board(text);
create or replace function public.tour_board(wk text default null)
returns table(pos bigint, name text, frame text, best int, me boolean, cups int[])
language sql stable security definer set search_path = public as $$
  with r as (
    select row_number() over (order by s.best desc, s.updated_at asc) as pos, p.name, p.frame, s.best, (p.id = auth.uid()) as me, p.id
    from public.tour_scores s join public.players p on p.id = s.player_id
    where s.week = coalesce(wk, public.tour_week())
  )
  select r.pos, r.name, r.frame, r.best, r.me, public.cups_of(r.id) from r where r.pos <= 100 or r.me order by r.pos;
$$;
revoke all on function public.tour_board(text) from public;
grant execute on function public.tour_board(text) to anon, authenticated;

drop function if exists public.top_players(text, int);
create or replace function public.top_players(kind text default 'best', lim int default 50)
returns table(name text, best int, trophies int, frame text, cups int[])
language sql stable security definer set search_path = public as $$
  select p.name, p.best, p.trophies, p.frame, public.cups_of(p.id) from public.players p
  order by case when kind = 'trophies' then p.trophies else p.best end desc, p.updated_at asc
  limit least(greatest(lim, 1), 100);
$$;
revoke all on function public.top_players(text, int) from public;
grant execute on function public.top_players(text, int) to anon, authenticated;

drop function if exists public.find_ghost(int);
create or replace function public.find_ghost(tro int)
returns table(seed text, dist int, skin text, path jsonb, name text, frame text, trophies int, best int, cups int[])
language sql stable security definer set search_path = public as $$
  select g.seed, g.dist, g.skin, g.path, p.name, p.frame, p.trophies, p.best, public.cups_of(p.id)
  from public.ghosts g join public.players p on p.id = g.player_id
  where g.player_id <> coalesce(auth.uid(), '00000000-0000-0000-0000-000000000000'::uuid)
    and g.created_at > now() - interval '30 days'
  order by (abs(p.trophies - coalesce(tro, 0)) <= 150) desc, random()
  limit 1;
$$;
revoke all on function public.find_ghost(int) from public;
grant execute on function public.find_ghost(int) to authenticated;
