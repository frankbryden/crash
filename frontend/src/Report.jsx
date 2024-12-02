import { useState } from 'react';
import { DataFetcher } from './utils/dataFetcher';
import useToken from './auth/useToken';
import Login from './auth/Login';
import { useLoaderData, useParams } from "react-router-dom";
import { ReportBarChart, ReportPieChart } from './ReportCharts';
import QuizAnswersReport from './QuizAnswersReport';

export default function Report() {
    const { report, quiz } = useLoaderData();
    const { quizId } = useParams();

    const overallData = {
        correct: report.overall.correct,
        incorrect: report.overall.total - report.overall.correct,
    };

    return (
        <div className="min-h-screen bg-gradient-to-b from-blue-50 to-blue-200 p-6">
            <h1 className="text-3xl font-bold text-center text-blue-600 mb-6">Quiz Report</h1>
            <div className="max-w-4xl mx-auto bg-white shadow-lg rounded-lg p-6">
                <QuizAnswersReport quiz={quiz} />
            </div>
        </div>
    );
}

            // <div className="h-36">
            //     <ReportPieChart title={"Overall"} data={overallData} />
            // </div>
            // <div className="flex flex-row space-y-1 h-48 min-h-full">
            //     <ReportBarChart title={"Topic"} data={report.tags} />
            //     <ReportBarChart title={"Question type"} data={report.questionTypes} />
            // </div>