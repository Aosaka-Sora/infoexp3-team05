const quizScreen = document.querySelector('#quiz-screen');
const startQuizButton = document.querySelector('#start-quiz');
const englishWord = document.querySelector('#english-word');
const answerButtons = document.querySelector('#answer-buttons');
const quizStatus = document.querySelector('#quiz-status');

let currentEnglish = '';

async function startQuiz() {
    quizStatus.textContent = '';
    startQuizButton.disabled = true;

    try {
        const response = await fetch('/api/quiz');
        const quiz = await response.json();
        if (!response.ok) {
            throw new Error(quiz.error || '問題を取得できませんでした');
        }

        currentEnglish = quiz.english;
        englishWord.textContent = currentEnglish;
        answerButtons.replaceChildren(
            ...quiz.choices.map(choice => {
                const button = document.createElement('button');
                button.type = 'button';
                button.textContent = choice;
                button.addEventListener('click', () => answerQuiz(choice));
                return button;
            }),
        );
        quizScreen.hidden = false;
        startQuizButton.disabled = false;
    } catch (error) {
        quizStatus.textContent = error.message;
        startQuizButton.disabled = false;
    }
}

async function answerQuiz(japanese) {
    const buttons = answerButtons.querySelectorAll('button');
    buttons.forEach(button => {
        button.disabled = true;
    });

    try {
        const response = await fetch('/api/ans_quiz', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                english: currentEnglish,
                japanese,
            }),
        });
        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.error || '回答を送信できませんでした');
        }
        quizStatus.textContent = result.correct ? '正解です' : '不正解です';
    } catch (error) {
        quizStatus.textContent = error.message;
        buttons.forEach(button => {
            button.disabled = false;
        });
    }
}

startQuizButton.addEventListener('click', startQuiz);
