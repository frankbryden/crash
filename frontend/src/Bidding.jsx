import { useState } from "react";


export default function Bidding({ bidFunc, bid }) {
    const [bidAmount, setBidAmount] = useState(0);

    function onBidSubmit() {
        if (bidAmount > 0) {
            bidFunc(bidAmount);
        }
    }

    return (
        <div className="flex flex-col items-center bg-gray-800 p-4 rounded-lg shadow-md space-y-4">
            <p className="text-lg font-semibold text-gray-200">Bid Amount</p>
            {bid != null ?
                <p className="text-lg font-semibold text-gray-200">{bid}</p>
                :
                <>
                    <input
                        type="number"
                        className="w-1/2 px-4 py-2 rounded-lg text-gray-700 border border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
                        onChange={(ev) => setBidAmount(ev.target.value)}
                    />
                    <button
                        onClick={() => onBidSubmit()}
                        className="px-6 py-2 bg-blue-500 text-gray-100 font-bold rounded-lg shadow-md hover:bg-blue-400 hover:shadow-lg transition duration-300"
                    >
                        Submit Bid
                    </button>
                </>
            }
        </div>
    )
}