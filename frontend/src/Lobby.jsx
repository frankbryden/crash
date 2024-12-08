export default function Lobby({ players }) {
    return (
        <div>
            <h2>Lobby</h2>
            <ul>
                {players.map((player, index) => <li key={index}>{player}</li>)}
            </ul>
        </div>
    )
}