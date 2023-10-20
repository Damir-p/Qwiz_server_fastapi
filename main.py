from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from databases import Database
import requests


app = FastAPI()
Base = declarative_base()

DATABASE_URL = "postgresql://postgres:postgres@db/serverdb"
database = Database(DATABASE_URL)
metadata = Base.metadata
Base = declarative_base()

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, index=True)
    answer_text = Column(String)
    creation_date = Column(DateTime, server_default=text("now()"))

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine) 

class QuestionRequest(BaseModel):
    questions_num: int

@app.post("/")
async def get_questions(question_request: QuestionRequest):
    async with database.transaction():
        questions = []
        for _ in range(question_request.questions_num):
            while True:
                response = requests.get("https://jservice.io/api/random?count=1")
                data = response.json()[0]
                question_text = data["question"]
                answer_text = data["answer"]

                existing_question = database.execute(Question.__table__.select().where(Question.question_text == question_text)).fetchone()

                if not existing_question:
                    break

            query = Question.__table__.insert().values(question_text=question_text, answer_text=answer_text)
            await database.execute(query)
            questions.append({
                "question_text": question_text,
                "answer_text": answer_text,
            })
        return questions
