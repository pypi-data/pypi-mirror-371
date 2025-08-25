import logging
import os
from typing import Tuple, Dict, Any

from ray.serve.handle import DeploymentHandle

from folder_classifier.dto import FolderClassificationRequest, FolderClassification
from folder_classifier.util import build_folder, render_tree


MODEL = os.getenv("MODEL", "Qwen3-4B-Instruct-2507-classifier-FP8")

SYSTEM_PROMPT = """
You are a strict text classifier.
Output MUST be a single JSON object with exactly two keys: "category" and "reasoning".
- "category" ∈ {"matter","other"} (lowercase).
- "reasoning" ≤ 30 words.
- Do not include any double-quote (") characters inside the value of "reasoning"; use single quotes ' instead.
- No backticks, no code fences, no extra text. Return one JSON object only.
If unsure, choose "other".
""".strip()

USER_PROMPT_TEMPLATE = """
Classify the FOLDER TREE as "matter" or "other".

Definitions
- matter: The FOLDER TREE represents exactly one legal matter/container (one client/case/matter) AND includes at least one legal-work indicator.
- other: Anything else, including:
  (a) the FOLDER TREE appears to contain multiple distinct matters (a container of matters), or
  (b) the ROOT NAME is a common subfolder/stage/type (e.g., "Correspondence", "Drafts", "Pleadings", "Court Documents", "Billing", "Evidence"), or
  (c) legal-work indicators are absent, or
  (d) there are zero files with extensions anywhere in the tree, or
  (e) contents are exclusively non-legal domains (finance/accounting/IT/admin) with no legal-work indicators, or
  (f) the ROOT NAME is generic/system-generated and not matter-specific (see R9).

Decision Rules (apply in order; case-insensitive)
RC_container: Any indication the FOLDER TREE holds more than one distinct matter (e.g., multiple top-level matter-like subfolders; repeated separate matter numbers/clients) → category=other.
R0_subfolder: ROOT NAME equals a common matter subfolder/stage/type (e.g., Correspondence/Emails, File Notes/Attendance Notes, Searches/Certificates, Court Documents/Pleadings/Evidence/Disclosure/Discovery, Drafts/Final/Signed/Executed, Billing/Invoices/Time Records) → category=other.
R7_files_present: Must contain ≥1 file with an extension (e.g., .pdf, .docx) anywhere in the tree; if none → category=other.
R8_nonlegal_only: If the tree shows strong non-legal domain signals (finance/accounting/IT/admin) and NO legal-work indicators (R2–R4 or R6), classify as other.
    • Finance/Accounting examples: BAS/Business Activity Statement, IAS, GST, Tax Return, PAYG, Payroll, Timesheets, Payslips, Superannuation, Xero/MYOB/QuickBooks exports, General Ledger, Trial Balance, Journals, Bank Statements.
    • IT/Systems examples: Backups, Logs, Source Code, Git, DevOps, Server/Network/VPN, Mailboxes, Google Workspace/Microsoft 365 admin.
    • Admin-only examples: generic receipts, vendor invoices, expense folders without legal context.
    • Note: “Billing/Invoices/Time Records” inside a matter is a typical legal subfolder; R8 applies only when legal indicators are entirely absent.
R9_generic_rootname: If the ROOT NAME is generic/system-generated and not matter-specific → category=other (even if legal documents appear underneath).
    • Examples: "CORTO Generated", "Generated Files", "Exports", "Uploads", "Scans", "Shared", "Dropbox Shared", "Google Drive", "OneDrive", "SharePoint", "Archive", "Backup", "Temp", "Incoming", "Outbox", "Bulk Import".
    • Heuristic: words like generated/export/import/sync/shared/archive/backup/temp/uploads/downloads indicate a system or generic container, not a single matter.
R1_rootname: ROOT NAME resembles a single matter/container (matter/file/case number; client/surname/company; or a combination such as “12345 Smith” or “Smith – Contract Dispute”).
R2_initial_docs: Early-stage matter docs (cost agreement/disclosure, retainer/engagement, intake/onboarding).
R3_legal_docs: Legal document types (agreement, contract, deed, will, affidavit, statement, advice, brief, pleadings, court forms, subpoena, orders, judgment, undertaking, notice of appeal, docket/case forms).
R4_legal_subfolders: Typical legal subfolders (correspondence/emails, file notes/attendance notes, searches/certificates, court documents/evidence/disclosure/discovery, drafts/final/signed/executed, billing/invoices/time records).
R5_support_filename_patterns: Supportive only (not decisive): versioning (v1/v2/v3), “final”, “executed”, “signed”, eight-digit dates (YYYYMMDD/DDMMYYYY).
R6_jurisdiction: Court/jurisdiction/case references (generic court acronyms, registry references, docket patterns).

Decision
- If RC_container → category=other (stop).
- Else if R0_subfolder → category=other (stop).
- Else if NOT R7_files_present → category=other (stop).
- Else if R8_nonlegal_only → category=other (stop).
- Else if R9_generic_rootname → category=other (stop).
- Else if R1_rootname AND any of {R2_initial_docs, R3_legal_docs, R4_legal_subfolders, R6_jurisdiction} AND no multi-matter signal → category=matter.
  (R5_support_filename_patterns cannot be used alone to justify "matter"; it is supportive only.)
- Else → category=other.

Normalization
- “File with extension”: name containing a period followed by a 1–5 char alphanumeric extension (e.g., .pdf, .docx). Ignore leading/trailing periods.
- Treat hyphens/underscores as separators. Ignore file extensions for semantic matching beyond the presence test. Tolerate minor typos.

Output format (JSON only; no prose before/after):
{"category": "<matter|other>", "reasoning": "≤30 words citing R# and 1–2 evidence tokens>"}

FOLDER TREE:
{folder_tree}
""".strip()


FOLDER_CLASSIFICATION_SCHEMA = FolderClassification.model_json_schema()


class FolderClassifier:
    def __init__(self, model_handle: DeploymentHandle):
        self.logger = logging.getLogger(__name__)
        self.model_handler = model_handle
        self.logger.info(f"Successfully initialized FolderClassifier")

    async def predict(self, request: FolderClassificationRequest) -> Tuple[str, str]:
        try:
            chat_completion_request = self._to_chat_completion_request(request)
            response = await self.model_handler.create_chat_completion.remote(chat_completion_request)
            content = response.choices[0].message.content
            result = FolderClassification.model_validate_json(content)
        except Exception as ex:
            self.logger.error(f"Failed to parse response: {content}\n{ex}")
            if '"category": "matter"' in content:
                result = FolderClassification(category="matter", reasoning="NA")
            else:
                result = FolderClassification(category="other", reasoning="NA")

        return result.category, result.reasoning

    @staticmethod
    def _to_chat_completion_request(request: FolderClassificationRequest) -> Dict[str, Any]:
        input_paths = request.items
        folder = build_folder(input_paths)
        folder_tree = render_tree(folder)
        chat_completion_request = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.replace("{folder_tree}", folder_tree)}
            ],
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.8,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "FolderClassification",
                    "schema": FOLDER_CLASSIFICATION_SCHEMA,
                    "strict": True,
                },
            }
        }
        return chat_completion_request





