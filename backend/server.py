from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import base64
from io import BytesIO
from PIL import Image
from reportlab.lib.pagesizes import A4, A3, landscape, portrait
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
try:
    from pypdf import PdfMerger
except ImportError:
    from pypdf import PdfWriter as PdfMerger
import tempfile
import asyncio
import zipfile
import shutil
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'document_scanner_db')]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Emergent LLM Key
# OpenAI direct integration (primary)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
LLM_FALLBACK_ENABLED = os.environ.get('LLM_FALLBACK_ENABLED', 'true').lower() == 'true'

# Lazy OpenAI client init
_openai_client = None

def get_openai_client():
    global _openai_client
    if _openai_client is None and OPENAI_API_KEY:
        try:
            from openai import OpenAI
            _openai_client = OpenAI(api_key=OPENAI_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            _openai_client = None
    return _openai_client

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Import auth dependencies after database setup
from auth_dependencies import get_current_user, require_approved_user, require_admin

# Document type mapping
DOCUMENT_TYPES = {
    "Bản mô tả ranh giới, mốc giới thửa đất": "BMT",
    "Bản vẽ (Trích lục, đo tách, chỉnh lý)": "HSKT",
    "Trích lục": "HSKT",
    "Trích đo": "HSKT",
    "Phiếu đo đạc chỉnh lý": "HSKT",
    "Bản vẽ tách thửa": "HSKT",
    "Bản vẽ hợp thửa": "HSKT",
    "Bản vẽ hoàn công": "BVHC",
    "Bản vẽ nhà": "BVN",
    "Bảng kê khai diện tích đang sử dụng": "BKKDT",
    "Bảng liệt kê danh sách các thửa đất cấp giấy": "DSCG",
    "Biên bản bán đấu giá tài sản": "BBBDG",
    "Biên bản bàn giao đất trên thực địa": "BBGD",
    "Biên bản của Hội đồng đăng ký đất đai lần đầu": "BBHDDK",
    "Biên bản kiểm tra nghiệm thu công trình xây dựng": "BBNT",
    "Biên bản kiểm tra sai sót trên Giấy chứng nhận": "BBKTSS",
    "Biên bản kiểm tra, xác minh hiện trạng sử dụng đất": "BBKTHT",
    "Biên bản về việc kết thúc công khai công bố di chúc": "BBKTDC",
    "Biên bản về việc kết thúc thông báo niêm yết công khai kết quả kiểm tra hồ sơ đăng ký cấp GCNQSD đất": "KTCKCG",
    "Biên bản về việc kết thúc thông báo niêm yết công khai về việc mất GCNQSD đất": "KTCKMG",
    "Biên lai thu thuế sử dụng đất phi nông nghiệp": "BLTT",
    "Căn cước công dân": "CCCD",
    "Danh sách chủ sử dụng và các thửa đất (mẫu 15)": "DS15",
    "Danh sách công khai hồ sơ cấp giấy CNQSDĐ": "DSCK",
    "Di chúc": "DICHUC",
    "Đơn cam kết, Giấy cam Kết": "DCK",
    "Đơn đăng ký biến động đất đai, tài sản gắn liền với đất": "DDKBD",
    "Đơn đăng ký đất đai, tài sản gắn liền với đất": "DDK",
    "Đơn đề nghị chuyển hình thức giao đất (cho thuê đất)": "CHTGD",
    "Đơn đề nghị điều chỉnh quyết định giao đất (cho thuê đất, cho phép chuyển mục đích)": "DCQDGD",
    "Đơn đề nghị miễn giảm Lệ phí trước bạ, thuế thu nhập cá nhân": "DMG",
    "Đơn đề nghị sử dụng đất kết hợp đa mục đích": "DMD",
    "Đơn xác nhận, Giấy Xác nhận": "DXN",
    "Đơn xin (đề nghị) chuyển mục đích sử dụng đất": "DXCMD",
    "Đơn xin (đề nghị) gia hạn sử dụng đất": "DGH",
    "Đơn xin (đề nghị) giao đất, cho thuê đất": "DXGD",
    "Đơn xin (đề nghị) tách thửa đất, hợp thửa đất": "DXTHT",
    "Đơn xin cấp đổi Giấy chứng nhận": "DXCD",
    "Đơn xin điều chỉnh thời hạn sử dụng đất của dự án đầu tư": "DDCTH",
    "Đơn xin xác nhận lại thời hạn sử dụng đất nông nghiệp": "DXNTH",
    "Giấy chứng nhận kết hôn": "GKH",
    "Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất": "GCNM",
    "Giấy chứng nhận quyền sử dụng đất": "GCNC",
    "Giấy đề nghị xác nhận các khoản nộp vào ngân sách": "GXNNVTC",
    "Giấy Khai Sinh": "GKS",
    "Giấy nộp tiền vào Ngân sách nhà nước": "GNT",
    "Giấy sang nhượng đất": "GSND",
    "Giấy tờ liên quan (các loại giấy tờ kèm theo)": "GTLQ",
    "Giấy ủy quyền": "GUQ",
    "Giấy xác nhận đăng ký lần đầu": "GXNDKLD",
    "Giấy xin phép xây dựng": "GPXD",
    "Hoá đơn giá trị gia tăng": "hoadon",
    "Hoàn thành công tác bồi thường hỗ trợ": "HTBTH",
    "Hợp đồng chuyển nhượng, tặng cho quyền sử dụng đất": "HDCQ",
    "Hợp đồng mua bán tài sản bán đấu giá": "HDBDG",
    "Hợp đồng thế chấp quyền sử dụng đất": "HDTHC",
    "Hợp đồng thi công": "HDTCO",
    "Hợp đồng thuê đất, điều hỉnh hợp đồng thuê đất": "HDTD",
    "Hợp đồng ủy quyền": "HDUQ",
    "Phiếu chuyển thông tin nghĩa vụ tài chính": "PCT",
    "Phiếu chuyển thông tin để xác định nghĩa vụ tài chính": "PCT",
    "Giấy tiếp nhận hồ sơ và hẹn trả kết quả": "BN",
    "Biên nhận hồ sơ": "BN",
    "Phiếu kiểm tra hồ sơ": "PKTHS",
    "Phiếu lấy ý kiến khu dân cư": "PLYKDC",
    "Phiếu xác nhận kết quả đo đạc": "PXNKQDD",
    "Phiếu yêu cầu đăng ký biện pháp bảo đảm bằng quyền sử dụng đất, tài sản gắn liền với đất": "DKTC",
    "Phiếu yêu cầu đăng ký thay đổi nội dung biện pháp bảo đảm bằng quyền sdđ, tài sản gắn liền với đất": "DKTD",
    "Phiếu yêu cầu xóa đăng ký biện pháp bảo đảm bằng quyền sử dụng đất, tài sản gắn liền với đất": "DKXTC",
    "Quét mã QR": "QR",
    "Quyết định cho phép chuyển mục đích": "QDCMD",
    "Quyết định cho phép tách, hợp thửa đất": "QDTT",
    "Quyết định chuyển hình thức giao đất (cho thuê đất)": "QDCHTGD",
    "Quyết định điều chỉnh quyết định giao đất (cho thuê đất, cho phép chuyển mục đích)": "QDDCGD",
    "Quyết định điều chỉnh thời hạn SDĐ của dự án đầu tư": "QDDCTH",
    "Quyết định gia hạn sử dụng đất khi hết thời hạn SDĐ": "QDGH",
    "Quyết định giao đất, cho thuê đất": "QDGTD",
    "Quyết định hủy Giấy chứng nhận quyền sử dụng đất": "QDHG",
    "Quyết định phê duyệt phương án bồi thường, hỗ trợ, tái định cư": "QDPDBT",
    "Quyết định phê quyệt điều chỉnh quy hoạch": "QDDCQH",
    "Quyết định phê quyệt đơn giá": "QDPDDG",
    "Quyết định thi hành án theo đơn yêu cầu": "QDTHA",
    "Quyết định thu hồi đất": "QDTH",
    "Quyết định về hình thức sử dụng đất": "QDHTSD",
    "Quyết định xử phạt": "QDXP",
    "Sơ đồ dự kiến tách thửa": "SDTT",
    "Thông báo cập nhật, chỉnh lý biến động": "TBCNBD",
    "Thông báo công bố công khai di chúc": "CKDC",
    "Thông báo thuế (trước bạ, thuế TNCN, tiền sử dụng đất)": "TBT",
    "Thông báo về việc chuyển thông tin Giấy chứng nhận bị mất để niêm yết công khai": "TBMG",
    "Thông báo về việc công khai kết quả thẩm tra xét duyệt hồ sơ cấp giấy chứng nhận quyền sử dụng đất": "TBCKCG",
    "Thông báo về việc niêm yết công khai mất giấy chứng nhận quyền sử dụng đất": "TBCKMG",
    "Thông báo xác nhận Hoàn thành nghĩa vụ tài chính": "HTNVTC",
    "Tờ khai thuế (trước bạ, thuế TNCN, tiền sử dụng đất)": "TKT",
    "Tờ trình về giao đất (cho thuê đất, cho phép chuyển mục đích)": "TTr",
    "Tờ trình về việc đăng ký đất đai, tài sản gắn liền với đất (UBND xã)": "TTCG",
    "Văn bản cam kết tài sản riêng": "CKTSR",
    "Văn bản chấp thuận cho phép chuyển mục đích": "VBCTCMD",
    "Văn bản đề nghị chấp thuận nhận chuyển nhượng, thuê, góp vốn quyền sdđ": "VBDNCT",
    "Văn bản đề nghị thẩm định, phê duyệt phương án sdđ": "PDPASDD",
    "Văn bản thỏa thuận phân chia di sản thừa kế": "VBTK",
    "Văn bản thỏa thuận quyền sử dụng đất của hộ gia đình": "TTHGD",
    "Văn bản thoả thuận về việc chấm dứt quyền hạn chế đối với thửa đất liền kề": "CDLK",
    "Văn bản thỏa thuận về việc xác lập quyền hạn chế đối với thửa đất liền kề": "HCLK",
    "Văn bản từ chối nhận di sản thừa kế": "VBTC",
    "Văn bản phân chia tài sản chung vợ chồng": "PCTSVC"
}


# Define Models
class LlmHealth(BaseModel):
    status: str
    provider: str
    model: Optional[str] = None
    openai_available: bool = False
    emergent_available: bool = False
    details: Optional[str] = None


class ScanResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_filename: str
    detected_type: str
    detected_full_name: str
    short_code: str
    confidence_score: float
    image_base64: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None  # NEW: Group scans by session
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UpdateFilenameRequest(BaseModel):
    id: str
    new_short_code: str


class ExportPDFRequest(BaseModel):
    scan_ids: List[str]


class DocumentRule(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    short_code: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CreateRuleRequest(BaseModel):
    full_name: str
    short_code: str


class UpdateRuleRequest(BaseModel):
    full_name: Optional[str] = None
    short_code: Optional[str] = None


class FolderScanFileResult(BaseModel):
    """Result for a single file in folder scan"""
    relative_path: str  # Path relative to ZIP root (e.g., "folder1/subfolder/file.jpg")
    original_filename: str
    detected_full_name: str
    short_code: str
    confidence_score: float
    status: str  # "success", "error", "skipped"
    error_message: Optional[str] = None
    user_id: Optional[str] = None


class FolderBatchResult(BaseModel):
    """Result for a single folder batch"""
    folder_name: str
    total_files: int
    success_count: int
    error_count: int
    processing_time_seconds: float
    download_url: str
    files: List[FolderScanFileResult]


class FolderScanJobStatus(BaseModel):
    """Status of a folder scan job"""
    job_id: str
    status: str  # "processing", "completed", "error"
    total_folders: int
    completed_folders: int
    current_folder: Optional[str] = None
    folder_results: List[FolderBatchResult]
    error_message: Optional[str] = None
    started_at: datetime
    updated_at: datetime


class FolderScanStartResponse(BaseModel):
    """Response when starting a folder scan"""
    job_id: str
    message: str
    total_folders: int
    total_files: int
    status_url: str


async def get_document_rules() -> dict:
    """Get all document rules from database or initialize from DOCUMENT_TYPES"""
    try:
        # DROP unique index if exists (we now allow duplicate short_codes)
        try:
            await db.document_rules.drop_index("short_code_1")
            logger.info("Dropped unique index on short_code to allow duplicates")
        except Exception:
            # Index doesn't exist or already dropped
            pass
        
        # Check if rules exist in database
        rules_count = await db.document_rules.count_documents({})
        
        if rules_count == 0:
            # First time: migrate from DOCUMENT_TYPES to database
            logger.info("Initializing document rules from DOCUMENT_TYPES")
            for full_name, short_code in DOCUMENT_TYPES.items():
                try:
                    rule = DocumentRule(
                        full_name=full_name,
                        short_code=short_code
                    )
                    # Use insert_one with error handling to prevent duplicates
                    await db.document_rules.insert_one(rule.model_dump())
                except Exception as e:
                    # Skip if already exists (duplicate key error)
                    if "duplicate" in str(e).lower():
                        logger.debug(f"Rule {short_code} already exists, skipping")
                    else:
                        logger.error(f"Error inserting rule {short_code}: {e}")
            
            final_count = await db.document_rules.count_documents({})
            logger.info(f"Initialized {final_count} document rules")
        
        # Fetch all rules from database
        rules_cursor = db.document_rules.find({})
        rules = await rules_cursor.to_list(length=None)
        
        # Convert to dict format {full_name: short_code}
        rules_dict = {rule['full_name']: rule['short_code'] for rule in rules}
        
        return rules_dict
    except Exception as e:
        logger.error(f"Error getting document rules: {e}")
        # Fallback to hardcoded DOCUMENT_TYPES
        return DOCUMENT_TYPES


async def smart_crop_and_analyze(image_bytes: bytes) -> tuple[str, dict]:
    """
    Two-Pass Smart Cropping:
    Pass 1: Crop 30% and detect emblem
    - If emblem found in 30% → GCN mới (quốc huy ở đầu 10-15%) → crop 40%
    - If no emblem in 30% → GCN cũ (quốc huy ở giữa 30-40%) → crop 60%
    Pass 2: Analyze with optimal crop
    
    Note: Nếu emblem XUẤT HIỆN trong 30% crop thì có nghĩa nó ở vị trí 0-30%,
    VẪN CÓ THỂ là GCN cũ với quốc huy ở 25-30%. Để an toàn, tăng crop lên 40-60%.
    
    Returns: (cropped_image_base64, analysis_result)
    """
    try:
        # PASS 1: Quick emblem detection with 30% crop
        logger.info("🔍 PASS 1: Detecting emblem with 30% crop...")
        quick_crop_base64 = resize_image_for_api(image_bytes, max_size=800, crop_top_only=True, crop_percentage=0.30)
        
        has_emblem = await detect_emblem_in_image(quick_crop_base64)
        
        # PASS 2: Smart cropping based on emblem detection
        if has_emblem:
            # Emblem found in 30% crop → Could be GCN mới OR GCN cũ
            # Use 65% to be safe (covers single page + 2-page spread cases)
            logger.info("✅ Emblem detected in top 30% → Using 65% crop (safe for all GCN types)")
            optimal_crop_percentage = 0.65
        else:
            # No emblem in 30% → Very rare, maybe not GCN or image issue
            # Use 70% as maximum safe crop
            logger.info("⚠️  Emblem NOT detected in top 30% → Using 70% crop (maximum coverage)")
            optimal_crop_percentage = 0.70
        
        # Create optimal crop for final analysis
        cropped_image_base64 = resize_image_for_api(
            image_bytes, 
            max_size=1024, 
            crop_top_only=True, 
            crop_percentage=optimal_crop_percentage
        )
        
        # Analyze with optimal crop
        logger.info(f"📊 PASS 2: Analyzing document with {int(optimal_crop_percentage*100)}% crop...")
        analysis_result = await analyze_document_with_vision(cropped_image_base64)
        
        return cropped_image_base64, analysis_result
        
    except Exception as e:
        logger.error(f"Error in smart crop and analyze: {e}")
        # Fallback: use 45% crop (middle ground)
        logger.info("⚠️  Fallback to 45% crop due to error")
        fallback_crop = resize_image_for_api(image_bytes, max_size=1024, crop_top_only=True, crop_percentage=0.45)
        analysis = await analyze_document_with_vision(fallback_crop)
        return fallback_crop, analysis


async def detect_emblem_in_image(image_base64: str) -> bool:
    """Quick check to detect Vietnamese national emblem in image - for smart cropping"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"emblem_detect_{uuid.uuid4()}",
            system_message="You are a visual recognition expert. Answer with simple YES or NO only."
        ).with_model("openai", "gpt-4o")
        
        image_content = ImageContent(image_base64=image_base64)
        
        prompt = """Look at this image carefully.
        
Do you see the Vietnamese national emblem (QUỐC HUY VIỆT NAM)?

The emblem has these features:
- Golden/yellow star with 5 points
- Red circular background
- Hammer and sickle symbols
- Usually at the top of official documents

Answer with ONLY ONE WORD:
- "YES" if you clearly see the Vietnamese national emblem
- "NO" if you don't see it or unsure

Your answer:"""
        
        user_message = UserMessage(text=prompt, file_contents=[image_content])
        response = await chat.send_message(user_message)
        
        # Parse response
        answer = response.strip().upper()
        has_emblem = "YES" in answer
        
        logger.info(f"Emblem detection result: {answer} → {has_emblem}")
        return has_emblem
        
    except Exception as e:
        logger.error(f"Error detecting emblem: {e}")
        # Fallback: assume emblem exists (use safer crop)
        return False


async def _analyze_with_openai_vision(image_base64: str, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
    """Call OpenAI Vision (gpt-4o-mini) and return text content."""
    client = get_openai_client()
    if not client:
        raise RuntimeError("OpenAI client not initialized. Missing or invalid OPENAI_API_KEY")
    data_url = f"data:image/jpeg;base64,{image_base64}"
    # Use chat.completions (OpenAI SDK v1.x)
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a precise OCR and document classifier. Always answer in JSON when asked."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "auto"}}
                ]
            }
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )
    content = resp.choices[0].message.content or ""
    return content


def _is_retryable_llm_error(e: Exception) -> bool:
    s = str(e).lower()
    if any(tok in s for tok in ["rate", "429", "timeout", "temporar", "unavailable", "connection", "reset"]):
        return True
    if any(tok in s for tok in ["unauthorized", "401", "invalid_api_key", "permission", "forbidden"]):
        return False
    return True


async def analyze_document_with_vision(image_base64: str) -> dict:
    """Analyze document using OpenAI Vision API with dynamic rules from database"""
    try:
        # Get document rules from database
        document_rules = await get_document_rules()
        
        # Create a mapping list for the prompt
        doc_types_list = "\n".join([f"- {full_name}: {code}" for full_name, code in document_rules.items()])
        
        # Build prompt (kept from previous logic)
        prompt = f"""IMPORTANT: This is a DOCUMENT ANALYSIS task for land registry documents. 
Any faces/photos in the document are part of official government records (ID photos on land certificates).
Please analyze ONLY the document text and official stamps, not the personal photos.

Nhận diện tài liệu dựa vào QUỐC HUY và TIÊU ĐỀ.

🎯 ƯU TIÊN 1: NHẬN DIỆN QUỐC HUY VIỆT NAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Nếu thấy QUỐC HUY Việt Nam (ngôi sao vàng, búa liềm) → Đây là tài liệu chính thức

🔍 Sau đó kiểm tra tiêu đề:
  • "Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất" → GCNM (GCN mới - tiêu đề DÀI)
  • "Giấy chứng nhận quyền sử dụng đất" (KHÔNG có "quyền sở hữu...") → GCNC (GCN cũ - tiêu đề NGẮN)
  • Nếu chỉ thấy "GIẤY CHỨNG NHẬN" mà không rõ tiếp theo → GCNC
  • Các loại khác theo danh sách bên dưới

⚠️ IMPORTANT for 2-page horizontal documents:
- If you see orange/colored background with national emblem on RIGHT side → This is GCNC
- Focus on the RIGHT page for title

⚠️ IGNORE any photos/faces in the document - focus ONLY on text and official stamps.

⚠️ QUY TẮC NGHIÊM NGẶT: CHỈ CHẤP NHẬN KHI KHỚP 100% CHÍNH XÁC!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ KHÔNG được đoán hoặc chọn "gần giống"
❌ KHÔNG được bỏ qua từ khóa phân biệt
❌ KHÔNG được nhận diện nếu chỉ khớp 1 nửa hoặc vài chữ
✅ CHỈ chọn khi khớp CHÍNH XÁC, TOÀN BỘ tiêu đề với danh sách

NẾU KHÔNG KHỚP CHÍNH XÁC 100% → Trả về:
  - detected_full_name: "Không rõ loại tài liệu"
  - short_code: "UNKNOWN"
  - confidence: 0.1

⚠️ QUAN TRỌNG: Một tài liệu có thể có NHIỀU TRANG
  - Trang 1: Có tiêu đề "GIẤY CHỨNG NHẬN" → GCN
  - Trang 2, 3, 4...: Không có tiêu đề mới → Hệ thống sẽ tự động gán là GCN
  - CHỈ KHI thấy tiêu đề MỚI khớp 100% → Mới đổi sang loại mới

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CÁC CẶP DỄ NHẦM - PHẢI KHỚP CHÍNH XÁC:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. "Đơn đăng ký BIẾN ĐỘNG đất đai" → DDKBD (PHẢI có "BIẾN ĐỘNG")
   "Đơn đăng ký đất đai" → DDK (KHÔNG có "BIẾN ĐỘNG")
   Nếu không rõ có "BIẾN ĐỘNG" không → "UNKNOWN"

2. "Hợp đồng CHUYỂN NHƯỢNG" → HDCQ (PHẢI có "CHUYỂN NHƯỢNG")
   "Hợp đồng THUÊ" → HDTD (PHẢI có "THUÊ")
   "Hợp đồng THẾ CHẤP" → HDTHC (PHẢI có "THẾ CHẤP")
   Nếu không rõ loại nào → "UNKNOWN"

3. "Quyết định CHO PHÉP chuyển mục đích" → QDCMD (PHẢI có "CHO PHÉP")
   Nếu không thấy "CHO PHÉP" rõ ràng → "UNKNOWN"

VÍ DỤ:
- Thấy "Giấy chứng nhận quyền sử dụng" (khớp 100%) → GCN ✅
- Thấy "Bản mô tả" (khớp 100%) → BMT ✅
- Thấy "Hợp đồng" nhưng không rõ loại → UNKNOWN ❌
- Chỉ thấy nội dung, không có tiêu đề → UNKNOWN ❌

DANH SÁCH ĐẦY ĐỦ (khớp chính xác):
{doc_types_list}

QUY TRÌNH KIỂM TRA:
━━━━━━━━━━━━━━━━━━
1. Tìm quốc huy Việt Nam (nếu có → tài liệu chính thức)
2. Đọc tiêu đề đầy đủ
3. Tìm trong danh sách có tên CHÍNH XÁC 100%?
4. NẾU CÓ → Trả về tên + mã chính xác, confidence: 0.9
5. NẾU KHÔNG → Trả về "UNKNOWN", confidence: 0.1

TRẢ VỀ JSON:
{{
  "detected_full_name": "Tên CHÍNH XÁC từ danh sách HOẶC 'Không rõ loại tài liệu'",
  "short_code": "MÃ CHÍNH XÁC HOẶC 'UNKNOWN'",
  "confidence": 0.9 hoặc 0.1
}}

❗ LƯU Ý: 
- CHỈ trả về mã khi khớp TOÀN BỘ tiêu đề với danh sách
- KHÔNG khớp 1 nửa, vài chữ, hoặc gần giống
- Backend sẽ tự xử lý việc gán trang tiếp theo"""
        
        # Try OpenAI primary; fallback to Emergent if enabled
        try:
            response_text = await _analyze_with_openai_vision(image_base64, prompt, max_tokens=700, temperature=0.1)
        except Exception as e:
            logger.warning(f"Primary OpenAI vision failed: {e}")
            if LLM_FALLBACK_ENABLED and EMERGENT_LLM_KEY and _is_retryable_llm_error(e):
                # Emergent fallback using previous implementation
                try:
                    chat = LlmChat(
                        api_key=EMERGENT_LLM_KEY,
                        session_id=f"doc_scan_{uuid.uuid4()}",
                        system_message="Bạn là AI chuyên gia phân loại tài liệu đất đai Việt Nam. Luôn trả về JSON."
                    ).with_model("openai", "gpt-4o")
                    image_content = ImageContent(image_base64=image_base64)
                    user_message = UserMessage(text=prompt, file_contents=[image_content])
                    response_text = await chat.send_message(user_message)
                except Exception as fe:
                    logger.error(f"Fallback Emergent failed: {fe}")
                    raise
            else:
                raise
        
        # Parse JSON response
        import json
        response_text = (response_text or "").strip()
        logger.info(f"Vision raw response (first 200): {response_text[:200]}")
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        try:
            result = json.loads(response_text)
        except Exception:
            # Try to extract inline JSON
            import re
            m = re.search(r'\{[\s\S]*\}', response_text)
            if m:
                import json as _json
                try:
                    result = _json.loads(m.group())
                except Exception:
                    result = None
            else:
                result = None
        
        if not result:
            # If policy refusal or non-json, classify as CONTINUATION
            if any(x in response_text.lower() for x in ["can't help", "sorry", "policy"]):
                return {
                    "detected_full_name": "Không có tiêu đề",
                    "short_code": "CONTINUATION",
                    "confidence": 0.1
                }
            # Default unknown
            return {
                "detected_full_name": "Không xác định",
                "short_code": "UNKNOWN",
                "confidence": 0.1
            }
        
        return {
            "detected_full_name": result.get("detected_full_name", "Không xác định"),
            "short_code": result.get("short_code", "UNKNOWN"),
            "confidence": result.get("confidence", 0.0)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        return {
            "detected_full_name": "Lỗi phân tích",
            "short_code": "ERROR",
            "confidence": 0.0
        }


def resize_image_for_api(image_bytes: bytes, max_size: int = 1024, crop_top_only: bool = True, crop_percentage: float = 0.35) -> str:
    """Resize image and convert to base64 - SMART CROP: adaptive based on emblem detection"""
    try:
        img = Image.open(BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # SMART CROP: Dynamic crop based on crop_percentage parameter
        if crop_top_only:
            width, height = img.size
            crop_height = int(height * crop_percentage)
            img = img.crop((0, 0, width, crop_height))
            logger.info(f"Smart cropped: {height}px → {crop_height}px ({int(crop_percentage*100)}% crop)")
        
        # Optimized resize for speed + quality balance
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # High quality for Vietnamese OCR
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=80, optimize=True)
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return img_base64
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        raise


def create_pdf_from_image(image_base64: str, output_path: str, filename: str):
    """Create a PDF file from base64 image - AUTO-DETECT A3/A4 and orientation"""
    try:
        # Decode base64 image
        image_data = base64.b64decode(image_base64)
        img = Image.open(BytesIO(image_data))
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        img_width, img_height = img.size
        
        # SMART PAGE SIZE DETECTION
        # A3 = 297mm x 420mm = 842pt x 1191pt
        # A4 = 210mm x 297mm = 595pt x 842pt
        
        # Determine if landscape or portrait
        is_landscape = img_width > img_height
        
        # Calculate aspect ratio to detect A3 vs A4
        aspect_ratio = max(img_width, img_height) / min(img_width, img_height)
        
        # A3 aspect ratio ≈ 1.414 (√2)
        # A4 aspect ratio ≈ 1.414 (√2) - same!
        # But A3 is larger in pixels
        
        # Detect paper size based on image dimensions
        # If image is very large (> 3000px on long side), likely A3
        long_side = max(img_width, img_height)
        
        if long_side > 3000 or (img_width > 3000 and img_height > 2000):
            # A3 size
            if is_landscape:
                page_size = landscape(A3)
                logger.info(f"Detected A3 Landscape: {img_width}x{img_height}")
            else:
                page_size = portrait(A3)
                logger.info(f"Detected A3 Portrait: {img_width}x{img_height}")
        else:
            # A4 size (default)
            if is_landscape:
                page_size = landscape(A4)
                logger.info(f"Detected A4 Landscape: {img_width}x{img_height}")
            else:
                page_size = portrait(A4)
                logger.info(f"Detected A4 Portrait: {img_width}x{img_height}")
        
        # Create PDF with detected page size
        c = canvas.Canvas(output_path, pagesize=page_size)
        
        page_width, page_height = page_size
        
        # Calculate scaling to fit page while maintaining aspect ratio
        scale = min(page_width / img_width, page_height / img_height) * 0.95  # 95% to leave margin
        
        new_width = img_width * scale
        new_height = img_height * scale
        
        # Center the image
        x = (page_width - new_width) / 2
        y = (page_height - new_height) / 2
        
        # Draw image
        img_reader = ImageReader(BytesIO(image_data))
        c.drawImage(img_reader, x, y, width=new_width, height=new_height)
        
        c.save()
        logger.info(f"Created PDF: {output_path} with page size {page_width:.0f}x{page_height:.0f}pt")
        
    except Exception as e:
        logger.error(f"Error creating PDF: {e}")
        raise


@api_router.post("/retry-scan")
async def retry_scan(
    scan_id: str,
    current_user: dict = Depends(require_approved_user)
):
    """Retry scanning a failed document"""
    try:
        # DEBUG: Log query
        logger.info(f"Retry scan for id: {scan_id}")
        
        # Get the failed scan from database
        failed_scan = await db.scan_results.find_one({"id": scan_id})
        
        if not failed_scan:
            total_docs = await db.scan_results.count_documents({})
            logger.error(f"Scan not found. Total docs: {total_docs}")
            raise HTTPException(status_code=404, detail=f"Scan not found (searched in {total_docs} documents)")
        
        if failed_scan.get('short_code') != 'ERROR':
            raise HTTPException(status_code=400, detail="Document is not in error state")
        
        # Check if we have the image
        image_base64 = failed_scan.get('image_base64')
        if not image_base64:
            raise HTTPException(status_code=400, detail="No image data to retry")
        
        # Decode image and retry scan
        import base64
        image_bytes = base64.b64decode(image_base64)
        
        # Create cropped image for OCR (35% crop, 1024px)
        cropped_image_base64 = resize_image_for_api(image_bytes, crop_top_only=True, max_size=1024)
        
        # Retry analysis with Vision API
        analysis_result = await analyze_document_with_vision(cropped_image_base64)
        
        # Update database with new result
        update_result = await db.scan_results.update_one(
            {"id": scan_id},
            {"$set": {
                "detected_type": analysis_result["detected_full_name"],
                "detected_full_name": analysis_result["detected_full_name"],
                "short_code": analysis_result["short_code"],
                "confidence_score": analysis_result["confidence"]
            }}
        )
        
        if update_result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update scan result")
        
        return {
            "message": "Retry successful",
            "detected_type": analysis_result["detected_full_name"],
            "short_code": analysis_result["short_code"],
            "confidence": analysis_result["confidence"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying scan {scan_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/scan-document", response_model=ScanResult)
async def scan_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_approved_user)
):
    """Scan a single document and detect type"""
    try:
        # Read file content
        content = await file.read()
        
        # DETECT ASPECT RATIO FROM ORIGINAL IMAGE FIRST (before any resize)
        img_original = Image.open(BytesIO(content))
        img_width, img_height = img_original.size
        aspect_ratio = img_width / img_height
        
        logger.info(f"Original image: {img_width}x{img_height}, aspect ratio: {aspect_ratio:.2f}")
        
        # If aspect ratio > 1.35, likely 2-page horizontal spread or wide format (like GCN cũ)
        # Lowered from 1.5 to 1.35 to catch more 2-page documents
        if aspect_ratio > 1.35:
            # 2-page spread or wide format: Title may be at 40-60%, use 65% crop
            crop_percent = 0.65
            logger.info(f"→ Detected 2-page/wide format (aspect {aspect_ratio:.2f}) → Using 65% crop")
        else:
            # Single page portrait: 50% crop sufficient
            crop_percent = 0.50
            logger.info(f"→ Detected single page (aspect {aspect_ratio:.2f}) → Using 50% crop")
        
        # Create FULL image for preview/storage (AFTER detection)
        full_image_base64 = resize_image_for_api(content, crop_top_only=False, max_size=1280)
        
        # Crop and analyze with detected percentage
        cropped_image_base64 = resize_image_for_api(content, crop_top_only=True, max_size=800, crop_percentage=crop_percent)
        analysis_result = await analyze_document_with_vision(cropped_image_base64)
        
        # Create scan result with FULL image for preview
        scan_result = ScanResult(
            original_filename=file.filename,
            detected_type=analysis_result["detected_full_name"],
            detected_full_name=analysis_result["detected_full_name"],
            short_code=analysis_result["short_code"],
            confidence_score=analysis_result["confidence"],
            image_base64=full_image_base64,  # Store full image
            user_id=current_user.get("id")
        )
        
        # Save to database
        doc = scan_result.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.scan_results.insert_one(doc)
        
        return scan_result
        
    except Exception as e:
        logger.error(f"Error scanning document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def apply_smart_grouping(results: List[ScanResult]) -> List[ScanResult]:
    """
    Smart grouping: STRICT mode - QUY TẮC MỚI
    
    Logic mới (theo yêu cầu):
    - Trang có tiêu đề KHỚP CHÍNH XÁC 100% với bảng quy tắc → Tài liệu mới
    - Trang KHÔNG có tiêu đề (UNKNOWN, confidence < 0.3) → Trang tiếp theo của tài liệu trước
    - CHỈ KHI thấy tiêu đề MỚI khớp 100% → Mới chuyển sang loại mới
    
    Ví dụ:
    - Trang 1: "GIẤY CHỨNG NHẬN" (khớp 100%) → GCN trang 1
    - Trang 2: Không có tiêu đề → GCN trang 2 (vẫn là GCN)
    - Trang 3: "BẢN MÔ TẢ" (khớp 100%) → BMT trang 1 (tài liệu mới!)
    - Trang 4: Không có tiêu đề → BMT trang 2
    """
    if not results:
        return results
    
    grouped = []
    last_valid_code = None
    last_valid_name = None
    continuation_count = 0
    
    for i, result in enumerate(results):
        # Skip error results
        if result.short_code == "ERROR":
            grouped.append(result)
            continuation_count = 0
            continue
        
        # QUY TẮC MỚI: Coi là "không có tiêu đề" nếu:
        # 1. short_code = "UNKNOWN" (AI không nhận diện được)
        # 2. confidence < 0.3 (AI không chắc chắn)
        # 3. Có chữ "không rõ" hoặc "unknown" trong tên
        is_continuation = (
            result.short_code == "UNKNOWN" or 
            result.confidence_score < 0.3 or
            "không rõ" in result.detected_full_name.lower() or
            "unknown" in result.detected_full_name.lower()
        )
        
        if is_continuation and last_valid_code:
            # Trang này không có tiêu đề → Vẫn thuộc tài liệu trước
            continuation_count += 1
            logger.info(f"Page {i+1} ({result.original_filename}) → Tiếp tục {last_valid_code} (trang {continuation_count + 1})")
            
            grouped.append(ScanResult(
                id=result.id,
                original_filename=result.original_filename,
                detected_type=f"{last_valid_name} (trang {continuation_count + 1})",
                detected_full_name=f"{last_valid_name} (trang {continuation_count + 1})",
                short_code=last_valid_code,
                confidence_score=0.95,  # High confidence for grouped pages
                image_base64=result.image_base64,
                user_id=result.user_id,
                session_id=result.session_id,  # Keep session_id
                timestamp=result.timestamp
            ))
        elif is_continuation and not last_valid_code:
            # Trang đầu tiên không có tiêu đề → Giữ nguyên UNKNOWN
            logger.info(f"Page {i+1} ({result.original_filename}) → Không rõ (không có tài liệu trước)")
            grouped.append(result)
        else:
            # Trang này có tiêu đề KHỚP 100% → Tài liệu mới!
            last_valid_code = result.short_code
            last_valid_name = result.detected_full_name
            continuation_count = 0
            
            # Đánh dấu là trang 1
            logger.info(f"Page {i+1} ({result.original_filename}) → Tài liệu mới: {result.detected_full_name} (trang 1)")
            grouped.append(ScanResult(
                id=result.id,
                original_filename=result.original_filename,
                detected_type=f"{result.detected_full_name} (trang 1)",
                detected_full_name=f"{result.detected_full_name} (trang 1)",
                short_code=result.short_code,
                confidence_score=result.confidence_score,
                image_base64=result.image_base64,
                user_id=result.user_id,
                session_id=result.session_id,  # Keep session_id
                timestamp=result.timestamp
            ))
    
    return grouped


@api_router.post("/batch-scan", response_model=List[ScanResult])
async def batch_scan(
    files: List[UploadFile] = File(...),
    previous_results: Optional[str] = Form(None),  # JSON string of previous batch results
    current_user: dict = Depends(require_approved_user)
):
    """
    Scan multiple documents - OPTIMIZED for 50+ files with controlled concurrency
    
    Args:
        files: Files to scan
        previous_results: JSON string of previous scan results (for continuation across batches)
        current_user: Current authenticated user
    """
    try:
        # Parse previous results if provided
        previous_scan_results = []
        if previous_results:
            try:
                import json
                prev_data = json.loads(previous_results)
                previous_scan_results = [ScanResult(**item) for item in prev_data]
                logger.info(f"Received {len(previous_scan_results)} previous results for continuation")
            except Exception as e:
                logger.warning(f"Failed to parse previous_results: {e}")
        
        # Generate session ID for this batch scan
        session_id = f"scan_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        logger.info(f"Starting batch scan with session_id: {session_id}")
        
        # Semaphore to limit concurrent API calls (avoid rate limits and timeout)
        # Use lower concurrency in production to avoid infrastructure timeouts
        MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT_SCANS", "2"))  # Default 2 for deployed env
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        async def process_file(file, current_user_dict, session_id, file_index, retry_count=0):
            async with semaphore:  # Control concurrency
                max_retries = 2
                try:
                    # Read file content
                    content = await file.read()
                    
                    # DETECT ASPECT RATIO FROM ORIGINAL IMAGE FIRST
                    img_original = Image.open(BytesIO(content))
                    img_width, img_height = img_original.size
                    aspect_ratio = img_width / img_height
                    
                    # 2-page spread or wide format needs more crop (lowered threshold to 1.35)
                    crop_percent = 0.65 if aspect_ratio > 1.35 else 0.50
                    
                    # Create FULL image for preview (AFTER detection)
                    full_image_base64 = resize_image_for_api(content, max_size=1280, crop_top_only=False)
                    
                    cropped_image_base64 = resize_image_for_api(content, max_size=800, crop_top_only=True, crop_percentage=crop_percent)
                    analysis_result = await analyze_document_with_vision(cropped_image_base64)
                    
                    # Create scan result with FULL image for display
                    scan_result = ScanResult(
                        original_filename=file.filename,
                        detected_type=analysis_result["detected_full_name"],
                        detected_full_name=analysis_result["detected_full_name"],
                        short_code=analysis_result["short_code"],
                        confidence_score=analysis_result["confidence"],
                        image_base64=full_image_base64,  # Store full image
                        user_id=current_user_dict.get("id") if current_user_dict else None,
                        session_id=session_id  # Add session ID
                    )
                    
                    return (file_index, scan_result)  # Return with index
                except Exception as e:
                    error_msg = str(e)
                    
                    # Auto retry for timeout/connection errors
                    is_retryable = ("timeout" in error_msg.lower() or 
                                   "connection" in error_msg.lower() or
                                   "rate limit" in error_msg.lower())
                    
                    if is_retryable and retry_count < max_retries:
                        logger.warning(f"Retrying {file.filename} (attempt {retry_count + 1}/{max_retries})")
                        await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                        return await process_file(file, current_user_dict, session_id, file_index, retry_count + 1)
                    
                    logger.error(f"Error processing {file.filename}: {error_msg}", exc_info=True)
                    
                    # Categorize error
                    if "rate limit" in error_msg.lower():
                        error_type = "Rate Limit"
                        error_detail = "Quá nhiều request. Đã thử retry."
                    elif "timeout" in error_msg.lower():
                        error_type = "Timeout"
                        error_detail = f"API phản hồi quá lâu. Đã thử {retry_count + 1} lần."
                    elif "json" in error_msg.lower():
                        error_type = "JSON Parse Error"
                        error_detail = "AI trả về dữ liệu không đúng format."
                    elif "connection" in error_msg.lower():
                        error_type = "Connection Error"
                        error_detail = f"Mất kết nối mạng. Đã thử {retry_count + 1} lần."
                    elif "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                        error_type = "API Key Error"
                        error_detail = "Lỗi xác thực API key."
                    else:
                        error_type = "Unknown Error"
                        error_detail = error_msg[:100]
                    
                    # Return error result with details (with index)
                    return (file_index, ScanResult(
                        original_filename=file.filename,
                        detected_type=f"❌ {error_type}",
                        detected_full_name=error_detail,
                        short_code="ERROR",
                        confidence_score=0.0,
                        image_base64="",
                        user_id=current_user_dict.get("id") if current_user_dict else None,
                        session_id=session_id  # Add session ID even for errors
                    ))
        
        # Process files with controlled concurrency
        # IMPORTANT: Preserve original file order for correct grouping
        tasks = [process_file(file, current_user, session_id, idx) for idx, file in enumerate(files)]
        indexed_results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Sort results by original index to maintain upload order
        # This is CRITICAL for multi-page grouping to work correctly
        indexed_results.sort(key=lambda x: x[0])  # Sort by index
        results = [result for idx, result in indexed_results]  # Extract results only
        
        logger.info(f"Received {len(results)} scan results in correct order")
        
        # SMART GROUPING: Apply continuation logic
        # IMPORTANT: Merge with previous results for cross-batch grouping
        if previous_scan_results:
            logger.info(f"Merging with {len(previous_scan_results)} previous results for continuation")
            all_results = previous_scan_results + results
            grouped_results = apply_smart_grouping(all_results)
            # Return only NEW results (skip previous ones)
            new_grouped_results = grouped_results[len(previous_scan_results):]
        else:
            logger.info("No previous results, applying grouping to current batch only")
            new_grouped_results = apply_smart_grouping(results)
        logger.info("Applying smart grouping for multi-page documents...")
        grouped_results = apply_smart_grouping(results)
        
        # Filter out error results and save valid ones
        valid_results = [r for r in new_grouped_results if r.short_code != "ERROR"]
        
        # Save to database in batch
        if valid_results:
            docs = []
            for result in valid_results:
                doc = result.model_dump()
                doc['timestamp'] = doc['timestamp'].isoformat()
                docs.append(doc)
            
            await db.scan_results.insert_many(docs)
        
        return new_grouped_results
        
    except Exception as e:
        logger.error(f"Error in batch scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/scan-history", response_model=List[ScanResult])
async def get_scan_history(current_user: dict = Depends(require_approved_user)):
    """Get scan history for current user"""
    try:
        # Filter by user_id to only show current user's scans
        user_id = current_user.get("id")
        results = await db.scan_results.find({"user_id": user_id}, {"_id": 0}).sort("timestamp", -1).to_list(1000)
        
        # Convert ISO string timestamps back to datetime objects
        for result in results:
            if isinstance(result['timestamp'], str):
                result['timestamp'] = datetime.fromisoformat(result['timestamp'])
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting scan history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/update-filename")
async def update_filename(
    request: UpdateFilenameRequest,
    current_user: dict = Depends(require_approved_user)
):
    """Update the short code for a scan result - allows duplicate names"""
    try:
        # Validate input
        if not request.new_short_code or not request.new_short_code.strip():
            raise HTTPException(status_code=400, detail="Short code cannot be empty")
        
        # DEBUG: Log query
        logger.info(f"Searching for document with id: {request.id}")
        
        # Check if document exists first - also log count
        total_docs = await db.scan_results.count_documents({})
        logger.info(f"Total documents in collection: {total_docs}")
        
        existing = await db.scan_results.find_one({"id": request.id})
        
        if not existing:
            # DEBUG: Try to find by any field containing this id
            logger.error("Document not found. Searching all docs...")
            sample = await db.scan_results.find({}).limit(2).to_list(2)
            if sample:
                logger.error(f"Sample doc keys: {list(sample[0].keys())}")
            raise HTTPException(status_code=404, detail=f"Document with id {request.id} not found in {total_docs} documents")
        
        # Update the short code (duplicates are allowed)
        update_res = await db.scan_results.update_one(
            {"id": request.id},
            {"$set": {"short_code": request.new_short_code.strip()}}
        )
        
        logger.info(f"Updated filename for {request.id}: {existing.get('short_code')} -> {request.new_short_code}")
        
        return {
            "message": "Filename updated successfully",
            "old_code": existing.get('short_code'),
            "new_code": request.new_short_code.strip()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating filename: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/export-single-document")
async def export_single_document(
    request: ExportPDFRequest,
    current_user: dict = Depends(require_approved_user)
):
    """Export a single document as PDF"""
    try:
        # Get scan result
        result = await db.scan_results.find_one(
            {"id": {"$in": request.scan_ids}},
            {"_id": 0}
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Scan result not found")
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        short_code = result.get('short_code', 'UNKNOWN')
        pdf_path = os.path.join(temp_dir, f"{short_code}.pdf")
        
        # Create PDF
        create_pdf_from_image(
            result['image_base64'],
            pdf_path,
            short_code
        )
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{short_code}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting single document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/export-pdf-single")
async def export_pdf_single(
    request: ExportPDFRequest,
    current_user: dict = Depends(require_approved_user)
):
    """Export scans as PDFs, automatically grouping by short_code"""
    try:
        # Get scan results
        results = await db.scan_results.find(
            {"id": {"$in": request.scan_ids}},
            {"_id": 0}
        ).to_list(1000)
        
        if not results:
            raise HTTPException(status_code=404, detail="No scan results found")
        
        # Group results by short_code
        grouped_results = {}
        for result in results:
            short_code = result.get('short_code', 'UNKNOWN')
            if short_code not in grouped_results:
                grouped_results[short_code] = []
            grouped_results[short_code].append(result)
        
        # Create temp directory for PDFs
        temp_dir = tempfile.mkdtemp()
        pdf_files = []
        
        # Process each group
        for short_code, group in grouped_results.items():
            if len(group) == 1:
                # Single document - create one PDF
                output_path = os.path.join(temp_dir, f"{short_code}.pdf")
                create_pdf_from_image(
                    group[0]['image_base64'],
                    output_path,
                    short_code
                )
                pdf_files.append(output_path)
            else:
                # Multiple documents with same code - merge into one PDF
                temp_pdfs = []
                for idx, result in enumerate(group):
                    temp_path = os.path.join(temp_dir, f"temp_{short_code}_{idx}.pdf")
                    create_pdf_from_image(
                        result['image_base64'],
                        temp_path,
                        f"{short_code}_{idx}"
                    )
                    temp_pdfs.append(temp_path)
                
                # Merge PDFs with same short_code
                merger = PdfMerger()
                for temp_pdf in temp_pdfs:
                    merger.append(temp_pdf)
                
                merged_path = os.path.join(temp_dir, f"{short_code}.pdf")
                merger.write(merged_path)
                merger.close()
                
                # Clean up temp files
                for temp_pdf in temp_pdfs:
                    os.remove(temp_pdf)
                
                pdf_files.append(merged_path)
        
        # Create a zip file with all PDFs
        zip_path = os.path.join(temp_dir, "documents_single.zip")
        import zipfile
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for pdf_file in pdf_files:
                zipf.write(pdf_file, os.path.basename(pdf_file))
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename="documents_single.zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting single PDFs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/export-pdf-merged")
async def export_pdf_merged(
    request: ExportPDFRequest,
    current_user: dict = Depends(require_approved_user)
):
    """Export all scans merged into one PDF"""
    try:
        # Get scan results
        results = await db.scan_results.find(
            {"id": {"$in": request.scan_ids}},
            {"_id": 0}
        ).to_list(1000)
        
        if not results:
            raise HTTPException(status_code=404, detail="No scan results found")
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        pdf_files = []
        
        # Create individual PDFs first
        for idx, result in enumerate(results):
            output_path = os.path.join(temp_dir, f"temp_{idx}.pdf")
            create_pdf_from_image(
                result['image_base64'],
                output_path,
                f"page_{idx}"
            )
            pdf_files.append(output_path)
        
        # Merge PDFs
        merger = PdfMerger()
        for pdf_file in pdf_files:
            merger.append(pdf_file)
        
        # Save merged PDF
        merged_path = os.path.join(temp_dir, "documents_merged.pdf")
        merger.write(merged_path)
        merger.close()
        
        return FileResponse(
            merged_path,
            media_type="application/pdf",
            filename="documents_merged.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting merged PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/clear-history")
async def clear_history(current_user: dict = Depends(require_approved_user)):
    """Clear all scan history"""
    try:
        result = await db.scan_results.delete_many({})
        return {"message": f"Deleted {result.deleted_count} scan results"}
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/rules", response_model=List[DocumentRule])
async def get_rules():
    """Get all document rules"""
    try:
        rules_cursor = db.document_rules.find({})
        rules = await rules_cursor.to_list(length=None)
        
        # Initialize if empty
        if not rules:
            await get_document_rules()  # This will initialize from DOCUMENT_TYPES
            rules_cursor = db.document_rules.find({})
            rules = await rules_cursor.to_list(length=None)
        
        return [DocumentRule(**rule) for rule in rules]
    except Exception as e:
        logger.error(f"Error getting rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/rules", response_model=DocumentRule)
async def create_rule(request: CreateRuleRequest):
    """Create a new document rule - ALLOWS DUPLICATE short_codes"""
    try:
        # REMOVED: No longer check for duplicate short_code
        # Multiple document types can have the same short code
        
        # Create new rule
        new_rule = DocumentRule(
            full_name=request.full_name,
            short_code=request.short_code
        )
        
        # Insert to database
        await db.document_rules.insert_one(new_rule.model_dump())
        
        logger.info(f"Created new rule: {request.full_name} -> {request.short_code}")
        return new_rule
    except Exception as e:
        logger.error(f"Error creating rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/rules/{rule_id}", response_model=DocumentRule)
async def update_rule(rule_id: str, request: UpdateRuleRequest):
    """Update an existing document rule - ALLOWS DUPLICATE short_codes"""
    try:
        # Find existing rule
        existing_rule = await db.document_rules.find_one({"id": rule_id})
        if not existing_rule:
            raise HTTPException(status_code=404, detail="Không tìm thấy quy tắc")
        
        # REMOVED: No longer check for duplicate short_code
        # Multiple document types can have the same short code
        
        # Prepare update data
        update_data = {"updated_at": datetime.now(timezone.utc)}
        if request.full_name:
            update_data["full_name"] = request.full_name
        if request.short_code:
            update_data["short_code"] = request.short_code
        
        # Update in database
        await db.document_rules.update_one(
            {"id": rule_id},
            {"$set": update_data}
        )
        
        # Get updated rule
        updated_rule = await db.document_rules.find_one({"id": rule_id})
        
        logger.info(f"Updated rule {rule_id}: {update_data}")
        return DocumentRule(**updated_rule)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str):
    """Delete a document rule"""
    try:
        # Find existing rule
        existing_rule = await db.document_rules.find_one({"id": rule_id})
        if not existing_rule:
            raise HTTPException(status_code=404, detail="Không tìm thấy quy tắc")
        
        # Delete from database
        result = await db.document_rules.delete_one({"id": rule_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Không thể xóa quy tắc")
        
        logger.info(f"Deleted rule {rule_id}: {existing_rule['full_name']}")
        return {"message": "Đã xóa quy tắc thành công", "deleted_rule": existing_rule['full_name']}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/rules/drop-unique-index")
async def drop_unique_index():
    """Drop unique index on short_code to allow duplicate codes"""
    try:
        # Drop the unique index
        _drop = await db.document_rules.drop_index("short_code_1")
        logger.info("Successfully dropped unique index on short_code")
        return {
            "message": "Đã xóa unique index, giờ có thể thêm mã trùng lặp",
            "index_dropped": "short_code_1"
        }
    except Exception as e:
        error_msg = str(e)
        if "index not found" in error_msg.lower():
            return {
                "message": "Index không tồn tại hoặc đã được xóa rồi",
                "status": "ok"
            }
        logger.error(f"Error dropping index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/rules/cleanup-duplicates")
async def cleanup_duplicate_rules():
    """Remove duplicate rules, keep only unique short_codes - OPTIMIZED"""
    try:
        # Use aggregation pipeline for better performance with large datasets
        pipeline = [
            {
                "$group": {
                    "_id": "$short_code",
                    "ids": {"$push": "$id"},
                    "count": {"$sum": 1}
                }
            },
            {
                "$match": {
                    "count": {"$gt": 1}  # Only groups with duplicates
                }
            }
        ]
        
        duplicates_groups = await db.document_rules.aggregate(pipeline).to_list(length=None)
        
        if not duplicates_groups:
            total_count = await db.document_rules.count_documents({})
            return {
                "message": "Không có quy tắc trùng lặp", 
                "remaining": total_count,
                "deleted": 0
            }
        
        # Collect IDs to delete (keep first, delete rest)
        ids_to_delete = []
        for group in duplicates_groups:
            # Keep first ID, delete the rest
            ids_to_delete.extend(group["ids"][1:])
        
        if ids_to_delete:
            # Delete duplicates in batch
            delete_result = await db.document_rules.delete_many({"id": {"$in": ids_to_delete}})
            deleted_count = delete_result.deleted_count
        else:
            deleted_count = 0
        
        # Get final count
        remaining_count = await db.document_rules.count_documents({})
        
        return {
            "message": f"Đã xóa {deleted_count} quy tắc trùng lặp",
            "deleted": deleted_count,
            "remaining": remaining_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/llm/health", response_model=LlmHealth)
async def llm_health():
    """Lightweight healthcheck for LLM providers."""
    # Check OpenAI first
    openai_ok = False
    emergent_ok = False
    detail_msgs = []

    # OpenAI
    client = get_openai_client()
    if client:
        try:
            resp = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
                temperature=0.2
            )
            openai_ok = True if getattr(resp, 'id', None) else True
        except Exception as e:
            detail_msgs.append(f"openai: {str(e)[:120]}")
    else:
        if OPENAI_API_KEY:
            detail_msgs.append("openai: client init failed")
        else:
            detail_msgs.append("openai: missing OPENAI_API_KEY")

    # Emergent fallback
    if EMERGENT_LLM_KEY:
        try:
            chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"health_{uuid.uuid4()}")\
                .with_model("openai", "gpt-4o")
            msg = UserMessage(text="ping")
            res = await chat.send_message(msg)
            if isinstance(res, str) and len(res) >= 0:
                emergent_ok = True
        except Exception as e:
            detail_msgs.append(f"emergent: {str(e)[:120]}")
    else:
        detail_msgs.append("emergent: missing EMERGENT_LLM_KEY")

    status = "healthy" if openai_ok else ("degraded" if emergent_ok else "unhealthy")
    provider = "openai" if openai_ok else ("emergent" if emergent_ok else "none")

    return LlmHealth(
        status=status,
        provider=provider,
        model=OPENAI_MODEL if openai_ok else ("gpt-4o" if emergent_ok else None),
        openai_available=openai_ok,
        emergent_available=emergent_ok,
        details="; ".join(detail_msgs) if detail_msgs else None
    )


@api_router.get("/")
async def root():
    return {"message": "Document Scanner API"}


@api_router.get("/setup-admin")
async def setup_admin_endpoint():
    """One-time admin setup endpoint - accessible via browser for easy deployment setup
    This will DELETE any existing 'admin' user (including pending ones) and create a fresh admin account
    """
    users_collection = db["users"]
    
    # Delete ALL existing users with username "admin" (including pending ones)
    delete_result = await users_collection.delete_many({"username": "admin"})
    
    # Create fresh admin account
    from auth_utils import PasswordHasher
    admin_password = "Thommit@19"
    hashed = PasswordHasher.hash_password(admin_password)
    
    admin_user = {
        "email": "admin@smartdocscan.com",
        "username": "admin",
        "hashed_password": hashed,
        "full_name": "Admin",
        "roles": ["admin", "user"],
        "status": "approved",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "approved_at": datetime.now(timezone.utc),
        "approved_by": None
    }
    
    result = await users_collection.insert_one(admin_user)
    
    # Create indexes
    try:
        await users_collection.create_index("email", unique=True)
        await users_collection.create_index("username", unique=True)
    except Exception:
        pass  # Indexes may already exist
    
    return {
        "message": "Admin account created successfully (deleted {} existing admin account(s))".format(delete_result.deleted_count),
        "username": "admin",
        "user_id": str(result.inserted_id),
        "deleted_old_accounts": delete_result.deleted_count
    }





# ==================== FOLDER SCANNING FEATURE ====================

SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif'}
MAX_FILES_PER_ZIP = 500
MAX_ZIP_SIZE_MB = 500

# Store active job statuses (in-memory, could use Redis for production)
active_jobs = {}


def extract_zip_and_find_images(zip_file_path: str, extract_to: str) -> dict:
    """
    Extract ZIP and find all image files recursively
    Returns: Dict of {folder_name: [(relative_path, absolute_path)]}
    Groups files by their direct parent folder (or second-level if first is wrapper)
    """
    try:
        # Extract ZIP
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        # Find all images recursively and group by parent folder
        folder_groups = {}
        
        for root, dirs, files in os.walk(extract_to):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                    # Calculate relative path from extract_to
                    relative_path = file_path.relative_to(extract_to)
                    
                    # Get folder name - use the DIRECT parent folder of the image
                    parts = relative_path.parts
                    if len(parts) > 1:
                        # Use the direct parent folder (last folder before file)
                        folder_name = parts[-2] if len(parts) > 1 else parts[0]
                    else:
                        folder_name = "root"  # Files in root
                    
                    if folder_name not in folder_groups:
                        folder_groups[folder_name] = []
                    
                    folder_groups[folder_name].append((str(relative_path), str(file_path)))
        
        total_images = sum(len(files) for files in folder_groups.values())
        logger.info(f"Found {total_images} images in {len(folder_groups)} folders")
        
        # Log folder structure for debugging
        for folder_name, files in folder_groups.items():
            logger.info(f"  Folder '{folder_name}': {len(files)} files")
        
        return folder_groups
        
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="File không phải là ZIP hợp lệ")
    except Exception as e:
        logger.error(f"Error extracting ZIP: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi giải nén ZIP: {str(e)}")


def create_result_zip(file_results: List[FolderScanFileResult], source_dir: str, output_zip_path: str):
    """
    Create result ZIP with PDFs maintaining folder structure
    OPTIMIZED: Use ZIP_STORED (no compression) for faster creation and download
    """
    try:
        # Track PDF names to avoid duplicates
        pdf_name_counter = {}
        
        # Use ZIP_STORED for faster zip creation (no compression)
        # PDFs are already compressed, so this doesn't increase size much
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_STORED) as zip_out:
            for file_result in file_results:
                if file_result.status == "success":
                    # Create unique PDF filename to avoid duplicates
                    base_name = file_result.short_code
                    
                    # Get folder path from relative_path
                    relative_dir = str(Path(file_result.relative_path).parent)
                    if relative_dir == '.':
                        relative_dir = ''
                    
                    # Generate unique filename in this directory
                    dir_key = relative_dir
                    if dir_key not in pdf_name_counter:
                        pdf_name_counter[dir_key] = {}
                    
                    if base_name not in pdf_name_counter[dir_key]:
                        pdf_name_counter[dir_key][base_name] = 1
                        pdf_filename = f"{base_name}.pdf"
                    else:
                        count = pdf_name_counter[dir_key][base_name]
                        pdf_filename = f"{base_name}_{count}.pdf"
                        pdf_name_counter[dir_key][base_name] = count + 1
                    
                    # PDF path in ZIP (maintain folder structure)
                    pdf_path_in_zip = str(Path(relative_dir) / pdf_filename) if relative_dir else pdf_filename
                    
                    # Create PDF in temp file
                    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                    
                    try:
                        # We need to read the original image to create PDF
                        original_image_path = Path(source_dir) / file_result.relative_path
                        
                        with open(original_image_path, 'rb') as img_file:
                            image_bytes = img_file.read()
                            # Convert to base64 for create_pdf_from_image
                            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        
                        create_pdf_from_image(image_base64, temp_pdf.name, file_result.short_code)
                        
                        # Add PDF to result ZIP
                        zip_out.write(temp_pdf.name, pdf_path_in_zip)
                        
                    finally:
                        # Clean up temp PDF
                        temp_pdf.close()
                        if os.path.exists(temp_pdf.name):
                            os.unlink(temp_pdf.name)
        
        logger.info(f"Created result ZIP with {len([f for f in file_results if f.status == 'success'])} PDFs (no compression for faster download)")
        
    except Exception as e:
        logger.error(f"Error creating result ZIP: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi tạo ZIP kết quả: {str(e)}")


@api_router.post("/scan-folder", response_model=FolderScanStartResponse)
async def scan_folder(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_approved_user)
):
    """
    Start folder scan job (returns immediately with job_id)
    - Client polls /api/folder-scan-status/{job_id} for progress
    - Each folder available for download as soon as it completes
    """
    try:
        # Validate file is ZIP
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Chỉ chấp nhận file ZIP")
        
        # Create temp directory for processing
        temp_dir = tempfile.mkdtemp(prefix='folder_scan_')
        upload_dir = os.path.join(temp_dir, 'upload')
        extract_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(extract_dir, exist_ok=True)
        
        # Save uploaded ZIP
        zip_path = os.path.join(upload_dir, file.filename)
        content = await file.read()
        
        # Check file size
        file_size_mb = len(content) / (1024 * 1024)
        if file_size_mb > MAX_ZIP_SIZE_MB:
            raise HTTPException(
                status_code=400, 
                detail=f"File quá lớn ({file_size_mb:.1f}MB). Giới hạn: {MAX_ZIP_SIZE_MB}MB"
            )
        
        with open(zip_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Processing ZIP file: {file.filename} ({file_size_mb:.1f}MB)")
        
        # Extract ZIP and group by folders
        folder_groups = extract_zip_and_find_images(zip_path, extract_dir)
        
        if len(folder_groups) == 0:
            raise HTTPException(status_code=400, detail="Không tìm thấy thư mục nào chứa ảnh")
        
        total_files = sum(len(files) for files in folder_groups.values())
        if total_files > MAX_FILES_PER_ZIP:
            raise HTTPException(
                status_code=400,
                detail=f"Quá nhiều files ({total_files}). Giới hạn: {MAX_FILES_PER_ZIP} files"
            )
        
        # Create job
        job_id = str(uuid.uuid4())
        job_status = FolderScanJobStatus(
            job_id=job_id,
            status="processing",
            total_folders=len(folder_groups),
            completed_folders=0,
            current_folder=None,
            folder_results=[],
            started_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        active_jobs[job_id] = job_status
        
        # Start background task
        asyncio.create_task(process_folder_scan_job(job_id, folder_groups, extract_dir, temp_dir, current_user))
        
        return FolderScanStartResponse(
            job_id=job_id,
            message="Đã bắt đầu quét. Sử dụng status_url để theo dõi tiến trình.",
            total_folders=len(folder_groups),
            total_files=total_files,
            status_url=f"/api/folder-scan-status/{job_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting folder scan: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")


async def process_folder_scan_job(job_id: str, folder_groups: dict, extract_dir: str, temp_dir: str, current_user: dict):
    """Background task to process folder scan"""
    try:
        job_status = active_jobs[job_id]
        
        for folder_idx, (folder_name, image_files) in enumerate(folder_groups.items(), 1):
            folder_start = datetime.now(timezone.utc)
            
            # Update job status
            job_status.current_folder = folder_name
            job_status.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"[Job {job_id}] Processing folder {folder_idx}/{len(folder_groups)}: {folder_name} ({len(image_files)} files)")
            
            # Determine concurrency - Lower for deployed environment to avoid timeouts
            MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT_SCANS", "2"))  # Default 2
            MAX_SIZE = 700 if len(image_files) > 50 else 800
            semaphore = asyncio.Semaphore(MAX_CONCURRENT)
            
            async def process_single_image(relative_path: str, absolute_path: str, max_size: int, current_user_dict: dict, retry_count=0):
                async with semaphore:
                    max_retries = 2
                    try:
                        with open(absolute_path, 'rb') as img_file:
                            image_bytes = img_file.read()
                        
                        img_original = Image.open(BytesIO(image_bytes))
                        img_width, img_height = img_original.size
                        aspect_ratio = img_width / img_height
                        crop_percent = 0.65 if aspect_ratio > 1.35 else 0.50
                        
                        cropped_image_base64 = resize_image_for_api(
                            image_bytes, max_size=max_size, crop_top_only=True, crop_percentage=crop_percent
                        )
                        analysis_result = await analyze_document_with_vision(cropped_image_base64)
                        
                        return FolderScanFileResult(
                            relative_path=relative_path,
                            original_filename=Path(relative_path).name,
                            detected_full_name=analysis_result["detected_full_name"],
                            short_code=analysis_result["short_code"],
                            confidence_score=analysis_result["confidence"],
                            status="success",
                            user_id=current_user_dict.get("id") if current_user_dict else None
                        )
                    except Exception as e:
                        error_msg = str(e)
                        is_retryable = ("timeout" in error_msg.lower() or "connection" in error_msg.lower() or
                                       "rate limit" in error_msg.lower() or "429" in error_msg)
                        
                        if is_retryable and retry_count < max_retries:
                            await asyncio.sleep(2 ** retry_count)
                            return await process_single_image(relative_path, absolute_path, max_size, current_user_dict, retry_count + 1)
                        
                        logger.error(f"Error processing {relative_path}: {e}")
                        return FolderScanFileResult(
                            relative_path=relative_path,
                            original_filename=Path(relative_path).name,
                            detected_full_name="Lỗi",
                            short_code="ERROR",
                            confidence_score=0.0,
                            status="error",
                            error_message=str(e)[:200],
                            user_id=current_user_dict.get("id") if current_user_dict else None
                        )
            
            # Process all images in this folder
            tasks = [process_single_image(rel_path, abs_path, MAX_SIZE, current_user) for rel_path, abs_path in image_files]
            file_results = await asyncio.gather(*tasks)
            
            # Count results
            folder_success = len([r for r in file_results if r.status == "success"])
            folder_error = len([r for r in file_results if r.status == "error"])
            
            # Create result ZIP for this folder IMMEDIATELY
            result_zip_filename = f"{folder_name}.zip"
            result_zip_path = os.path.join(temp_dir, result_zip_filename)
            create_result_zip(file_results, extract_dir, result_zip_path)
            
            # Save to permanent location
            permanent_result_path = os.path.join(ROOT_DIR, 'temp_results', f"{folder_name}_{uuid.uuid4().hex[:8]}.zip")
            os.makedirs(os.path.dirname(permanent_result_path), exist_ok=True)
            shutil.copy(result_zip_path, permanent_result_path)
            
            folder_end = datetime.now(timezone.utc)
            folder_time = (folder_end - folder_start).total_seconds()
            
            # Add to job results IMMEDIATELY (available for download)
            folder_result = FolderBatchResult(
                folder_name=folder_name,
                total_files=len(image_files),
                success_count=folder_success,
                error_count=folder_error,
                processing_time_seconds=folder_time,
                download_url=f"/api/download-folder-result/{os.path.basename(permanent_result_path)}",
                files=file_results
            )
            
            job_status.folder_results.append(folder_result)
            job_status.completed_folders += 1
            job_status.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"[Job {job_id}] Folder {folder_name} complete: {folder_success}/{len(image_files)} success. ZIP ready for download!")
        
        # Mark job as completed
        job_status.status = "completed"
        job_status.current_folder = None
        job_status.updated_at = datetime.now(timezone.utc)
        
        logger.info(f"[Job {job_id}] All folders completed!")
        
        # Cleanup temp dir
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.warning(f"Could not clean up temp dir: {e}")
            
    except Exception as e:
        logger.error(f"[Job {job_id}] Error processing job: {e}", exc_info=True)
        job_status = active_jobs.get(job_id)
        if job_status:
            job_status.status = "error"
            job_status.error_message = str(e)
            job_status.updated_at = datetime.now(timezone.utc)


@api_router.get("/folder-scan-status/{job_id}", response_model=FolderScanJobStatus)
async def get_folder_scan_status(job_id: str):
    """Get status of folder scan job (poll this endpoint)"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job không tồn tại")
    
    return active_jobs[job_id]


@api_router.get("/download-folder-result/{filename}")
async def download_folder_result(filename: str):
    """Download the result ZIP from folder scan"""
    try:
        result_path = os.path.join(ROOT_DIR, 'temp_results', filename)
        
        if not os.path.exists(result_path):
            raise HTTPException(status_code=404, detail="File không tồn tại hoặc đã hết hạn")
        
        return FileResponse(
            result_path,
            media_type="application/zip",
            filename=f"scanned_documents_{filename}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Include the router in the main app
app.include_router(api_router)


# ==================== AUTHENTICATION ENDPOINTS ====================
from auth_models import UserRegisterRequest, UserLoginRequest, TokenResponse
from auth_utils import PasswordHasher, TokenManager

auth_router = APIRouter(prefix="/api/auth", tags=["authentication"])


@auth_router.post("/register", status_code=201)
async def register(user_data: UserRegisterRequest):
    """Register a new user (pending approval)"""
    users_collection = db["users"]
    
    # Check for existing email
    existing_email = await users_collection.find_one({"email": user_data.email.lower()})
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    # Check for existing username  
    existing_username = await users_collection.find_one({"username": user_data.username.lower()})
    if existing_username:
        raise HTTPException(status_code=409, detail="Username already taken")
    
    # Hash password and create user
    hashed_password = PasswordHasher.hash_password(user_data.password)
    new_user = {
        "email": user_data.email.lower(),
        "username": user_data.username.lower(),
        "hashed_password": hashed_password,
        "full_name": user_data.full_name,
        "roles": ["user"],
        "status": "pending",  # pending, approved, disabled
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "approved_at": None,
        "approved_by": None
    }
    
    result = await users_collection.insert_one(new_user)
    
    return {
        "message": "Registration successful. Awaiting admin approval.",
        "user_id": str(result.inserted_id),
        "email": new_user["email"],
        "status": new_user["status"]
    }


@auth_router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLoginRequest):
    """Authenticate user and return access token"""
    users_collection = db["users"]
    
    logger.info(f"Login attempt for username: {login_data.username}")
    
    # Find user
    user = await users_collection.find_one({"username": login_data.username.lower()})
    
    if not user:
        logger.warning(f"User not found: {login_data.username}")
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    logger.info(f"User found: {user['username']}, status: {user['status']}")
    
    # Verify password
    if not PasswordHasher.verify_password(login_data.password, user["hashed_password"]):
        logger.warning(f"Password verification failed for: {user['username']}")
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    # Check user status
    if user["status"] != "approved":
        raise HTTPException(
            status_code=403,
            detail=f"User account is {user['status']}. Please contact admin."
        )
    
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=403,
            detail="User account is disabled"
        )
    
    # Create access token
    access_token = TokenManager.create_access_token(
        data={"sub": str(user["_id"]), "username": user["username"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "full_name": user.get("full_name"),
            "roles": user.get("roles", []),
            "status": user["status"]
        }
    }


@auth_router.get("/me")
async def get_current_user_info(current_user: dict = Depends(require_approved_user)):
    """Get current authenticated user info"""
    return {
        "id": str(current_user["_id"]),
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user.get("full_name"),
        "roles": current_user.get("roles", []),
        "status": current_user["status"],
        "created_at": current_user["created_at"]
    }


# Admin endpoints
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])


@admin_router.get("/users/pending")
async def get_pending_users(admin: dict = Depends(require_admin)):
    """List all pending users awaiting approval"""
    users_collection = db["users"]
    pending_users = await users_collection.find({"status": "pending"}).to_list(None)
    
    return [
        {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "full_name": user.get("full_name"),
            "created_at": user["created_at"]
        }
        for user in pending_users
    ]


@admin_router.get("/users/all")
async def get_all_users(admin: dict = Depends(require_admin)):
    """List all users"""
    users_collection = db["users"]
    all_users = await users_collection.find({}).to_list(None)
    
    return [
        {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "full_name": user.get("full_name"),
            "roles": user.get("roles", []),
            "status": user["status"],
            "is_active": user.get("is_active", True),
            "created_at": user["created_at"]
        }
        for user in all_users
    ]


@admin_router.post("/users/approve/{user_id}")
async def approve_user(user_id: str, admin: dict = Depends(require_admin)):
    """Approve a pending user"""
    users_collection = db["users"]
    
    result = await users_collection.find_one_and_update(
        {"_id": ObjectId(user_id), "status": "pending"},
        {
            "$set": {
                "status": "approved",
                "approved_at": datetime.now(timezone.utc),
                "approved_by": str(admin["_id"]),
                "updated_at": datetime.now(timezone.utc)
            }
        },
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found or not in pending status")
    
    return {
        "message": "User approved successfully",
        "user_id": str(result["_id"]),
        "status": result["status"]
    }


@admin_router.post("/users/disable/{user_id}")
async def disable_user(user_id: str, admin: dict = Depends(require_admin)):
    """Disable a user account"""
    users_collection = db["users"]
    
    result = await users_collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "is_active": False,
                "status": "disabled",
                "updated_at": datetime.now(timezone.utc)
            }
        },
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User disabled successfully"}


@admin_router.post("/users/enable/{user_id}")
async def enable_user(user_id: str, admin: dict = Depends(require_admin)):
    """Enable a user account"""
    users_collection = db["users"]
    
    result = await users_collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "is_active": True,
                "status": "approved",
                "updated_at": datetime.now(timezone.utc)
            }
        },
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User enabled successfully"}


app.include_router(auth_router)
app.include_router(admin_router)


# ==================== END AUTHENTICATION ====================


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()