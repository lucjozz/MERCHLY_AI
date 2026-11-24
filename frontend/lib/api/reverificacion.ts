/**
 * Re-verificación global (docs/013-Seguridad/09): cuando el backend responde
 * "Confirmá que sos vos", cualquier pantalla abre la misma ventana (montada en
 * el layout), y si la persona confirma, el pedido se reintenta solo.
 */
export const REAUTENTICACION_REQUERIDA = "Confirmá que sos vos para continuar.";
export const EVENTO_REVERIFICAR = "merchly:reverificar";

export interface PedidoReverificacion {
  resolver: (ok: boolean) => void;
}

let enCurso: Promise<boolean> | null = null;

/** Abre la ventana y espera la respuesta. Si ya hay una abierta, comparte la misma. */
export function pedirReverificacion(): Promise<boolean> {
  if (typeof window === "undefined") return Promise.resolve(false);
  if (!enCurso) {
    enCurso = new Promise<boolean>((resolver) => {
      window.dispatchEvent(new CustomEvent<PedidoReverificacion>(EVENTO_REVERIFICAR, { detail: { resolver } }));
    }).finally(() => {
      enCurso = null;
    });
  }
  return enCurso;
}
