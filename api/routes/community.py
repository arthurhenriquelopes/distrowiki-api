from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from api.database import get_db
from api.db_models import DistroVote, DistroEdit, Profile
from api.security import get_current_user, get_api_key
import uuid
import datetime

router = APIRouter(prefix="/community", tags=["Community"])

# Schemas
class VoteRequest(BaseModel):
    distro_name: str
    vote_type: int # 1 or -1

class ProposeEditRequest(BaseModel):
    distro_name: str
    field: str
    new_value: str

class ReviewEditRequest(BaseModel):
    action: str # "approve" or "reject"
    comment: Optional[str] = None

class EditResponse(BaseModel):
    id: uuid.UUID
    distro_name: str
    field: str
    new_value: str
    status: str
    created_at: datetime.datetime
    user_email: Optional[str] = None # Enriched if admin

    class Config:
        from_attributes = True

# Helper to check admin
def check_admin(user_id: str, db: Session):
    role = db.query(Profile.role).filter(Profile.id == user_id).scalar()
    if role != 'admin':
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return True

@router.post("/vote")
def vote_distro(
    vote: VoteRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if vote.vote_type not in [1, -1]:
        raise HTTPException(status_code=400, detail="Vote type must be 1 (up) or -1 (down)")

    existing_vote = db.query(DistroVote).filter(
        DistroVote.user_id == user_id,
        DistroVote.distro_name == vote.distro_name
    ).first()

    if existing_vote:
        if existing_vote.vote_type == vote.vote_type:
             return {"message": "Vote already recorded"}
        else:
             existing_vote.vote_type = vote.vote_type
             db.commit()
             return {"message": "Vote updated"}
    
    new_vote = DistroVote(
        user_id=user_id,
        distro_name=vote.distro_name,
        vote_type=vote.vote_type
    )
    db.add(new_vote)
    db.commit()
    return {"message": "Vote recorded"}

@router.post("/propose-edit")
def propose_edit(
    proposal: ProposeEditRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_edit = DistroEdit(
        user_id=user_id,
        distro_name=proposal.distro_name,
        field=proposal.field,
        new_value=proposal.new_value,
        status="pending"
    )
    db.add(new_edit)
    db.commit()
    return {"message": "Edit proposal submitted for review"}

@router.get("/votes/{distro_name}")
def get_votes(distro_name: str, db: Session = Depends(get_db)):
    upvotes = db.query(func.count(DistroVote.id)).filter(
        DistroVote.distro_name == distro_name,
        DistroVote.vote_type == 1
    ).scalar()
    
    downvotes = db.query(func.count(DistroVote.id)).filter(
        DistroVote.distro_name == distro_name,
        DistroVote.vote_type == -1
    ).scalar()

    return {"distro": distro_name, "upvotes": upvotes, "downvotes": downvotes, "score": upvotes - downvotes}

# --- Admin Routes ---

@router.get("/admin/edits", response_model=List[EditResponse])
def get_pending_edits(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_admin(user_id, db)
    
    # Fetch edits with user info potentially?
    edits = db.query(DistroEdit).filter(DistroEdit.status == "pending").order_by(DistroEdit.created_at.desc()).all()
    
    # Manually map to response
    response = []
    for edit in edits:
        # Fetch email
        email = db.query(Profile.email).filter(Profile.id == edit.user_id).scalar()
        item = EditResponse.from_orm(edit)
        item.user_email = email
        response.append(item)
        
    return response

@router.post("/admin/edits/{edit_id}/review")
def review_edit(
    edit_id: uuid.UUID,
    review: ReviewEditRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_admin(user_id, db)
    
    edit = db.query(DistroEdit).filter(DistroEdit.id == edit_id).first()
    if not edit:
        raise HTTPException(status_code=404, detail="Edit not found")
        
    if review.action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    edit.status = "approved" if review.action == "approve" else "rejected"
    edit.admin_comment = review.comment
    edit.updated_at = func.now()
    
    db.commit()
    
    # TODO: Integration with Google Sheets or Main JSON here (if approved)
    # Since we lack keys for now, we just mark DB status.
    
    return {"message": f"Edit {review.action}d"}

@router.post("/admin/promote")
def promote_user(
    email: str = Body(..., embed=True),
    api_key: str = Depends(get_api_key), # Protect with Server API KEY (from .env)
    db: Session = Depends(get_db)
):
    """
    Bootstrap endpoint to make a user admin. Protected by X-API-Key.
    """
    user = db.query(Profile).filter(Profile.email == email).first()
    if not user:
         raise HTTPException(status_code=404, detail="User not found")
    
    user.role = "admin"
    db.commit()
    return {"message": f"User {email} promoted to admin"}
