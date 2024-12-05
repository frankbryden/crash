export default function Lobby({ players }) {
    return (
        <div>
            <ul>
                {players.map((player, index) => <li key={index}>{player}</li>)}
            </ul>
        </div>
    )
}