import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    rules: {
      // Un efecto con "() => valor" devuelve ese valor y React lo usa como limpieza.
      // Pasó con scrollIntoView (en Chrome reciente devuelve una Promise) y rompía la pantalla.
      "no-restricted-syntax": [
        "error",
        {
          selector: "CallExpression[callee.name=/^use(Layout)?Effect$/] > ArrowFunctionExpression[expression=true]",
          message: "Usá llaves en el efecto: () => { ... }. Si devuelve un valor, React lo toma como función de limpieza.",
        },
      ],
    },
  },
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;
