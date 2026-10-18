export class SesionInvalidaError extends Error {
  constructor(mensaje = "Sesión inválida o expirada.") {
    super(mensaje);
    this.name = "SesionInvalidaError";
  }
}