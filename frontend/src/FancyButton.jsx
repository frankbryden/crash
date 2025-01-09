export default function FancyButton({ name, onClick }) {
    return (
        <a
            href="#_"
            onClick={onClick}
            className="inline-block px-6 py-3 bg-green-500 text-gray-900 font-bold text-lg rounded-lg shadow-lg hover:bg-green-400 hover:shadow-xl active:bg-green-600 transition duration-300"
        >
            {name}
        </a>
    )
}