export class DataFetcher {
    constructor(token) {
        this.url = import.meta.env.VITE_BACKEND;
        this.token = token;
        this.fetchQuestions = this.fetchQuestions.bind(this);
        this.fetchQuiz = this.fetchQuiz.bind(this);
    }

    async fetchData(method, endpoint, params, body) {
        let token = this.token ? this.token : localStorage.getItem("token");
        let resp;
        try {
            resp = await fetch(this.url + endpoint, {
                method: method,
                headers: new Headers({
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }),
                params: params,
                body: JSON.stringify(body)
            });
        } catch (error) {
            console.error(error);
            return {};
        }
        if (resp.status === 401) {
            throw new Response("Not authorized", { status: 401 });
        }
        if (!resp.ok) {
            throw new Error('Network response was not ok')
        }
        return resp.json();
    }

    fetchQuestions() {
        return this.fetchData("GET", "/questions");
    }

    fetchQuizzes() {
        return this.fetchData("GET", "/quizzes");
    }

    generateQuiz(quizName) {
        return this.fetchData("POST", "/generate_quiz", {}, {
            quizName: quizName,
        });
    }

    submitAnswer(quizId, questionId, answer) {
        console.log(`Submitting answer ${answer}`);
        return this.fetchData("POST", `/answer/${quizId}`, {}, {answer: answer, questionId: questionId});
    }

    /**
     * Submit a list of answers
     * @param {string} quizId
     * @param {object} answers Mapping from {questionId -> answer}
     * @returns Network response
     */
    submitAnswers(quizId, answers) {
        return this.fetchData("POST", `/answer/${quizId}`, {}, answers);
    }

    async fetchQuiz(quizId) {
        const quiz = await this.fetchData("GET", `/quiz/${quizId}`);
        return {
            quiz
        }
    }
    
    async fetchReport(quizId) {
        const report = await this.fetchData("GET", `/report/${quizId}`);
        return {
            report
        }
    }

    async fetchTagDefinitions() {
        const tagDefinitions = await this.fetchData("GET", `/tagDefinitions`);
        return {
            tagDefinitions
        };
    }
}