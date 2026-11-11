# Carpeta de desarrollo (no la usa el juego)

- `drone-rush.html`: el CÓDIGO FUENTE del juego. Se edita este archivo y NO el index.html de la raíz.
- `deploy.sh`: genera desde el fuente el index.html de la raíz (Telegram/web), crazygames/index.html y poki/index.html, y hace commit + push.
  Se usa así: `./deploy.sh "mensaje"`, con el fuente en /home/claude/drone-rush.html y el repo en /home/claude/drone-rush (rutas fijas dentro del script).
- `video/` y `vid/`: scripts para grabar el juego y montar los vídeos de TikTok y CrazyGames (Playwright + ffmpeg).

## Métricas, avisos y antitrampas (noviembre 2026)
Ejecutar en Supabase > SQL Editor, por este orden: `10_metricas.sql`, `11_antitrampas.sql`, `12_avisos.sql`.
- Métricas: `select * from m_diario;` (jugadores, partidas, anuncios por jugador), `m_retencion` (D1/D3/D7), `m_jefes`, `m_plataformas`.
- Antitrampas: techos por horas de vida de la cuenta; sospechosos: `select name,best,trophies,ac_flags from players where ac_flags>0;`
- Avisos del bot: ver `supabase/functions/daily-notify/LEEME.md`.
