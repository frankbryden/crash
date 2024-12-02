export default function Progressbar({ percentage }) {
    return (
        <div className="mb-8">
            <div className="bg-light relative h-[10px] w-full rounded-2xl">
                <div
                    className={`bg-primary absolute top-0 left-0 h-full w-[${Math.round(percentage * 100)}%] rounded-2xl`}
                ></div>
            </div>
        </div>
    )
}