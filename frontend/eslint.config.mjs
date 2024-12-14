import { fixupConfigRules } from "@eslint/compat";
import globals from "globals";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";
import react from "eslint-plugin-react";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all,
});

export default [
    ...fixupConfigRules(compat.extends("")),
    {
        languageOptions: {
            globals: Object.fromEntries(
                Object.entries({
                    ...globals.browser,
                    ...globals.node,
                }).map(([key, value]) => [key.trim(), value])
            ),
        },
        plugins: {
            react: react,
        },
        rules: {
            "react/jsx-filename-extension": [1, { extensions: [".js", ".jsx"] }],
            "no-console": 0,
            "react/no-unused-state": 1,
        },
    },
];
