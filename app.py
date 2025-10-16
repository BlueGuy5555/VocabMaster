from flask import Flask, redirect, render_template, request
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

app = Flask(__name__)


engine = create_engine("sqlite:///data.db")
Base = declarative_base()

class Topics(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    learned_words = Column(String, nullable=False)

class New_words(Base):
    __tablename__ = "new_words"
    id = Column(Integer, primary_key=True, autoincrement=True)
    words = Column(String, nullable=False)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()




@app.route("/", methods=["POST", "GET"])
def home():
    getting_back = session.query(New_words).all()
    new_words = [w.words for w in getting_back]


    if request.method == "POST":
        topic_input = request.form.get("topic", "").strip()

        if not topic_input:
            return "You didn't enter any word"

        words = topic_input.split()
        cleaned_words = []

        for word in words:
            word = word.strip().lower()
            if len(word) <= 1:
                continue
            elif word.isdigit():
                continue
            word = word.translate(str.maketrans("", "", "[]{}()\\/@#$%^&*(-_=+1234567890.?!',\""))
            cleaned_words.append(word)
        session.query(New_words).delete()
        session.commit()
        new_words = []
        for w in cleaned_words:
            existing = session.query(Topics).filter(Topics.learned_words == w).first()
            if not existing and not w in new_words:
                new_words.append(w)

        session.add_all([New_words(words=w) for w in new_words])
        session.commit()
        getting_back = session.query(New_words).all()
        new_words = [w.words for w in getting_back]
        return render_template("app.html", topic=new_words, index=len(new_words), words=len(words), new_words=len(new_words), learned_words=len(words)-len(new_words))
    
    return render_template("app.html", topic=new_words, index=len(new_words), words=0, new_words=0, learned_words=0)


@app.route("/add", methods=["POST"])
def add():
    value = request.form.get("add")
    if not value:
        return "No word provided", 400
    delete = session.query(New_words).filter(New_words.words == value).delete()
    session.commit()
    new_topic = Topics(learned_words=value)
    session.add(new_topic)
    session.commit()
    return redirect("/")


@app.route("/progress", methods=["POST", "GET"])
def progress():
    words = session.query(Topics).filter(Topics.id > 3980).all()
    return render_template("progress.html", words=words)
if __name__ == '__main__':
    app.run(debug=True)

