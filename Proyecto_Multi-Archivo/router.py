# -*- coding: utf-8 -*-
from fastapi import APIRouter
from pydantic import BaseModel
from saas_audit_engine import audit_code_payload
from saas_pytest_generator import generate_pytest_suite
from saas_billing_stripe import process_mock_checkout

router = APIRouter()

class CodePayloadRequest(BaseModel):
    code: str

class CheckoutRequest(BaseModel):
    client_name: str
    plan_amount: float

@router.post("/api/v1/audit")
async def audit_endpoint(payload: CodePayloadRequest):
    return audit_code_payload(payload.code)

@router.post("/api/v1/generate-tests")
async def generate_tests_endpoint(payload: CodePayloadRequest):
    return generate_pytest_suite(payload.code)

@router.post("/api/v1/checkout/subscribe")
async def subscribe_endpoint(payload: CheckoutRequest):
    return process_mock_checkout(payload.client_name, payload.plan_amount)
