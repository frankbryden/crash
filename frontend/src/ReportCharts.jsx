import { Bar, Pie } from 'react-chartjs-2';
import 'chart.js/auto'; // ADD THIS


export function ReportBarChart({title, data}) {
    console.log(`Chart ${title} rendering data`);
    console.log(data);
    const keys = Object.keys(data);
    const datasets = keys.map(key => {
        return {
            label: key,
            data: Object.values(data[key]),
        }
    });
    const labels = Object.keys(data[keys[0]]);

    return (
        <div>
            <Bar options={{ maintainAspectRatio: false }}
            data={{
                labels: labels,
                datasets: datasets
            }} />
            <p>{title}</p>
        </div>
    )
}

export function ReportPieChart({title, data}) {
    console.log(`Chart ${title} rendering data`);
    console.log(data);
    const labels = Object.keys(data);
    const datasets = [{
        data: Object.values(data),
    }];

    return (
        <div className=''>
            <div>
                <Pie options={{ maintainAspectRatio: false }}
                    data={{
                        labels: labels,
                        datasets: datasets
                    }} />
            </div>
            <p>{title}</p>
        </div>
    )
}