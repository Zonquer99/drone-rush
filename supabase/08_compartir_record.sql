-- Drone Rush · 08 · Compartir la carta de récord
-- Registro de publicaciones (para limitar el spam). Solo lo usa la función share-record.
create table if not exists public.record_shares (
  id bigserial primary key,
  tg_id bigint not null,
  kind text not null check (kind in ('group','friend')),
  meters integer not null default 0,
  created_at timestamptz not null default now()
);
create index if not exists record_shares_tg_idx on public.record_shares (tg_id, kind, created_at desc);
alter table public.record_shares enable row level security;  -- sin políticas: nadie desde el juego, solo la función

-- Carpeta pública para las cartas de "Retar a un amigo" (Telegram necesita poder descargarlas)
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('cards', 'cards', true, 2000000, array['image/jpeg','image/png'])
on conflict (id) do update set public = true, file_size_limit = 2000000, allowed_mime_types = array['image/jpeg','image/png'];
