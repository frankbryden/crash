import { NAMES } from "./constants"

export function getRandomName() {
    return NAMES[Math.floor(Math.random() * NAMES.length)];
}