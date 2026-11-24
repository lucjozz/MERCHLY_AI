/** URL de una foto del inventario (privada: el BFF la sirve solo con sesión). Sin dependencias de servidor. */
export const urlFoto = (id: string) => `/api/backend/inventario/fotos/${id}`;
