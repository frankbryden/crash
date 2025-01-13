import { useEffect, useState } from "react"

export default function Gift({ isActive, nextAvailableGift }) {
    const [remainingTime, setRemainingTime] = useState(humanDiff(nextAvailableGift, new Date()));


    // Stolen from https://stackoverflow.com/a/59793084/2538341
    function humanDiff(t1, t2) {
        const diff = Math.max(t1, t2) - Math.min(t1, t2);
        const SEC = 1000, MIN = 60 * SEC, HRS = 60 * MIN;

        const hrs = Math.floor(diff / HRS);
        const min = Math.floor((diff % HRS) / MIN).toLocaleString('en-US', { minimumIntegerDigits: 2 });
        const sec = Math.floor((diff % MIN) / SEC).toLocaleString('en-US', { minimumIntegerDigits: 2 });

        return `${min}:${sec}`;
    }

    useEffect(() => {
        const interval = setInterval(() => setRemainingTime(humanDiff(nextAvailableGift, new Date())), 1000);
        return () => clearInterval(interval);
    }, []);

    return (
        <>
            {isActive ?
                <a href="#" className="animate-bounce">
                    🎁
                </a>
                :
                <p>{remainingTime}</p>
            }
        </>
    )
}