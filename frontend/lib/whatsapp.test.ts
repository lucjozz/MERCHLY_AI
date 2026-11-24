import { test } from "node:test";
import assert from "node:assert/strict";
import { armarMensajeCatalogo, enlaceWhatsApp } from "./whatsapp.ts";

test("arma el catálogo con título en negrita, precios y nota", () => {
  const m = armarMensajeCatalogo({
    encabezado: "Catálogo de Tienda Ana",
    nota: "Envíos a todo el país",
    simbolo: "Bs",
    items: [{ nombre: "Botella térmica", precio: "120" }, { nombre: "Mochila", precio: "" }],
  });
  assert.equal(m, "*Catálogo de Tienda Ana*\n\n• Botella térmica — *Bs 120*\n• Mochila — consultá el precio\n\nEnvíos a todo el país");
});

test("los asteriscos de los datos no rompen el formato", () => {
  const m = armarMensajeCatalogo({ encabezado: "*Oferta*", nota: "", simbolo: "Bs", items: [{ nombre: "Gorra *nueva*", precio: "50" }] });
  assert.equal(m, "*Oferta*\n\n• Gorra nueva — *Bs 50*");
});

test("el enlace de WhatsApp codifica el texto completo", () => {
  const url = enlaceWhatsApp("Hola & chau\n*Bs 10*");
  assert.ok(url.startsWith("https://wa.me/?text="));
  assert.equal(decodeURIComponent(url.split("text=")[1]), "Hola & chau\n*Bs 10*");
});
