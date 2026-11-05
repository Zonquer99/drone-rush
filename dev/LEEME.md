# Carpeta de desarrollo (no la usa el juego)

- `drone-rush.html`: el CÓDIGO FUENTE del juego. Se edita este archivo y NO el index.html de la raíz.
- `deploy.sh`: genera desde el fuente el index.html de la raíz (Telegram/web), crazygames/index.html y poki/index.html, y hace commit + push.
  Se usa así: `./deploy.sh "mensaje"`, con el fuente en /home/claude/drone-rush.html y el repo en /home/claude/drone-rush (rutas fijas dentro del script).
- `video/` y `vid/`: scripts para grabar el juego y montar los vídeos de TikTok y CrazyGames (Playwright + ffmpeg).
