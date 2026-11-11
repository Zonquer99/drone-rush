-- Drone Rush · Antitrampas (límites de plausibilidad en el servidor)
-- Pegar entero en Supabase > SQL Editor > New query > Run
--
-- Qué hace: el juego guarda en el móvil, así que el servidor no puede ver cada partida. Lo que sí
-- puede es poner TECHO a lo que es humanamente posible según el tiempo que lleva jugando la cuenta.
-- Si alguien edita su guardado a 99.999.999 monedas o 900.000 trofeos, el servidor recorta el
-- valor al techo (no da error, para no estropear el guardado de nadie) y lo apunta en `ac_flags`.
-- Los rankings (trofeos, récord, torneo semanal, reto diario, escuadrones) leen estas columnas.

alter table public.players add column if not exists ac_flags int not null default 0;
revoke update (ac_flags) on public.players from authenticated;

-- Techos según horas de vida de la cuenta (generosos a propósito: jamás deberían tocar a un jugador real)
create or replace function public.cap_best(created timestamptz) returns int language sql immutable as $$
  select least(10000000, (20000 + 800 * least(extract(epoch from (now() - created)) / 3600, 24 * 400))::int) $$;
create or replace function public.cap_trophies(created timestamptz) returns int language sql immutable as $$
  select least(1000000, (4000 + 600 * least(extract(epoch from (now() - created)) / 3600, 24 * 400))::int) $$;
create or replace function public.cap_coins(created timestamptz) returns bigint language sql immutable as $$
  select (200000 + 30000 * least(extract(epoch from (now() - created)) / 3600, 24 * 400))::bigint $$;

create or replace function public.players_guard() returns trigger
language plpgsql set search_path = public as $$
declare cb int; ct int; cc bigint; coins numeric; created timestamptz; flagged boolean := false;
begin
  -- el SQL Editor y las funciones de servidor (service_role) no se limitan
  if coalesce(auth.role(), '') <> 'authenticated' then return new; end if;
  created := case when tg_op = 'INSERT' then now() else old.created_at end;
  cb := public.cap_best(created); ct := public.cap_trophies(created); cc := public.cap_coins(created);
  if new.best > cb then new.best := cb; flagged := true; end if;
  if new.trophies > ct then new.trophies := ct; flagged := true; end if;
  if new.save ? 'coins' and (new.save->>'coins') ~ '^-?[0-9]+(\.[0-9]+)?$' then
    coins := (new.save->>'coins')::numeric;
    if coins > cc then new.save := jsonb_set(new.save, '{coins}', to_jsonb(cc)); flagged := true; end if;
    if coins < 0 then new.save := jsonb_set(new.save, '{coins}', to_jsonb(0)); end if;
  end if;
  if (new.save ? 'best') and (new.save->>'best') ~ '^[0-9]+$' and (new.save->>'best')::numeric > cb then
    new.save := jsonb_set(new.save, '{best}', to_jsonb(cb)); flagged := true; end if;
  if (new.save ? 'trophies') and (new.save->>'trophies') ~ '^[0-9]+$' and (new.save->>'trophies')::numeric > ct then
    new.save := jsonb_set(new.save, '{trophies}', to_jsonb(ct)); flagged := true; end if;
  if (new.save ? 'maxTrophies') and (new.save->>'maxTrophies') ~ '^[0-9]+$' and (new.save->>'maxTrophies')::numeric > ct then
    new.save := jsonb_set(new.save, '{maxTrophies}', to_jsonb(ct)); flagged := true; end if;
  if flagged then new.ac_flags := case when tg_op = 'UPDATE' then old.ac_flags else 0 end + 1; end if;
  return new;
end $$;
drop trigger if exists players_guard on public.players;
create trigger players_guard before insert or update on public.players
  for each row execute function public.players_guard();

-- Torneo semanal y reto diario: la puntuación no puede superar el techo de la cuenta
create or replace function public.submit_tour(score int) returns text
language plpgsql security definer set search_path = public as $$
declare wk text := public.tour_week(); cr timestamptz;
begin
  if auth.uid() is null or score is null or score < 0 or score > 1000000 then return wk; end if;
  select created_at into cr from public.players where id = auth.uid();
  if cr is null or score > public.cap_best(cr) then return wk; end if;
  insert into public.tour_scores (week, player_id, best) values (wk, auth.uid(), score)
  on conflict (week, player_id) do update set best = greatest(public.tour_scores.best, excluded.best), updated_at = now();
  return wk;
end $$;
revoke all on function public.submit_tour(int) from public;
grant execute on function public.submit_tour(int) to authenticated;

create or replace function public.submit_daily(day text, score int) returns void
language plpgsql security definer set search_path = public as $$
#variable_conflict use_column
declare d date; today date := (now() at time zone 'Europe/Madrid')::date; cr timestamptz;
begin
  if auth.uid() is null or score is null or score < 0 then return; end if;
  begin d := submit_daily.day::date; exception when others then return; end;
  if abs(d - today) > 1 then return; end if;
  select created_at into cr from public.players where id = auth.uid();
  if cr is null or score > public.cap_best(cr) then return; end if;
  insert into public.daily_scores (day, player_id, best) values (d, auth.uid(), least(score, 1000000))
  on conflict (day, player_id) do update set best = greatest(public.daily_scores.best, excluded.best), updated_at = now()
  where excluded.best > public.daily_scores.best;
end $$;
revoke all on function public.submit_daily(text, int) from public;
grant execute on function public.submit_daily(text, int) to authenticated;

-- Escuadrones: ningún salto de más de 8.000 m entre dos avisos (antes 20.000)
create or replace function public.squad_add(m int) returns void
language plpgsql security definer set search_path = public as $$
declare sid uuid; wk text := public.tour_week();
begin
  if auth.uid() is null or m is null or m < 1 then return; end if;
  select squad_id into sid from public.squad_members where player_id = auth.uid();
  if sid is null then return; end if;
  insert into public.squad_scores (week, player_id, squad_id, meters) values (wk, auth.uid(), sid, least(m, 8000))
  on conflict (week, player_id) do update
    set meters = public.squad_scores.meters + least(m, 8000), squad_id = sid, last_at = now()
    where public.squad_scores.last_at < now() - interval '4 seconds';
end $$;
revoke all on function public.squad_add(int) from public;
grant execute on function public.squad_add(int) to authenticated;

-- Para revisar sospechosos:  select name, best, trophies, ac_flags from players where ac_flags > 0 order by ac_flags desc;
