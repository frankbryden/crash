/**
 * A component to display player cash values in a darker theme styled table
 * @param {Object} props
 * @param {string} props.title Title of the table
 * @param {Object} props.mapping Player names as keys, cash values as numbers
 * @param {boolean} props.sorted Whether to sort the data by cash values
 * @returns React component
 */
export default function CashValuesTable({ title, mapping, sorted = false }) {
    const data = sorted
        ? Object.entries(mapping).sort(([, valA], [, valB]) => valB - valA)
        : Object.entries(mapping);

    return (
        <div className="p-4 border border-gray-700 rounded-lg bg-gray-800 shadow-md">
            <h2 className="text-lg font-semibold mb-4 text-center text-gray-200">{title}</h2>
            <table className="table-auto w-full border-collapse border border-gray-700">
                <thead>
                    <tr className="bg-gray-700 text-gray-200">
                        <th className="px-4 py-2 border border-gray-600">Player</th>
                        <th className="px-4 py-2 border border-gray-600">Cash</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map(([key, value], index) => (
                        <tr
                            key={index}
                            className={`${index % 2 === 0 ? "bg-gray-700" : "bg-gray-800"
                                } hover:bg-gray-600`}
                        >
                            <td className="px-4 py-2 border border-gray-600 text-gray-300">
                                {key}
                            </td>
                            <td className="px-4 py-2 border border-gray-600 text-gray-300">
                                {value}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
