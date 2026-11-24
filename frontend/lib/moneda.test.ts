/** Tests de los cálculos de dinero (npm test). Sin dependencias: node --test. */
import { test } from "node:test";
import assert from "node:assert/strict";
import { calcularCostoBolivia, calcularMargen, formatearMonto } from "./moneda.ts";

const cerca = (a: number, b: number) => assert.ok(Math.abs(a - b) < 0.005, `${a} != ${b}`);

test("costo puesto en Bolivia: FOB 10, flete 2, GA 10 %", () => {
  const r = calcularCostoBolivia({ fobUsd: 10, fleteUsd: 2, gravamenPct: 10, gastosLocalesUsd: 1, comisionCobroPct: 0, precioVentaUsd: 30 });
  assert.ok(r);
  cerca(r.seguroUsd, 0.2); // 2 % del FOB
  cerca(r.cifUsd, 12.2);
  cerca(r.gravamenUsd, 1.22);
  cerca(r.ivaUsd, 13.42 * 0.1494); // (CIF + GA) × 14,94 %
  cerca(r.costoPuestoUsd, 12.2 + 1.22 + 13.42 * 0.1494 + 1);
  cerca(r.gananciaUsd, 30 - r.costoPuestoUsd);
});

test("la comisión de cobro se descuenta del precio de venta", () => {
  const sin = calcularCostoBolivia({ fobUsd: 10, fleteUsd: 0, gravamenPct: 0, gastosLocalesUsd: 0, comisionCobroPct: 0, precioVentaUsd: 20 })!;
  const con = calcularCostoBolivia({ fobUsd: 10, fleteUsd: 0, gravamenPct: 0, gastosLocalesUsd: 0, comisionCobroPct: 5, precioVentaUsd: 20 })!;
  cerca(sin.gananciaUsd - con.gananciaUsd, 1);
  cerca(con.comisionUsd, 1);
});

test("datos inválidos devuelven null (nunca un número inventado)", () => {
  const base = { fobUsd: 10, fleteUsd: 2, gravamenPct: 10, gastosLocalesUsd: 0, comisionCobroPct: 0, precioVentaUsd: 30 };
  assert.equal(calcularCostoBolivia({ ...base, precioVentaUsd: 0 }), null);
  assert.equal(calcularCostoBolivia({ ...base, fobUsd: -1 }), null);
  assert.equal(calcularCostoBolivia({ ...base, gravamenPct: Number.NaN }), null);
  assert.equal(calcularCostoBolivia({ ...base, gravamenPct: 150 }), null);
});

test("margen simple y formato de montos", () => {
  const m = calcularMargen(10, 2, 0, 24)!;
  cerca(m.margenPct, 50);
  assert.equal(formatearMonto(null), "Sin dato");
  assert.match(formatearMonto(10, { moneda: "BOB", tipo_cambio: 11.75 }), /117,50/);
});
