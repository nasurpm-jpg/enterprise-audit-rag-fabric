import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, FieldValidationInfo, field_validator
from openai import OpenAI

class ComplianceCriterion(BaseModel):
    criterion_name: str = Field(..., description="The name of the corporate standard or safety rule.")
    passed: bool = Field(..., description="True if the document completely satisfies this rule.")
    weight: float = Field(..., description="The weight of this criterion in the overall score (0.0 to 1.0).")
    deduction_reason: Optional[str] = Field(None, description="Detailed explanation if passed is False.")

class AuditEvaluationPayload(BaseModel):
    document_id: str = Field(..., description="Unique enterprise identifier for the source report.")
    overall_quality_score: float = Field(..., description="Calculated final score strictly between 0 and 100.")
    criteria_breakdown: List[ComplianceCriterion] = Field(..., description="Granular check-by-check validation trace.")
    systemic_risks_detected: List[str] = Field(..., description="High-level corporate patterns or failures caught in the text.")
    architectural_audit_trail: str = Field(..., description="Step-by-step technical justification of the AI's grading path.")

    @field_validator("overall_quality_score")
    @classmethod
    def validate_score_bounds(cls, v: float, info: FieldValidationInfo) -> float:
        if not (0.0 <= v <= 100.0):
            raise ValueError("Enterprise Quality Score must be tightly bound between 0.0 and 100.0")
        return round(v, 2)

class EnterpriseQualityScorer:
    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def evaluate_report(self, doc_id: str, report_text: str, compliance_framework: str) -> AuditEvaluationPayload:
        system_prompt = (
            "You are a Senior Corporate Auditor embedded in an automated Enterprise Architecture Office. "
            "Your objective is to ingest unstructured vendor or internal audit reports and rigorously score them "
            "on a 0-100% scale based on a provided compliance framework. "
            "You must populate every field of the schema explicitly. The overall_quality_score must mathematically "
            "match the weighted outcome of your criteria breakdown. Do not leave any fields blank."
        )
        user_content = f"COMPLIANCE FRAMEWORK PROTOCOLS:\n{compliance_framework}\n\nUNSTRUCTURED SOURCE REPORT TO AUDIT:\n{report_text}"
        
        response = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format=AuditEvaluationPayload,
            temperature=0.0
        )
        payload = response.choices.message.parsed
        payload.document_id = doc_id
        return payload
