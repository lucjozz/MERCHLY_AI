export const COOKIE_TOKEN = "merchly_token";

export function guardarToken(token: string, expiraEnSegundos: number): void {
  document.cookie = `${COOKIE_TOKEN}=${token}; path=/; max-age=${expiraEnSegundos}; SameSite=Lax`;
}

export function borrarToken(): void {
  document.cookie = `${COOKIE_TOKEN}=; path=/; max-age=0; SameSite=Lax`;
}

export function obtenerTokenCliente(): string | null {
  const par = document.cookie
    .split("; ")
    .find((c) => c.startsWith(`${COOKIE_TOKEN}=`));
  return par ? par.slice(COOKIE_TOKEN.length + 1) : null;
}