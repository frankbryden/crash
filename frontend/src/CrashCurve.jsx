import { CssSyntaxError } from "postcss";
import { useEffect, useRef } from "react";

const BORDER_MARGIN = 2;

export default function CrashCurve() {
    const canvasRef = useRef(null);
    const animationIdRef = useRef(null);

    // let [playerPos, setPlayerPos] = useState({ x: 10, y: 10 });
    let playerPos = { x: 10, y: 10 };
    let timeFrame = 0;
    let start;

    function f(x) {
        return (1.2 ** x) / (1.19 ** x);
    }

    function update(timestamp) {
        if (start === undefined) {
            start = timestamp;
        }
        animationIdRef.current = requestAnimationFrame(update);
        playerPos.x += 1;
        playerPos.y += 0.5;
        // console.log(playerPos);

        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Border
        ctx.beginPath();
        ctx.rect(BORDER_MARGIN, BORDER_MARGIN, canvas.width - 2 * BORDER_MARGIN, canvas.height - 2 * BORDER_MARGIN);
        ctx.stroke();

        ctx.beginPath();
        let lastPoint = canvas.height - f(0);
        ctx.moveTo(0, lastPoint);
        for (let x = 1; x < (timestamp - start) / 10; x++) {
            lastPoint = canvas.height - f(x);
            ctx.lineTo(x, lastPoint);
        }
        // ctx.arc(playerPos.x, playerPos.y, 10, 0, 2 * Math.PI, false);
        ctx.stroke();
    }

    useEffect(() => {
        const canvas = canvasRef.current;
        // const parent = canvas.parentNode;
        // const width = parent.clientWidth;
        // const height = parent.clientHeight;

        // // Set canvas dimensions to match CSS size
        // canvas.width = width;
        // canvas.height = height;

        animationIdRef.current = requestAnimationFrame(update);
        console.log("Animation frame requested");
        return () => {
            console.log("Cancel animation");
            cancelAnimationFrame(animationIdRef.current);
        }
    }, []);


    return (
        <canvas id="curve-canvas" ref={canvasRef} width="1080px" height="480px">
        </canvas>
    )
}