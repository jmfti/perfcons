from fastapi import FastAPI, Header, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import os
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@db:3306/perfcons")
API_TOKEN = os.getenv("API_TOKEN", "CHANGE-THIS-TOKEN-IN-PRODUCTION")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model
class Fact(Base):
    __tablename__ = "facts"
    
    conversation_id = Column(String(255), primary_key=True, index=True)
    fact = Column(Text(16000), nullable=False)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class FactCreate(BaseModel):
    fact: str

class FactUpdate(BaseModel):
    fact: str

class FactResponse(BaseModel):
    conversation_id: str
    fact: str
    
    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI(
    title="Perfcons API",
    description="REST API for managing facts associated with conversation IDs",
    version="1.0.0"
)

security = HTTPBearer()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication middleware
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# CRUD endpoints
@app.post("/facts", response_model=FactResponse, status_code=status.HTTP_201_CREATED)
async def create_fact(
    fact_data: FactCreate,
    conversation_id: str = Header(..., alias="X-Conversation-ID"),
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create a new fact for a conversation ID"""
    # Check if fact already exists
    existing_fact = db.query(Fact).filter(Fact.conversation_id == conversation_id).first()
    if existing_fact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Fact already exists for this conversation ID"
        )
    
    db_fact = Fact(conversation_id=conversation_id, fact=fact_data.fact)
    db.add(db_fact)
    db.commit()
    db.refresh(db_fact)
    return db_fact

@app.get("/facts", response_model=FactResponse)
async def read_fact(
    conversation_id: str = Header(..., alias="X-Conversation-ID"),
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Retrieve a fact by conversation ID"""
    fact = db.query(Fact).filter(Fact.conversation_id == conversation_id).first()
    if not fact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fact not found for this conversation ID"
        )
    return fact

@app.get("/facts/all", response_model=List[FactResponse])
async def read_all_facts(
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Retrieve all facts"""
    facts = db.query(Fact).all()
    return facts

@app.put("/facts", response_model=FactResponse)
async def update_fact(
    fact_data: FactUpdate,
    conversation_id: str = Header(..., alias="X-Conversation-ID"),
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Update a fact by conversation ID"""
    fact = db.query(Fact).filter(Fact.conversation_id == conversation_id).first()
    if not fact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fact not found for this conversation ID"
        )
    
    fact.fact = fact_data.fact
    db.commit()
    db.refresh(fact)
    return fact

@app.delete("/facts", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fact(
    conversation_id: str = Header(..., alias="X-Conversation-ID"),
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Delete a fact by conversation ID"""
    fact = db.query(Fact).filter(Fact.conversation_id == conversation_id).first()
    if not fact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fact not found for this conversation ID"
        )
    
    db.delete(fact)
    db.commit()
    return None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
