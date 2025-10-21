from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
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
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

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
class ScanResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_filename: str
    detected_type: str
    detected_full_name: str
    short_code: str
    confidence_score: float
    image_base64: str
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


async def get_document_rules() -> dict:
    """Get all document rules from database or initialize from DOCUMENT_TYPES"""
    try:
        # Create unique index on short_code to prevent duplicates
        try:
            await db.document_rules.create_index("short_code", unique=True)
        except:
            pass  # Index already exists
        
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


async def analyze_document_with_vision(image_base64: str) -> dict:
    """Analyze document using OpenAI Vision API with dynamic rules from database"""
    try:
        # Get document rules from database
        document_rules = await get_document_rules()
        
        # Create a mapping list for the prompt
        doc_types_list = "\n".join([f"- {full_name}: {code}" for full_name, code in document_rules.items()])
        
        # Initialize LlmChat with precision focus
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"doc_scan_{uuid.uuid4()}",
            system_message="""Bạn là AI chuyên gia phân loại tài liệu đất đai Việt Nam.
            NHIỆM VỤ: Đọc CHÍNH XÁC từng từ trong tiêu đề, phân biệt các loại giấy tờ tương tự.
            LƯU Ý: Nhiều loại tài liệu chỉ khác nhau 1-2 từ (ví dụ: "biến động" vs không có).
            Trả về JSON với tên và mã CHÍNH XÁC từ danh sách."""
        ).with_model("openai", "gpt-4o")  # gpt-4o for precision
        
        # Create image content
        image_content = ImageContent(image_base64=image_base64)
        
        # Create user message with OPTIMIZED prompt - focus on quốc huy + title
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
✅ CHỈ chọn khi khớp CHÍNH XÁC 100% với danh sách

NẾU KHÔNG CHẮC CHẮN 100% → Trả về "CONTINUATION" (trang tiếp theo của tài liệu trước)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CÁC CẶP DỄ NHẦM - PHẢI KHỚP CHÍNH XÁC:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. "Đơn đăng ký BIẾN ĐỘNG đất đai" → DDKBD (PHẢI có "BIẾN ĐỘNG")
   "Đơn đăng ký đất đai" → DDK (KHÔNG có "BIẾN ĐỘNG")
   Nếu không rõ có "BIẾN ĐỘNG" không → "CONTINUATION"

2. "Hợp đồng CHUYỂN NHƯỢNG" → HDCQ (PHẢI có "CHUYỂN NHƯỢNG")
   "Hợp đồng THUÊ" → HDTD (PHẢI có "THUÊ")
   "Hợp đồng THẾ CHẤP" → HDTHC (PHẢI có "THẾ CHẤP")
   Nếu không rõ loại nào → "CONTINUATION"

3. "Quyết định CHO PHÉP chuyển mục đích" → QDCMD (PHẢI có "CHO PHÉP")
   Nếu không thấy "CHO PHÉP" rõ ràng → "CONTINUATION"

DANH SÁCH ĐẦY ĐỦ (khớp chính xác):
{doc_types_list}

QUY TRÌNH KIỂM TRA:
━━━━━━━━━━━━━━━━━━
1. Tìm quốc huy Việt Nam (nếu có → tài liệu chính thức)
2. Đọc tiêu đề đầy đủ
3. Tìm trong danh sách có tên CHÍNH XÁC 100%?
4. NẾU CÓ → Trả về tên + mã chính xác, confidence: 0.9
5. NẾU KHÔNG → Trả về "CONTINUATION", confidence: 0.1

TRẢ VỀ JSON:
{{
  "detected_full_name": "Tên CHÍNH XÁC từ danh sách HOẶC 'Không có tiêu đề'",
  "short_code": "MÃ CHÍNH XÁC HOẶC 'CONTINUATION'",
  "confidence": 0.9 hoặc 0.1
}}

❗ NHỚ: Thà trả về "CONTINUATION" còn hơn đoán sai!"""
        
        user_message = UserMessage(
            text=prompt,
            file_contents=[image_content]
        )
        
        # Send message and get response
        response = await chat.send_message(user_message)
        
        # Parse JSON response
        import json
        # Extract JSON from response (handle markdown code blocks)
        response_text = response.strip()
        
        # Log raw response for debugging
        logger.info(f"OpenAI Vision raw response: {response_text[:200]}")
        
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Try to parse JSON
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as je:
            logger.error(f"JSON parse error. Raw response: {response_text}")
            
            # Check if OpenAI refused due to content policy
            if "can't help" in response_text.lower() or "sorry" in response_text.lower():
                logger.warning("OpenAI refused to analyze - likely due to face detection. Returning CONTINUATION.")
                return {
                    "detected_full_name": "Không có tiêu đề",
                    "short_code": "CONTINUATION",
                    "confidence": 0.1
                }
            
            # Try to extract JSON manually if it's embedded in text
            import re
            json_match = re.search(r'\{[^}]+\}', response_text)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # If all fails, return CONTINUATION instead of ERROR
                logger.error("Cannot parse response, returning CONTINUATION")
                return {
                    "detected_full_name": "Không có tiêu đề",
                    "short_code": "CONTINUATION",
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
async def retry_scan(scan_id: str):
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
async def scan_document(file: UploadFile = File(...)):
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
            image_base64=full_image_base64  # Store full image
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
    Smart grouping: STRICT mode - chỉ nhóm khi không có tiêu đề rõ ràng
    
    Quy tắc NGHIÊM NGẶT:
    - File có tiêu đề CHÍNH XÁC (confidence > 0.8) → Tài liệu mới
    - File KHÔNG có tiêu đề (CONTINUATION hoặc confidence < 0.2) → Trang tiếp theo
    - File lỗi (ERROR) → Giữ nguyên
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
        
        # STRICT: Only treat as continuation if very low confidence
        is_continuation = (
            result.short_code == "CONTINUATION" or 
            result.confidence_score < 0.2 or  # Increased threshold from 0.3 to 0.2
            "không có tiêu đề" in result.detected_full_name.lower()
        )
        
        if is_continuation and last_valid_code:
            # This is a continuation page - use previous document's name
            continuation_count += 1
            logger.info(f"Page {i+1} ({result.original_filename}) identified as continuation of {last_valid_code} (page {continuation_count + 1})")
            
            grouped.append(ScanResult(
                id=result.id,
                original_filename=result.original_filename,
                detected_type=f"{last_valid_name} (trang {continuation_count + 1})",
                detected_full_name=f"{last_valid_name} (trang {continuation_count + 1})",
                short_code=last_valid_code,
                confidence_score=0.95,  # High confidence for grouped pages
                image_base64=result.image_base64,
                timestamp=result.timestamp
            ))
        else:
            # This is a new document with clear title
            last_valid_code = result.short_code
            last_valid_name = result.detected_full_name
            continuation_count = 0
            
            # Mark as page 1 if it has good confidence
            if result.confidence_score > 0.7:
                grouped.append(ScanResult(
                    id=result.id,
                    original_filename=result.original_filename,
                    detected_type=f"{result.detected_full_name} (trang 1)",
                    detected_full_name=f"{result.detected_full_name} (trang 1)",
                    short_code=result.short_code,
                    confidence_score=result.confidence_score,
                    image_base64=result.image_base64,
                    timestamp=result.timestamp
                ))
            else:
                grouped.append(result)
    
    return grouped


@api_router.post("/batch-scan", response_model=List[ScanResult])
async def batch_scan(files: List[UploadFile] = File(...)):
    """Scan multiple documents - OPTIMIZED for 50+ files with controlled concurrency"""
    try:
        # Semaphore to limit concurrent API calls (avoid rate limits and timeout)
        MAX_CONCURRENT = 5  # Reduced from 10 to 5 to avoid timeout
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        async def process_file(file, retry_count=0):
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
                        image_base64=full_image_base64  # Store full image
                    )
                    
                    return scan_result
                except Exception as e:
                    error_msg = str(e)
                    
                    # Auto retry for timeout/connection errors
                    is_retryable = ("timeout" in error_msg.lower() or 
                                   "connection" in error_msg.lower() or
                                   "rate limit" in error_msg.lower())
                    
                    if is_retryable and retry_count < max_retries:
                        logger.warning(f"Retrying {file.filename} (attempt {retry_count + 1}/{max_retries})")
                        await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                        return await process_file(file, retry_count + 1)
                    
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
                    
                    # Return error result with details
                    return ScanResult(
                        original_filename=file.filename,
                        detected_type=f"❌ {error_type}",
                        detected_full_name=error_detail,
                        short_code="ERROR",
                        confidence_score=0.0,
                        image_base64=""
                    )
        
        # Process files with controlled concurrency
        tasks = [process_file(file) for file in files]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # SMART GROUPING: Apply continuation logic
        logger.info("Applying smart grouping for multi-page documents...")
        grouped_results = apply_smart_grouping(results)
        
        # Filter out error results and save valid ones
        valid_results = [r for r in grouped_results if r.short_code != "ERROR"]
        
        # Save to database in batch
        if valid_results:
            docs = []
            for result in valid_results:
                doc = result.model_dump()
                doc['timestamp'] = doc['timestamp'].isoformat()
                docs.append(doc)
            
            await db.scan_results.insert_many(docs)
        
        return grouped_results
        
    except Exception as e:
        logger.error(f"Error in batch scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/scan-history", response_model=List[ScanResult])
async def get_scan_history():
    """Get all scan history"""
    try:
        results = await db.scan_results.find({}, {"_id": 0}).sort("timestamp", -1).to_list(1000)
        
        # Convert ISO string timestamps back to datetime objects
        for result in results:
            if isinstance(result['timestamp'], str):
                result['timestamp'] = datetime.fromisoformat(result['timestamp'])
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting scan history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/update-filename")
async def update_filename(request: UpdateFilenameRequest):
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
            logger.error(f"Document not found. Searching all docs...")
            sample = await db.scan_results.find({}).limit(2).to_list(2)
            if sample:
                logger.error(f"Sample doc keys: {list(sample[0].keys())}")
            raise HTTPException(status_code=404, detail=f"Document with id {request.id} not found in {total_docs} documents")
        
        # Update the short code (duplicates are allowed)
        result = await db.scan_results.update_one(
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
async def export_single_document(request: ExportPDFRequest):
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
async def export_pdf_single(request: ExportPDFRequest):
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
async def export_pdf_merged(request: ExportPDFRequest):
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
async def clear_history():
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
            ids_to_delete.extend(group['ids'][1:])
        
        # Delete in batches to avoid timeout
        BATCH_SIZE = 100
        total_deleted = 0
        
        for i in range(0, len(ids_to_delete), BATCH_SIZE):
            batch = ids_to_delete[i:i+BATCH_SIZE]
            result = await db.document_rules.delete_many({"id": {"$in": batch}})
            total_deleted += result.deleted_count
            logger.info(f"Deleted batch {i//BATCH_SIZE + 1}: {result.deleted_count} rules")
        
        remaining_count = await db.document_rules.count_documents({})
        logger.info(f"Cleanup complete: deleted {total_deleted} duplicates, {remaining_count} remaining")
        
        return {
            "message": f"Đã xóa {total_deleted} quy tắc trùng lặp",
            "remaining": remaining_count,
            "deleted": total_deleted
        }
            
    except Exception as e:
        logger.error(f"Error cleaning duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/")
async def root():
    return {"message": "Document Scanner API"}


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