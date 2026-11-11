// Lógica pura de los avisos (sin Deno ni red) para poder probarla.
export type Msg = { text: string; all: boolean } | null;

// day = 'YYYY-MM-DD' en hora de Madrid · idle = días sin jugar · en = idioma inglés
export function pickMsg(day: string, idle: number, en: boolean): Msg {
  const [y, m, d] = day.split("-").map(Number);
  const T = (es: string, ing: string) => (en ? ing : es);
  if (m === 12 && d >= 1 && d <= 23)
    return { all: true, text: T(`🎄 Casilla ${d} del Adviento esperándote en Drone Rush. ¡Entra a abrirla!`, `🎄 Advent door ${d} is waiting for you in Drone Rush. Come open it!`) };
  if (m === 12 && d === 24)
    return { all: true, text: T("🎁 ¡Hoy se abre el GRAN PREMIO del Adviento en Drone Rush!", "🎁 Today the Advent GRAND PRIZE opens in Drone Rush!") };
  if ((m === 11 && d >= 29 && y === 2026) || (m === 1 && d >= 5 && y === 2027))
    return { all: true, text: T("⏳ Últimas horas de la temporada: sube de liga y recoge tu cofre antes de que se reinicien los trofeos.", "⏳ Last hours of the season: climb a league and grab your chest before trophies reset.") };
  if ((m === 12 && d >= 25) || (m === 1 && d <= 4))
    return { all: true, text: T("🎁 Regalos en pista y el Krampus de Hielo te esperan en Drone Rush hasta el 6 de enero.", "🎁 Gifts on the track and the Ice Krampus are waiting in Drone Rush until January 6.") };
  if (idle >= 3)
    return { all: false, text: T("🚁 Tu reto diario y tus misiones te esperan en Drone Rush. ¿Echamos una partida?", "🚁 Your daily challenge and missions are waiting in Drone Rush. One quick run?") };
  return null;
}
