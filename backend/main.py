from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

DATABASE_URL = "sqlite:///./mortgage.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    home_price: Mapped[float] = mapped_column(Float)
    down_payment: Mapped[float] = mapped_column(Float)
    annual_interest_rate: Mapped[float] = mapped_column(Float)
    term_years: Mapped[int] = mapped_column(Integer)
    monthly_income: Mapped[float] = mapped_column(Float)
    monthly_payment: Mapped[float] = mapped_column(Float)
    debt_to_income: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mortgage API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MortgageRequest(BaseModel):
    home_price: float = Field(gt=0)
    down_payment: float = Field(ge=0)
    annual_interest_rate: float = Field(gt=0, lt=100)
    term_years: int = Field(gt=0, le=40)
    monthly_income: float = Field(gt=0)


class MortgageResponse(MortgageRequest):
    monthly_payment: float
    debt_to_income: float


class QuoteOut(MortgageResponse):
    id: int
    created_at: datetime


def calculate_monthly_payment(principal: float, annual_rate_percent: float, term_years: int) -> float:
    monthly_rate = annual_rate_percent / 100 / 12
    total_payments = term_years * 12
    if monthly_rate == 0:
        return principal / total_payments
    return principal * (monthly_rate * (1 + monthly_rate) ** total_payments) / ((1 + monthly_rate) ** total_payments - 1)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/mortgage/quote", response_model=MortgageResponse)
def create_quote(payload: MortgageRequest) -> MortgageResponse:
    loan_amount = payload.home_price - payload.down_payment
    if loan_amount <= 0:
        raise HTTPException(status_code=400, detail="Down payment must be less than home price")

    monthly_payment = calculate_monthly_payment(loan_amount, payload.annual_interest_rate, payload.term_years)
    debt_to_income = (monthly_payment / payload.monthly_income) * 100

    with Session(engine) as session:
        quote = Quote(
            home_price=payload.home_price,
            down_payment=payload.down_payment,
            annual_interest_rate=payload.annual_interest_rate,
            term_years=payload.term_years,
            monthly_income=payload.monthly_income,
            monthly_payment=monthly_payment,
            debt_to_income=debt_to_income,
        )
        session.add(quote)
        session.commit()

    return MortgageResponse(**payload.model_dump(), monthly_payment=round(monthly_payment, 2), debt_to_income=round(debt_to_income, 2))


@app.get("/api/mortgage/quotes", response_model=List[QuoteOut])
def get_quotes() -> List[QuoteOut]:
    with Session(engine) as session:
        quotes = session.query(Quote).order_by(Quote.created_at.desc()).all()
        return [
            QuoteOut(
                id=q.id,
                home_price=q.home_price,
                down_payment=q.down_payment,
                annual_interest_rate=q.annual_interest_rate,
                term_years=q.term_years,
                monthly_income=q.monthly_income,
                monthly_payment=round(q.monthly_payment, 2),
                debt_to_income=round(q.debt_to_income, 2),
                created_at=q.created_at,
            )
            for q in quotes
        ]
