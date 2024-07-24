import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Replace with your actual bot token
TOKEN = '7417715664:AAGraoJ1mPDkRyHLUEf9EePHOpO1DWqspyg'

# In-memory storage
categories = {
    1: "General Knowledge",
    2: "Science",
    3: "History"
}

questions = {
    1: [
        ("What is the capital of France?", "Paris", "London", "Berlin", "Madrid"),
        ("Which planet is known as the Red Planet?", "Mars", "Venus", "Jupiter", "Saturn"),
        ("Who painted the Mona Lisa?", "Leonardo da Vinci", "Vincent van Gogh", "Pablo Picasso", "Michelangelo"),
        ("What is the largest ocean on Earth?", "Pacific Ocean", "Atlantic Ocean", "Indian Ocean", "Arctic Ocean"),
        ("Which country is home to the kangaroo?", "Australia", "New Zealand", "South Africa", "Brazil"),
        ("What is the chemical symbol for gold?", "Au", "Ag", "Fe", "Cu"),
        ("Who wrote 'Romeo and Juliet'?", "William Shakespeare", "Charles Dickens", "Jane Austen", "Mark Twain"),
        ("What is the capital of Japan?", "Tokyo", "Kyoto", "Osaka", "Seoul"),
        ("Which is the longest river in the world?", "Nile", "Amazon", "Mississippi", "Yangtze"),
        ("What is the hardest natural substance on Earth?", "Diamond", "Quartz", "Topaz", "Corundum"),
        ("Who is known as the father of modern physics?", "Albert Einstein", "Isaac Newton", "Niels Bohr", "Galileo Galilei"),
        ("What is the largest mammal in the world?", "Blue Whale", "African Elephant", "Colossal Squid", "Giraffe"),
        ("In which year did Christopher Columbus first reach the Americas?", "1492", "1776", "1066", "1215"),
        ("What is the main language spoken in Brazil?", "Portuguese", "Spanish", "English", "French"),
        ("Which element has the chemical symbol 'O'?", "Oxygen", "Gold", "Silver", "Iron"),
        ("Who was the first woman to fly solo across the Atlantic?", "Amelia Earhart", "Bessie Coleman", "Harriet Quimby", "Jacqueline Cochran"),
        ("What is the currency of the United Kingdom?", "Pound Sterling", "Euro", "Dollar", "Yen"),
        ("Which famous scientist developed the theory of evolution by natural selection?", "Charles Darwin", "Isaac Newton", "Albert Einstein", "Stephen Hawking"),
        ("What is the smallest country in the world?", "Vatican City", "Monaco", "San Marino", "Liechtenstein"),
        ("Who wrote '1984'?", "George Orwell", "Aldous Huxley", "Ray Bradbury", "H.G. Wells")
    ],
    2: [
        ("What is the chemical symbol for water?", "H2O", "CO2", "NaCl", "O2"),
        ("What is the largest organ in the human body?", "Skin", "Heart", "Liver", "Brain"),
        # Add more questions for this category
    ],
    3: [
        ("In which year did World War II end?", "1945", "1939", "1941", "1950"),
        ("Who was the first President of the United States?", "George Washington", "Thomas Jefferson", "Abraham Lincoln", "John Adams"),
        # Add more questions for this category
    ]
}

user_scores = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Welcome to the Quiz Bot! Use /categories to see available quiz categories.')

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f'category_{id}')]
        for id, name in categories.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose a category:', reply_markup=reply_markup)

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    category_id = int(query.data.split('_')[1])
    
    all_questions = questions[category_id]
    if len(all_questions) < 10:
        await query.edit_message_text("Not enough questions in this category. Please choose another.")
        return
    
    selected_questions = random.sample(all_questions, 10)
    context.user_data['questions'] = selected_questions
    context.user_data['current_question'] = 0
    context.user_data['score'] = 0
    
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    questions = context.user_data['questions']
    current = context.user_data['current_question']
    
    if current >= len(questions):
        await finish_quiz(update, context)
        return
    
    question, correct_answer, *wrong_answers = questions[current]
    answers = [correct_answer] + wrong_answers
    random.shuffle(answers)
    
    keyboard = [
        [InlineKeyboardButton(answers[0], callback_data=f'answer_{answers[0]}'),
         InlineKeyboardButton(answers[1], callback_data=f'answer_{answers[1]}')],
        [InlineKeyboardButton(answers[2], callback_data=f'answer_{answers[2]}'),
         InlineKeyboardButton(answers[3], callback_data=f'answer_{answers[3]}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    question_text = f"Question {current + 1}/10:\n\n{question}"
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text=question_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=question_text, reply_markup=reply_markup)

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user_answer = query.data.split('_', 1)[1]
    
    questions = context.user_data['questions']
    current = context.user_data['current_question']
    correct_answer = questions[current][1]
    
    if user_answer == correct_answer:
        context.user_data['score'] += 1
        await query.answer("Correct!")
    else:
        await query.answer(f"Wrong. The correct answer was: {correct_answer}")
    
    context.user_data['current_question'] += 1
    await send_question(update, context)

async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    score = context.user_data['score']
    user_id = update.callback_query.from_user.id
    
    if user_id not in user_scores:
        user_scores[user_id] = 0
    user_scores[user_id] += score
    
    await update.callback_query.edit_message_text(f"Quiz finished! Your score: {score}/10\nYour total score: {user_scores[user_id]}")

async def show_progress(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in user_scores:
        await update.message.reply_text(f"Your total score: {user_scores[user_id]}")
    else:
        await update.message.reply_text("You haven't completed any quizzes yet.")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("categories", show_categories))
    application.add_handler(CommandHandler("progress", show_progress))
    application.add_handler(CallbackQueryHandler(start_quiz, pattern='^category_'))
    application.add_handler(CallbackQueryHandler(check_answer, pattern='^answer_'))

    application.run_polling()

if __name__ == '__main__':
    main()