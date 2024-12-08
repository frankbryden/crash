/**
 * A generic way of representing a collection of string-number mappings, optionally sorted by value
 * @param {bids} param0 key/value pairs of title to number
 * @returns React component to display the data
 */
export default function NumbersTable({ title, keyColTitle, valColTitle, mapping, sorted = false }) {
    const data = sorted ?
        // Sort by number (second element in pair)
        Object.entries(mapping).sort((a, b) => b[1] - a[1]) :
        // No sorting, preserve ordering
        Object.entries(mapping);

    return (
        <div>
            <h2>{title}</h2>
            <table>
                <thead>
                    <tr>
                        <th>{keyColTitle}</th>
                        <th>{valColTitle}</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map(([key, value], index) =>
                        <tr key={index}>
                            <td>{key}</td>
                            <td>{value}</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    )
}