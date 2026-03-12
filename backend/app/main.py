import os
import tempfile
from fastapi import File, UploadFile
from app.ocr_service import extract_text_from_image
from app.schemas import OCRSolveResponse
import json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.schemas import (
    SolveQuestionRequest,
    SolveQuestionResponse,
    HistoryItem,
    MarkWrongRequest,
)
from app.llm_service import solve_math_question
from app.database import Base, engine, get_db
from app.models import QuestionHistory
from app.practice_service import (
    generate_practice_by_knowledge,
    regenerate_similar_question,
)
from app.schemas import (
    GeneratePracticeRequest,
    GeneratePracticeResponse,
    RegenerateQuestionResponse,
)

from app.report_service import build_learning_report
from app.schemas import LearningReportResponse

from app.suggestion_service import build_study_suggestion
from app.schemas import StudySuggestionResponse

from fastapi import Query
from app.models import QuestionHistory, Student
from app.student_service import ensure_default_student, list_students, create_student
from app.schemas import StudentItem, CreateStudentRequest

from fastapi.responses import HTMLResponse

Base.metadata.create_all(bind=engine)

from app.database import SessionLocal

with SessionLocal() as db:
    ensure_default_student(db)

app = FastAPI(title="AI Math Tutor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"message": "AI Math Tutor API is running"}


@app.post("/api/solve", response_model=SolveQuestionResponse)
def solve_question(
    req: SolveQuestionRequest,
    student_id: int = Query(1),
    db: Session = Depends(get_db)
):
    try:
        result = solve_math_question(req.question)

        row = QuestionHistory(
            question=req.question,
            answer=result["answer"],
            steps=json.dumps(result["steps"], ensure_ascii=False),
            knowledge_points=json.dumps(result["knowledge_points"], ensure_ascii=False),
            similar_question=result["similar_question"],
            is_wrong=False,
            student_id=student_id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)

        return SolveQuestionResponse(
            id=row.id,
            answer=row.answer,
            steps=json.loads(row.steps),
            knowledge_points=json.loads(row.knowledge_points),
            similar_question=row.similar_question,
            is_wrong=row.is_wrong,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history", response_model=list[HistoryItem])
def get_history(
    student_id: int = Query(1),
    db: Session = Depends(get_db)
):
    rows = (
        db.query(QuestionHistory)
        .filter(QuestionHistory.student_id == student_id)
        .order_by(QuestionHistory.id.desc())
        .all()
    )
    return [
        HistoryItem(
            id=row.id,
            question=row.question,
            answer=row.answer,
            steps=json.loads(row.steps),
            knowledge_points=json.loads(row.knowledge_points),
            similar_question=row.similar_question,
            is_wrong=row.is_wrong,
        )
        for row in rows
    ]


@app.patch("/api/history/{question_id}/wrong", response_model=HistoryItem)
def mark_wrong(question_id: int, body: MarkWrongRequest, db: Session = Depends(get_db)):
    row = db.query(QuestionHistory).filter(QuestionHistory.id == question_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="记录不存在")

    row.is_wrong = body.is_wrong
    db.commit()
    db.refresh(row)

    return HistoryItem(
        id=row.id,
        question=row.question,
        answer=row.answer,
        steps=json.loads(row.steps),
        knowledge_points=json.loads(row.knowledge_points),
        similar_question=row.similar_question,
        is_wrong=row.is_wrong,
    )


@app.get("/api/wrong-questions", response_model=list[HistoryItem])
def get_wrong_questions(
    student_id: int = Query(1),
    db: Session = Depends(get_db)
):
    rows = (
        db.query(QuestionHistory)
        .filter(
            QuestionHistory.student_id == student_id,
            QuestionHistory.is_wrong == True
        )
        .order_by(QuestionHistory.id.desc())
        .all()
    )

    return [
        HistoryItem(
            id=row.id,
            question=row.question,
            answer=row.answer,
            steps=json.loads(row.steps),
            knowledge_points=json.loads(row.knowledge_points),
            similar_question=row.similar_question,
            is_wrong=row.is_wrong,
        )
        for row in rows
    ]

@app.post("/api/solve-image", response_model=OCRSolveResponse)
async def solve_image(
    file: UploadFile = File(...),
    student_id: int = Query(1),
    db: Session = Depends(get_db)
):
    temp_path = None
    try:
        suffix = os.path.splitext(file.filename or "")[-1] or ".png"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        ocr_text = extract_text_from_image(temp_path).strip()
        if not ocr_text:
            raise HTTPException(status_code=400, detail="OCR 未识别到题目内容")

        result = solve_math_question(ocr_text)

        row = QuestionHistory(
            question=ocr_text,
            answer=result["answer"],
            steps=json.dumps(result["steps"], ensure_ascii=False),
            knowledge_points=json.dumps(result["knowledge_points"], ensure_ascii=False),
            similar_question=result["similar_question"],
            is_wrong=False,
            student_id=student_id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)

        return OCRSolveResponse(
            id=row.id,
            question=ocr_text,
            ocr_text=ocr_text,
            answer=row.answer,
            steps=json.loads(row.steps),
            knowledge_points=json.loads(row.knowledge_points),
            similar_question=row.similar_question,
            is_wrong=row.is_wrong,
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/api/generate-practice", response_model=GeneratePracticeResponse)
def generate_practice(req: GeneratePracticeRequest):
    try:
        result = generate_practice_by_knowledge(req.knowledge_point, req.count)
        return GeneratePracticeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/history/{question_id}/regenerate", response_model=RegenerateQuestionResponse)
def regenerate_question(question_id: int, db: Session = Depends(get_db)):
    row = db.query(QuestionHistory).filter(QuestionHistory.id == question_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="记录不存在")

    try:
        result = regenerate_similar_question(row.question)
        return RegenerateQuestionResponse(
            source_question_id=question_id,
            question=result["question"],
            answer=result["answer"],
            steps=result["steps"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/report", response_model=LearningReportResponse)
def get_learning_report(
    student_id: int = Query(1),
    db: Session = Depends(get_db)
):
    try:
        result = build_learning_report(db, student_id)
        return LearningReportResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/study-suggestion", response_model=StudySuggestionResponse)
def get_study_suggestion(
    student_id: int = Query(1),
    db: Session = Depends(get_db)
):
    try:
        result = build_study_suggestion(db, student_id)
        return StudySuggestionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/students", response_model=list[StudentItem])
def get_students(db: Session = Depends(get_db)):
    rows = list_students(db)
    return [StudentItem.model_validate(row) for row in rows]


@app.post("/api/students", response_model=StudentItem)
def add_student(req: CreateStudentRequest, db: Session = Depends(get_db)):
    row = create_student(db, req.name.strip())
    return StudentItem.model_validate(row)

@app.get("/api/export/report", response_class=HTMLResponse)
def export_report_html(
    student_id: int = Query(1),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    student_name = student.name if student else f"学生{student_id}"

    rows = (
        db.query(QuestionHistory)
        .filter(QuestionHistory.student_id == student_id)
        .order_by(QuestionHistory.id.desc())
        .all()
    )

    report = build_learning_report(db, student_id)
    suggestion = build_study_suggestion(db, student_id)

    wrong_rows = [row for row in rows if row.is_wrong][:10]

    wrong_html = ""
    for row in wrong_rows:
        try:
            knowledge_points = json.loads(row.knowledge_points or "[]")
        except Exception:
            knowledge_points = []

        try:
            steps = json.loads(row.steps or "[]")
        except Exception:
            steps = []

        wrong_html += f"""
        <div class="card">
          <h3>错题 #{row.id}</h3>
          <p><strong>题目：</strong>{row.question}</p>
          <p><strong>答案：</strong>{row.answer}</p>
          <p><strong>知识点：</strong>{'、'.join(knowledge_points) if knowledge_points else '无'}</p>
          <div>
            <strong>步骤解析：</strong>
            <ol>
              {''.join([f'<li>{step}</li>' for step in steps])}
            </ol>
          </div>
        </div>
        """

    top_kp_html = "".join([
        f"<li>{item['name']}（{item['count']}次）</li>"
        for item in report["top_knowledge_points"]
    ])

    weak_html = "".join([
        f"""
        <div class="card">
          <h3>{item['name']}</h3>
          <p>错误 {item['wrong_count']} 次 / 共出现 {item['total_count']} 次 / 错误率 {item['wrong_rate']}%</p>
          <p>{item['suggestion']}</p>
        </div>
        """
        for item in suggestion["weak_knowledge_points"]
    ])

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="UTF-8" />
      <title>{student_name} - 学习练习单</title>
      <style>
        body {{
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          margin: 0;
          padding: 24px;
          color: #222;
          background: #f7f8fa;
        }}
        .container {{
          max-width: 960px;
          margin: 0 auto;
          background: #fff;
          padding: 32px;
          border-radius: 16px;
        }}
        h1, h2, h3 {{
          margin-top: 0;
        }}
        .summary {{
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 12px;
          margin-bottom: 24px;
        }}
        .summary-item {{
          background: #f5f7fa;
          border-radius: 12px;
          padding: 16px;
          text-align: center;
        }}
        .summary-label {{
          color: #666;
          font-size: 14px;
          margin-bottom: 8px;
        }}
        .summary-value {{
          font-size: 28px;
          font-weight: bold;
          color: #18a058;
        }}
        .card {{
          background: #fafafa;
          border-radius: 12px;
          padding: 16px;
          margin-bottom: 16px;
        }}
        .section {{
          margin-top: 32px;
        }}
        .print-bar {{
          margin-bottom: 24px;
        }}
        .print-btn {{
          padding: 10px 16px;
          border: none;
          background: #18a058;
          color: #fff;
          border-radius: 8px;
          cursor: pointer;
        }}
        @media print {{
          body {{
            background: #fff;
            padding: 0;
          }}
          .container {{
            max-width: none;
            border-radius: 0;
            padding: 0;
          }}
          .print-bar {{
            display: none;
          }}
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="print-bar">
          <button class="print-btn" onclick="window.print()">打印 / 保存为 PDF</button>
        </div>

        <h1>{student_name} - 学习练习单</h1>

        <div class="summary">
          <div class="summary-item">
            <div class="summary-label">总题数</div>
            <div class="summary-value">{report['total_count']}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">错题数</div>
            <div class="summary-value">{report['wrong_count']}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">正确数</div>
            <div class="summary-value">{report['correct_count']}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">错题率</div>
            <div class="summary-value">{report['wrong_rate']}%</div>
          </div>
        </div>

        <div class="section">
          <h2>整体学习建议</h2>
          <div class="card">{suggestion['overall_suggestion']}</div>
        </div>

        <div class="section">
          <h2>高频知识点</h2>
          <div class="card">
            <ul>{top_kp_html or '<li>暂无</li>'}</ul>
          </div>
        </div>

        <div class="section">
          <h2>薄弱知识点分析</h2>
          {weak_html or '<div class="card">暂无薄弱知识点</div>'}
        </div>

        <div class="section">
          <h2>错题本（最近10题）</h2>
          {wrong_html or '<div class="card">暂无错题</div>'}
        </div>
      </div>
    </body>
    </html>
    """
    return html