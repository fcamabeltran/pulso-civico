from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.compare_service import compare_candidates
from app.services.share_service import generate_comparison_image

router = APIRouter()


@router.get("/share-image")
def share_image(c1: int, c2: int, db: Session = Depends(get_db)) -> Response:
    compare_data = compare_candidates(db, c1, c2)
    image = generate_comparison_image(compare_data)
    return Response(content=image, media_type="image/png")

