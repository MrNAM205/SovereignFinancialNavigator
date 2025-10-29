from fastapi import APIRouter, HTTPException
from typing import Optional

from models import UserProfile

router = APIRouter()

# In-memory database for a single user profile. 
# In a real multi-user app, this would be a database lookup.
user_profile_db = {
    "user-001": UserProfile(
        id="user-001", 
        full_name="John Doe", 
        address="123 Sovereign Street, Freedom, Republic 12345",
        status="Sovereign Living Man",
        declarations=["I am a living man, not a corporation.", "I reserve all my rights without prejudice."]
    )
}

@router.get("/user-profile", response_model=UserProfile, tags=["User Profile"])
def get_user_profile() -> UserProfile:
    """Retrieves the sovereign user profile."""
    profile = user_profile_db.get("user-001")
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found.")
    return profile

@router.put("/user-profile", response_model=UserProfile, tags=["User Profile"])
def update_user_profile(profile_update: UserProfile) -> UserProfile:
    """Updates the sovereign user profile."""
    # The ID in the path would be better for a multi-user system
    profile = user_profile_db.get("user-001")
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found.")

    # Update fields
    update_data = profile_update.dict(exclude_unset=True)
    updated_profile = profile.copy(update=update_data)
    
    user_profile_db["user-001"] = updated_profile
    return updated_profile