-- Drone Rush · 09 · Reto del día (ranking diario) y Escuadrones
-- Pegar entero en Supabase > SQL Editor > New query > Run

-- ============ RETO DEL DÍA ============
create table if not exists public.daily_scores (
  day date not null,
  player_id uuid not null references public.players(id) on delete cascade on update cascade,
  best integer not null check (best between 0 and 1000000),
  updated_at timestamptz not null default now(),
  primary key (day, player_id)
);
create index if not exists daily_scores_day_best on public.daily_scores (day, best desc);
alter table public.daily_scores enable row level security;   -- sin políticas: solo a través de las funciones
grant select, insert, update, delete on public.daily_scores to service_role;

create or replace function public.submit_daily(day text, score int) returns void
language plpgsql security definer set search_path = public as $$
#variable_conflict use_column
declare d date; today date := (now() at time zone 'Europe/Madrid')::date;
begin
  if auth.uid() is null or score is null or score < 0 then return; end if;
  begin d := submit_daily.day::date; exception when others then return; end;
  if abs(d - today) > 1 then return; end if;
  if not exists (select 1 from public.players where id = auth.uid()) then return; end if;
  insert into public.daily_scores (day, player_id, best) values (d, auth.uid(), least(score, 1000000))
  on conflict (day, player_id) do update set best = greatest(public.daily_scores.best, excluded.best), updated_at = now()
  where excluded.best > public.daily_scores.best;
end $$;
revoke all on function public.submit_daily(text, int) from public;
grant execute on function public.submit_daily(text, int) to authenticated;

create or replace function public.daily_board(day text)
returns table(pos bigint, name text, frame text, best int, me boolean, cups int[])
language sql stable security definer set search_path = public as $$
  with r as (
    select row_number() over (order by s.best desc, s.updated_at asc) as pos, p.name, p.frame, s.best, (p.id = auth.uid()) as me, p.id
    from public.daily_scores s join public.players p on p.id = s.player_id
    where s.day = daily_board.day::date
  )
  select r.pos, r.name, r.frame, r.best, r.me, public.cups_of(r.id) from r where r.pos <= 50 or r.me order by r.pos;
$$;
revoke all on function public.daily_board(text) from public;
grant execute on function public.daily_board(text) to anon, authenticated;

-- ============ ESCUADRONES ============
create table if not exists public.squads (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  emoji text not null default '🚁',
  code text not null unique,
  owner uuid references public.players(id) on delete set null on update cascade,
  created_at timestamptz not null default now(),
  constraint squad_name_ok check (name ~ '^[A-Za-z0-9_ .ÁÉÍÓÚÜÑáéíóúüñ]{3,16}$'),
  constraint squad_emoji_ok check (char_length(emoji) <= 4)
);
create unique index if not exists squads_name_ci on public.squads (lower(name));
create table if not exists public.squad_members (
  player_id uuid primary key references public.players(id) on delete cascade on update cascade,
  squad_id uuid not null references public.squads(id) on delete cascade,
  joined_at timestamptz not null default now()
);
create index if not exists squad_members_sq on public.squad_members (squad_id);
create table if not exists public.squad_scores (
  week text not null,
  player_id uuid not null references public.players(id) on delete cascade on update cascade,
  squad_id uuid not null references public.squads(id) on delete cascade,
  meters bigint not null default 0,
  last_at timestamptz not null default now(),
  primary key (week, player_id)
);
create index if not exists squad_scores_wk on public.squad_scores (week, squad_id);
alter table public.squads enable row level security;
alter table public.squad_members enable row level security;
alter table public.squad_scores enable row level security;
grant select, insert, update, delete on public.squads, public.squad_members, public.squad_scores to service_role;

-- Crear escuadrón: devuelve el código para invitar
create or replace function public.squad_create(nm text, emo text) returns text
language plpgsql security definer set search_path = public as $$
declare cd text; sid uuid; i int;
begin
  if auth.uid() is null or not exists (select 1 from public.players where id = auth.uid()) then return 'sin_jugador'; end if;
  if exists (select 1 from public.squad_members where player_id = auth.uid()) then return 'ya_tienes'; end if;
  nm := btrim(coalesce(nm, ''));
  if nm !~ '^[A-Za-z0-9_ .ÁÉÍÓÚÜÑáéíóúüñ]{3,16}$' then return 'nombre_no_valido'; end if;
  if exists (select 1 from public.squads where lower(name) = lower(nm)) then return 'nombre_cogido'; end if;
  loop
    cd := '';
    for i in 1..6 loop cd := cd || substr('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', 1 + floor(random() * 32)::int, 1); end loop;
    exit when not exists (select 1 from public.squads where code = cd);
  end loop;
  insert into public.squads (name, emoji, code, owner) values (nm, left(coalesce(nullif(emo, ''), '🚁'), 4), cd, auth.uid()) returning id into sid;
  insert into public.squad_members (player_id, squad_id) values (auth.uid(), sid);
  return cd;
end $$;
revoke all on function public.squad_create(text, text) from public;
grant execute on function public.squad_create(text, text) to authenticated;

-- Unirse con código (máx. 20 miembros)
create or replace function public.squad_join(cd text) returns text
language plpgsql security definer set search_path = public as $$
declare sid uuid;
begin
  if auth.uid() is null or not exists (select 1 from public.players where id = auth.uid()) then return 'sin_jugador'; end if;
  if exists (select 1 from public.squad_members where player_id = auth.uid()) then return 'ya_tienes'; end if;
  select id into sid from public.squads where code = upper(btrim(coalesce(cd, '')));
  if sid is null then return 'no_existe'; end if;
  if (select count(*) from public.squad_members where squad_id = sid) >= 20 then return 'lleno'; end if;
  insert into public.squad_members (player_id, squad_id) values (auth.uid(), sid);
  return 'ok';
end $$;
revoke all on function public.squad_join(text) from public;
grant execute on function public.squad_join(text) to authenticated;

-- Salir (si era el último, el escuadrón desaparece; si era el jefe, pasa al más antiguo)
create or replace function public.squad_leave() returns text
language plpgsql security definer set search_path = public as $$
declare sid uuid;
begin
  select squad_id into sid from public.squad_members where player_id = auth.uid();
  if sid is null then return 'sin_escuadron'; end if;
  delete from public.squad_members where player_id = auth.uid();
  if not exists (select 1 from public.squad_members where squad_id = sid) then
    delete from public.squads where id = sid;
  elsif (select owner from public.squads where id = sid) is not distinct from auth.uid() then
    update public.squads set owner = (select player_id from public.squad_members where squad_id = sid order by joined_at limit 1) where id = sid;
  end if;
  return 'ok';
end $$;
revoke all on function public.squad_leave() from public;
grant execute on function public.squad_leave() to authenticated;

-- Sumar metros de una partida al escuadrón (semana actual)
create or replace function public.squad_add(m int) returns void
language plpgsql security definer set search_path = public as $$
declare sid uuid; wk text := public.tour_week();
begin
  if auth.uid() is null or m is null or m < 1 then return; end if;
  select squad_id into sid from public.squad_members where player_id = auth.uid();
  if sid is null then return; end if;
  insert into public.squad_scores (week, player_id, squad_id, meters) values (wk, auth.uid(), sid, least(m, 20000))
  on conflict (week, player_id) do update
    set meters = public.squad_scores.meters + least(m, 20000), squad_id = sid, last_at = now()
    where public.squad_scores.last_at < now() - interval '4 seconds';
end $$;
revoke all on function public.squad_add(int) from public;
grant execute on function public.squad_add(int) to authenticated;

-- Ranking de escuadrones de una semana
create or replace function public.squad_top(lim int default 20, wk text default null)
returns table(pos bigint, name text, emoji text, members bigint, points bigint, mine boolean)
language sql stable security definer set search_path = public as $$
  with pts as (
    select s.id, s.name, s.emoji, coalesce(sum(sc.meters), 0) as points
    from public.squads s left join public.squad_scores sc on sc.squad_id = s.id and sc.week = coalesce(wk, public.tour_week())
    group by s.id
  ), r as (
    select row_number() over (order by p.points desc, p.name) as pos, p.*,
      (select count(*) from public.squad_members m where m.squad_id = p.id) as members,
      exists (select 1 from public.squad_members m where m.squad_id = p.id and m.player_id = auth.uid()) as mine
    from pts p
  )
  select r.pos, r.name, r.emoji, r.members, r.points, r.mine from r where r.pos <= least(greatest(lim, 1), 50) or r.mine order by r.pos;
$$;
revoke all on function public.squad_top(int, text) from public;
grant execute on function public.squad_top(int, text) to anon, authenticated;

-- Mi escuadrón con sus miembros y metros de la semana
create or replace function public.squad_mine()
returns table(name text, emoji text, code text, is_owner boolean, points bigint, pos bigint, members jsonb)
language sql stable security definer set search_path = public as $$
  with me as (select squad_id from public.squad_members where player_id = auth.uid()),
  t as (select * from public.squad_top(1000) )
  select s.name, s.emoji, s.code, (s.owner = auth.uid()),
    coalesce((select t.points from t where t.name = s.name), 0),
    coalesce((select t.pos from t where t.name = s.name), 0),
    coalesce((select jsonb_agg(jsonb_build_object('name', p.name, 'frame', p.frame, 'meters', coalesce(sc.meters, 0), 'me', p.id = auth.uid()) order by coalesce(sc.meters, 0) desc)
      from public.squad_members m join public.players p on p.id = m.player_id
      left join public.squad_scores sc on sc.player_id = m.player_id and sc.week = public.tour_week()
      where m.squad_id = s.id), '[]'::jsonb)
  from public.squads s where s.id = (select squad_id from me);
$$;
revoke all on function public.squad_mine() from public;
grant execute on function public.squad_mine() to authenticated;

-- Puesto de mi escuadrón en una semana ya terminada (para el premio)
create or replace function public.squad_prize(wk text) returns int
language sql stable security definer set search_path = public as $$
  with mine as (select squad_id from public.squad_scores where week = wk and player_id = auth.uid()),
  r as (
    select squad_id, row_number() over (order by sum(meters) desc) as pos
    from public.squad_scores where week = wk group by squad_id
  )
  select coalesce((select pos::int from r where r.squad_id = (select squad_id from mine)), 0)
  where wk < public.tour_week();
$$;
revoke all on function public.squad_prize(text) from public;
grant execute on function public.squad_prize(text) to authenticated;
