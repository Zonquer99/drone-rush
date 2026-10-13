-- Drone Rush · 07 · Insignia 👑 por 100 amigos invitados
-- cups_of devuelve ahora 4 valores: [1º, 2º, 3º, corona(0/1)]
create or replace function public.cups_of(pid uuid) returns int[]
language sql stable security definer set search_path = public as $$
  select array[
    (select count(*) from public.tour_results where player_id = pid and rank = 1),
    (select count(*) from public.tour_results where player_id = pid and rank = 2),
    (select count(*) from public.tour_results where player_id = pid and rank = 3),
    case when (select count(*) from public.referrals where inviter = pid) >= 100 then 1 else 0 end
  ]::int[];
$$;
revoke all on function public.cups_of(uuid) from public;
