import { useEffect, useState } from "react"

export default function Gift({ nextAvailableGift, claimGift }) {
    const [remainingTime, setRemainingTime] = useState(humanDiff(nextAvailableGift, new Date()));


    // Stolen from https://stackoverflow.com/a/59793084/2538341
    function humanDiff(t1, t2) {
        const diff = Math.max(t1.getTime(), t2.getTime()) - Math.min(t1.getTime(), t2.getTime());
        const SEC = 1000, MIN = 60 * SEC, HRS = 60 * MIN;
        const min = Math.floor(diff / MIN);
        const sec = Math.floor(diff / SEC);
        console.log(`Sec is Math.floor(${diff} / ${SEC}) = ${sec}`);
        // const min = Math.floor((diff % HRS) / MIN).toLocaleString('en-US', { minimumIntegerDigits: 2 });
        // const sec = Math.floor((diff % MIN) / SEC).toLocaleString('en-US', { minimumIntegerDigits: 2 });
        // console.log(`Computing difference between ${t1.getHours()}:${t1.getMinutes()}:${t1.getSeconds()} and ${t2.getHours()}:${t2.getMinutes()}:${t2.getSeconds()}`);
        // console.log(`diff is ${diff/1000}s`);
        return `${min}:${sec}`;
    }

    const isActive = new Date() > nextAvailableGift;

    useEffect(() => {
        const interval = setInterval(() => setRemainingTime(humanDiff(nextAvailableGift, new Date())), 1000);
        return () => clearInterval(interval);
    }, []);

    return (
        <>
            {isActive ?
                <a href="#" className="animate-bounce" onClick={claimGift}>
                    🎁
                </a>
                :
                <p>{remainingTime}</p>
            }
        </>
    )
}