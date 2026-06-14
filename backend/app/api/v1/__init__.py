from fastapi import APIRouter
from app.api.v1 import campaigns, customers, twins, insights, callbacks, events, auth, xenopilot, aws_status

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
router.include_router(customers.router, prefix="/customers", tags=["customers"])
router.include_router(twins.router, prefix="/twins", tags=["twins"])
router.include_router(insights.router, prefix="/insights", tags=["insights"])
router.include_router(callbacks.router, prefix="/campaigns", tags=["callbacks"])
router.include_router(events.router, prefix="/events", tags=["events"])
router.include_router(xenopilot.router, prefix="/xenopilot", tags=["xenopilot"])
router.include_router(aws_status.router, prefix="/aws", tags=["aws"])

