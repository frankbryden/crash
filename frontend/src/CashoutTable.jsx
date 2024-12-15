
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
    console.log(data);
    return (
        <div>
            <h2>Cashout</h2>
            <table>
                <thead>
                    <tr>
                        <th>Player</th>
                        <th>Bid</th>
                        <th>Multiplier</th>
                        <th>Gain</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map(([name, bid, mult, gain], index) =>
                        <tr key={index}>
                            <td>{name}</td>
                            <td>{bid}</td>
                            <td>{mult}</td>
                            <td>{gain}</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    )
}