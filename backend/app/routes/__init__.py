from fastapi import APIRouter

from app.routes.ai_assistant import router as ai_router
from app.routes.candidates import router as candidates_router
from app.routes.compare import router as compare_router
from app.routes.formulas import router as formulas_router
from app.routes.formula_members import router as formula_members_router
from app.routes.search import router as search_router
from app.routes.share import router as share_router

api_router = APIRouter()
api_router.include_router(candidates_router, tags=["candidates"])
api_router.include_router(compare_router, tags=["compare"])
api_router.include_router(search_router, tags=["search"])
api_router.include_router(ai_router, tags=["ai_assistant"])
api_router.include_router(share_router, tags=["share"])
api_router.include_router(formulas_router, tags=["formulas"])
api_router.include_router(formula_members_router, tags=["formula_members"])
