
const COLUMN_ORDERING = ["bid", "mult", "gain"];
/**
 * Cashout table
 * 
 * Displays player bid, cashout multiplier and gain. If any of the values are -1, they are not displayed.
 * A blank space is left instead.
 * @param {rows} Array List of objects of the shape {
 *      name: str,
 *      bid: int,
 *      mult: float,
 *      gain: float,
 * }
 * @returns React component to display the data
 */
export default function CashoutTable({ rows }) {
    const data = Object.keys(rows).map(name => [name, ...COLUMN_ORDERING.map(col => rows[name][col])]);
    return (
        <div>
            <h2>Cashout</h2>
            <table className="w-full bg-gray-800 rounded-lg shadow-md overflow-hidden">
                <thead>
                    <tr className="bg-gray-700 text-gray-200">
                        <th className="px-4 py-2">Player</th>
                        <th className="px-4 py-2">Bid</th>
                        <th className="px-4 py-2">Multiplier</th>
                        <th className="px-4 py-2">Gain</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map(([name, bid, mult, gain], index) => (
                        <tr
                            key={index}
                            className={`text-gray-300 ${index % 2 === 0 ? "bg-gray-700" : "bg-gray-800"
                                }`}
                        >
                            <td className="px-4 py-2">{name}</td>
                            <td className="px-4 py-2">{bid}</td>
                            <td className="px-4 py-2">{mult}</td>
                            <td className="px-4 py-2">{gain}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}