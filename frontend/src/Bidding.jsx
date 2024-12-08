import { useState } from "react";


export default function Bidding({ bidFunc }) {
    const [bidAmount, setBidAmount] = useState(0);

    return (
        <div>
            <p>Bid amount</p>
            <input type="number" onChange={(ev) => setBidAmount(ev.target.value)} />
            <button onClick={() => bidFunc(bidAmount)}>Submit bid</button>
        </div>
    )

}