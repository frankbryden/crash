export default function Cashout({ bidAmount, hasCashedOut, cashOutObj, cashoutCallback }) {
    const playing = bidAmount > 0;

    return (
        <div className="flex flex-col items-center bg-gray-800 p-4 rounded-lg shadow-md space-y-4 space-x-4">
            <p className="text-lg font-semibold text-gray-200">Cashout</p>
            {hasCashedOut ?
                <p className="text-green-500 font-bold text-2xl animate-pulse text-center">Cashed out @ x{cashOutObj.mult} for a gain of {cashOutObj.gain}</p>
                :
                <>
                    {playing ?
                        <p className="text-lg font-semibold text-gray-200">Bid: {bidAmount}</p>
                        :
                        <p className="text-base font-semibold text-gray-200">Not playing</p>
                    }
                </>
            }
            <button
                onClick={() => cashoutCallback()}
                disabled={!playing}
                className={"inline-block px-6 py-3 text-gray-900 font-bold text-lg rounded-lg shadow-lg transition duration-300 " + (playing ? "bg-green-500 hover:bg-green-400 hover:shadow-xl active:bg-green-600" : "bg-gray-700")}
            >
                Cashout
            </button>
        </div>
    )
}