export default function Lobby({ players }) {
    return (
        <div className="p-4 bg-gray-800 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-2 text-blue-400">Lobby</h2>
            <ul className="list-disc pl-6 space-y-1">
                {players.map((player, index) => (
                    <li key={index} className="text-gray-200">{player}</li>
                ))}
            </ul>
        </div>
    )
}