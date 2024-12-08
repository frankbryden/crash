import { CssSyntaxError } from "postcss";
import { useEffect, useRef } from "react";

const BORDER_MARGIN = 2;
const TARGET_POINTS_X = 500;
const DEFAULT_MAX_MULT = 6;
const PADDING = 20;

export default function CrashCurve({ points: mults }) {
    const canvasRef = useRef(null);
    const animationIdRef = useRef(null);
    const lastMult = mults[mults.length - 1];
    const yDelta = lastMult - mults[0];

    function scalePoint(number, height) {
        return (number - mults[0]) * height / Math.max(lastMult, DEFAULT_MAX_MULT);
    }

    const canvas = canvasRef.current;
    if (canvas != null) {
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Border
        ctx.beginPath();
        ctx.rect(BORDER_MARGIN, BORDER_MARGIN, canvas.width - 2 * BORDER_MARGIN, canvas.height - 2 * BORDER_MARGIN);
        ctx.stroke();

        if (lastMult > 0) {
            ctx.font = "50px serif";
            ctx.fillText(`x${lastMult}`, 20, 50);
        }

        ctx.beginPath();
        // Go to (0, 0) with a flipped y-axis
        let lastPoint = canvas.height - scalePoint(mults[0], canvas.height - PADDING);
        ctx.moveTo(0, lastPoint);

        for (let index = 1; index < mults.length; index++) {
            lastPoint = canvas.height - scalePoint(mults[index], canvas.height - PADDING);
            let x;
            if (mults.length > TARGET_POINTS_X) {
                x = 1 / mults.length;
            } else {
                x = 1 / TARGET_POINTS_X;
            }
            ctx.lineTo(x * index * (canvas.width - PADDING), lastPoint);
        }
        ctx.stroke();
    }


    return (
        <canvas id="curve-canvas" ref={canvasRef} width="1080px" height="480px">
        </canvas>
    )
}