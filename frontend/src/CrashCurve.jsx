import { useRef } from "react";

const BORDER_MARGIN = 2;
const TARGET_POINTS_X = 500;
const DEFAULT_MAX_MULT = 4;
const PADDING = 20;
const NUMBER_OF_TICKS = 6;

export default function CrashCurve({ points: mults, countdown }) {
    const canvasRef = useRef(null);
    const lastMult = mults[mults.length - 1];
    const currentYAxisMax = Math.max(lastMult, DEFAULT_MAX_MULT);

    function scalePoint(number, height) {
        return (number - mults[0]) * height / currentYAxisMax;
    }

    function getYTicks(ctx) {
        const highestTickVal = Math.floor(currentYAxisMax - (currentYAxisMax % 2));
        const tickStep = highestTickVal / NUMBER_OF_TICKS;
        const pointWithCurrentHighestTick = mults.slice(mults.length / 2).find((mult) => mult > highestTickVal);
        let ticks = [];
        for (let tick = 0; tick <= NUMBER_OF_TICKS * tickStep; tick += tickStep) {
            if (tick < 10) {
                ticks.push(Math.trunc(tick) + (Math.round(tick * 10) - Math.trunc(tick) * 10) / 10);
            } else {
                ticks.push(Math.round(tick));
            }
        }
        return ticks;
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
            ctx.font = "50px Brush Script MT";
            ctx.fillText(`x${lastMult}`, 25, 50);
        }

        const ticks = getYTicks(ctx);
        let tickIndex = 0;
        // Object to keep track of where the y-axis ticks need to go
        let ticksGeometry = new Map();

        if (countdown) {
            ctx.font = "50px Brush Script MT";
            let text;
            const remaining = Math.round(countdown.remainingTime);
            if (remaining % 10 == 0) {
                text = `${Math.round(countdown.remainingTime) / 10}.0s`;
            } else {
                text = `${Math.round(countdown.remainingTime) / 10}s`;
            }
            const textWidth = ctx.measureText(text).width;
            ctx.fillText(text, canvas.width / 2 - textWidth / 2, canvas.height / 2);
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

            // y-axis tick logic
            if (mults[index] > ticks[tickIndex]) {
                ticksGeometry.set(ticks[tickIndex], lastPoint);
                tickIndex++;
            }
        }
        ctx.stroke();

        // Render y-axis
        ticksGeometry.forEach((tickY, tickLabel) => {
            ctx.beginPath();
            ctx.moveTo(0, tickY);
            ctx.lineTo(10, tickY);
            ctx.stroke();
            ctx.font = "12px Brush Script MT";
            ctx.fillText(tickLabel, 11, tickY + 5);
        });

    }


    return (
        <canvas id="curve-canvas" ref={canvasRef} width="1080px" height="480px">
        </canvas>
    )
}