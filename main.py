import os
import json
from core.scoring_engine import EnterpriseQualityScorer, AuditEvaluationPayload, ComplianceCriterion
from core.data_fabric_rag import EnterpriseDataFabricRAG

if __name__ == "__main__":
    API_KEY = os.getenv("OPENAI_API_KEY", "mock-key-for-architectural-validation")

    print("🚀 Initializing Vector-Backed Enterprise Data Fabric Pipeline...")
    fabric = EnterpriseDataFabricRAG()

    # 1. Ingest Documents linked to SAP Metadata
    fabric.ingest_unstructured_document(
        doc_id="AUDIT-2026-001",
        text="Critical degradation caught on pipeline block valve BV-102. High-pressure gas leak risk due to gasket seal erosion.",
        sap_metadata={"facility": "Ghawar-Main", "region": "Eastern-Province", "sap_asset_id": "SAP-VLV-102"}
    )
    
    fabric.ingest_unstructured_document(
        doc_id="AUDIT-2026-002",
        text="Environmental safety walkthrough complete. Minor oil sheen noted near containment bund 4, remediation scheduled.",
        sap_metadata={"facility": "Shaybah-B", "region": "Southern-Province", "sap_asset_id": "SAP-BND-004"}
    )

    # 2. Test Quality Assessment Scorer
    print("\n📊 Testing Module: 0-100% Quality Assessment Scorer...")
    mock_compliance_framework = """
    RULE_1: Mandatory PPE verification log must be explicitly detailed (Weight: 40% of total score).
    RULE_2: Digital signatures of the supervising site engineer must be present (Weight: 30% of total score).
    RULE_3: Clear physical environmental remediation timeline must be specified (Weight: 30% of total score).
    """
    messy_incoming_report = "Workers were wearing standard helmets on site. However, we could not find the digital authorization certificate for the supervising engineer on duty. No oil cleanup timeline has been drafted yet."

    if API_KEY == "mock-key-for-architectural-validation":
        print("⚠️ [Skipping live API call - running structural mockup trace for architectural review]")
        audit_result = AuditEvaluationPayload(
            document_id="DOC-ARAMCO-2026-009",
            overall_quality_score=40.0,
            criteria_breakdown=[
                ComplianceCriterion(criterion_name="PPE Verification", passed=True, weight=0.4),
                ComplianceCriterion(criterion_name="Engineer Digital Signature", passed=False, weight=0.3, deduction_reason="Signature missing."),
                ComplianceCriterion(criterion_name="Environmental Remediation Timeline", passed=False, weight=0.3, deduction_reason="No timeline dates provided.")
            ],
            systemic_risks_detected=["Unsupervised workflows", "Environmental spill hazards"],
            architectural_audit_trail="Passed PPE checks (40 points). Failed Engineer signature validation. Failed environmental safety compliance. Score: 40%."
        )
    else:
        scorer = EnterpriseQualityScorer(api_key=API_KEY)
        audit_result = scorer.evaluate_report(
            doc_id="DOC-ARAMCO-2026-009",
            report_text=messy_incoming_report,
            compliance_framework=mock_compliance_framework
        )

    print(json.dumps(audit_result.model_dump(), indent=2))

    # 3. Test Contextual Semantic Search
    query = "Is there an active high pressure gas leak or valve erosion failure recorded?"
    print(f"\n🔍 Executing Contextual Semantic Search for: '{query}'")
    context_matches = fabric.contextual_semantic_search(user_query=query, region_filter="Eastern-Province")
    print(json.dumps(context_matches, indent=2))
