-- Drone Rush · Métricas (sesiones, retención, anuncios, jefes)
-- Pegar entero en Supabase > SQL Editor > New query > Run
-- Después, para ver los datos:  select * from m_diario;  select * from m_retencion;  select * from m_jefes;

create table if not exists public.events (
  id bigserial primary key,
  player_id uuid not null,
  plat text,
  name text not null,
  v int not null default 0,
  at timestamptz not null default now()
);
create index if not exists events_name_at on public.events (name, at);
create index if not exists events_player_at on public.events (player_id, at);
alter table public.events enable row level security;       -- sin políticas: solo entra por track_events
revoke all on public.events from anon, authenticated;
grant select, insert, update, delete on public.events to service_role;
grant usage, select on sequence public.events_id_seq to service_role;

create or replace function public.track_events(evs jsonb, plat text default 'web') returns void
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null or evs is null or jsonb_typeof(evs) <> 'array' then return; end if;
  -- freno: máximo 150 eventos por minuto y jugador
  if (select count(*) from public.events where player_id = auth.uid() and at > now() - interval '1 minute') > 150 then return; end if;
  insert into public.events (player_id, plat, name, v)
  select auth.uid(), left(coalesce(plat, 'web'), 8), e->>'n',
         case when (e->>'v') ~ '^-?[0-9]{1,9}$' then (e->>'v')::int else 0 end
  from (select e from jsonb_array_elements(evs) e limit 40) t(e)
  where e->>'n' in ('session', 'run', 'ad_offer', 'ad_ok', 'boss', 'adv');
end $$;
revoke all on function public.track_events(jsonb, text) from public;
grant execute on function public.track_events(jsonb, text) to authenticated;

-- Resumen por día (hora de Madrid)
create or replace view public.m_diario as
select (at at time zone 'Europe/Madrid')::date as dia,
  count(distinct player_id) filter (where name = 'session') as jugadores,
  count(*) filter (where name = 'session') as sesiones,
  count(*) filter (where name = 'run') as partidas,
  round(count(*) filter (where name = 'run')::numeric / nullif(count(*) filter (where name = 'session'), 0), 1) as partidas_por_sesion,
  count(*) filter (where name = 'ad_offer') as anuncios_ofrecidos,
  count(*) filter (where name = 'ad_ok') as anuncios_vistos,
  round(count(*) filter (where name = 'ad_ok')::numeric / nullif(count(distinct player_id) filter (where name = 'session'), 0), 2) as anuncios_por_jugador,
  round(avg(v) filter (where name = 'run')) as metros_medios
from public.events group by 1 order by 1 desc;

-- Retención: de los que llegaron el día X, qué % volvió al día 1, 3 y 7
create or replace view public.m_retencion as
with s as (select distinct player_id, (at at time zone 'Europe/Madrid')::date as d from public.events where name = 'session'),
f as (select player_id, min(d) as d0 from s group by 1)
select f.d0 as cohorte, count(*) as nuevos,
  round(100.0 * count(*) filter (where exists (select 1 from s where s.player_id = f.player_id and s.d = f.d0 + 1)) / count(*)) as d1_pct,
  round(100.0 * count(*) filter (where exists (select 1 from s where s.player_id = f.player_id and s.d = f.d0 + 3)) / count(*)) as d3_pct,
  round(100.0 * count(*) filter (where exists (select 1 from s where s.player_id = f.player_id and s.d = f.d0 + 7)) / count(*)) as d7_pct
from f group by 1 order by 1 desc;

-- Hasta qué jefe llega la gente (v = número de jefe, 0 = Centinela)
create or replace view public.m_jefes as
select v as jefe, count(*) as veces, count(distinct player_id) as jugadores
from public.events where name = 'boss' group by 1 order by 1;

-- Por plataforma
create or replace view public.m_plataformas as
select plat, count(distinct player_id) as jugadores, count(*) filter (where name = 'run') as partidas,
  count(*) filter (where name = 'ad_ok') as anuncios_vistos
from public.events group by 1 order by 2 desc;

revoke all on public.m_diario, public.m_retencion, public.m_jefes, public.m_plataformas from anon, authenticated;
