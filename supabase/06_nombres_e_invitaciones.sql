-- Drone Rush · Fase 6: filtro de nombres ofensivos + invitaciones reales
-- Pegar entero en Supabase > SQL Editor > New query > Run

-- ===== 1) Filtro de nombres =====
create or replace function public.bad_name(n text) returns boolean
language plpgsql immutable set search_path = public as $$
declare norm text; flat text; tok text;
begin
  norm := translate(lower(coalesce(n,'')), 'áéíóúüñ013457@$', 'aeiouunoieastas');
  flat := regexp_replace(norm, '[^a-z]', '', 'g');
  -- palabras largas o inequívocas: se buscan dentro del nombre
  if flat ~ '(hijodeputa|hijaputa|gilipoll|maricon|mariquita|subnormal|retrasad|follar|folla|pollas|cabron|zorras|putit|putas|mierda|cojon|chupamela|chupapolla|pajer|nazi|hitler|fuck|shit|bitch|cunt|nigg|negrat|fagg|whore|pussy|penis|vagin|porn|rape|violad|pedof|pedoph|kkk|asshole|motherf|dickhead|bastard|jihad|terroris)' then
    return true;
  end if;
  -- palabras cortas: solo si son una palabra entera del nombre (separada por _ . o números)
  foreach tok in array regexp_split_to_array(norm, '[^a-z]+') loop
    if tok in ('puta','puto','putos','polla','coño','cono','culo','tonto','idiota','imbecil','mongolo','zorra','perra','guarra','marica','sexo','sex','dick','cock','fag','ass','tits','cum','nig','admin','moderador','soporte','support','dronerush') then
      return true;
    end if;
  end loop;
  return false;
end $$;

create or replace function public.check_name() returns trigger
language plpgsql set search_path = public as $$
begin
  if public.bad_name(new.name) then raise exception 'nombre_no_permitido' using errcode = 'P0001'; end if;
  return new;
end $$;
drop trigger if exists players_check_name on public.players;
create trigger players_check_name before insert or update of name on public.players
  for each row execute function public.check_name();

-- name_available ahora también rechaza nombres ofensivos
create or replace function public.name_available(n text) returns boolean
language sql stable security definer set search_path = public as $$
  select not public.bad_name(n) and not exists (select 1 from public.players where lower(name) = lower(n));
$$;

-- ===== 2) Invitaciones =====
alter table public.players add column if not exists ref_code text;
create unique index if not exists players_ref_code on public.players (ref_code) where ref_code is not null;

create table if not exists public.referrals (
  invitee uuid primary key references public.players(id) on delete cascade on update cascade,
  inviter uuid not null references public.players(id) on delete cascade on update cascade,
  claimed boolean not null default false,
  created_at timestamptz not null default now()
);
create index if not exists referrals_inviter on public.referrals (inviter, claimed);
alter table public.referrals enable row level security;
grant select, insert, update, delete on public.referrals to service_role;

-- Mi código de invitación (se crea la primera vez)
create or replace function public.my_ref() returns text
language plpgsql security definer set search_path = public as $$
declare c text;
begin
  select ref_code into c from public.players where id = auth.uid();
  if c is null and exists (select 1 from public.players where id = auth.uid()) then
    loop
      c := upper(substr(md5(random()::text || auth.uid()::text), 1, 7));
      begin
        update public.players set ref_code = c where id = auth.uid();
        exit;
      exception when unique_violation then null;
      end;
    end loop;
  end if;
  return c;
end $$;
revoke all on function public.my_ref() from public;
grant execute on function public.my_ref() to authenticated;

-- Un jugador NUEVO entra con el enlace de alguien: se apunta la invitación
-- (solo cuentas ligadas a Telegram, creadas hace menos de 3 días, y una sola vez)
create or replace function public.register_ref(code text) returns text
language plpgsql security definer set search_path = public as $$
declare me public.players; inv uuid;
begin
  select * into me from public.players where id = auth.uid();
  if me.id is null then return 'sin_jugador'; end if;
  if me.tg_id is null then return 'sin_telegram'; end if;
  if me.created_at < now() - interval '3 days' then return 'no_nuevo'; end if;
  if exists (select 1 from public.referrals where invitee = me.id) then return 'ya_invitado'; end if;
  select id into inv from public.players where ref_code = upper(code);
  if inv is null then return 'codigo_no_valido'; end if;
  if inv = me.id then return 'eres_tu'; end if;
  insert into public.referrals (invitee, inviter) values (me.id, inv);
  return 'ok';
end $$;
revoke all on function public.register_ref(text) from public;
grant execute on function public.register_ref(text) to authenticated;

-- El que invita recoge sus amigos nuevos (devuelve cuántos nuevos y el total)
create or replace function public.claim_refs() returns table(nuevos int, total int)
language plpgsql security definer set search_path = public as $$
declare n int;
begin
  with c as (update public.referrals set claimed = true where inviter = auth.uid() and not claimed returning 1)
  select count(*) into n from c;
  return query select n, (select count(*)::int from public.referrals where inviter = auth.uid());
end $$;
revoke all on function public.claim_refs() from public;
grant execute on function public.claim_refs() to authenticated;
