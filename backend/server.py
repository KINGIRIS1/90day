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
from reportlab.lib.pagesizes import A4
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


async def analyze_document_with_vision(image_base64: str) -> dict:
    """Analyze document using OpenAI Vision API"""
    try:
        # Create a mapping list for the prompt
        doc_types_list = "\n".join([f"- {full_name}: {code}" for full_name, code in DOCUMENT_TYPES.items()])
        
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
        
        # Create user message with OPTIMIZED prompt - focus on title only
        prompt = f"""Đọc tiêu đề tài liệu (thường ở dòng 5-7) và xác định CHÍNH XÁC loại.

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
1. Đọc tiêu đề đầy đủ
2. Tìm trong danh sách có tên CHÍNH XÁC 100%?
3. NẾU CÓ → Trả về tên + mã chính xác, confidence: 0.9
4. NẾU KHÔNG → Trả về "CONTINUATION", confidence: 0.1

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
            # Try to extract JSON manually if it's embedded in text
            import re
            json_match = re.search(r'\{[^}]+\}', response_text)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise je
        
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


def resize_image_for_api(image_bytes: bytes, max_size: int = 1280, crop_top_only: bool = True) -> str:
    """Resize image and convert to base64 - OPTIMAL: 20% crop for lines 5-7"""
    try:
        img = Image.open(BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # CROP: Take top 20% (lines 5-7 where title usually is)
        if crop_top_only:
            width, height = img.size
            crop_height = int(height * 0.20)  # Back to 20% - optimal for title only
            img = img.crop((0, 0, width, crop_height))
            logger.info(f"Cropped image from {height}px to {crop_height}px (top 20%, lines 5-7)")
        
        # High quality resize for better OCR
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # High quality
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=80, optimize=True)  # Increased to 80%
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return img_base64
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        raise


def create_pdf_from_image(image_base64: str, output_path: str, filename: str):
    """Create a PDF file from base64 image"""
    try:
        # Decode base64 image
        image_data = base64.b64decode(image_base64)
        img = Image.open(BytesIO(image_data))
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Create PDF
        c = canvas.Canvas(output_path, pagesize=A4)
        
        # Calculate dimensions to fit A4
        a4_width, a4_height = A4
        img_width, img_height = img.size
        
        # Calculate scaling to fit A4 while maintaining aspect ratio
        scale = min(a4_width / img_width, a4_height / img_height) * 0.9
        
        new_width = img_width * scale
        new_height = img_height * scale
        
        # Center the image
        x = (a4_width - new_width) / 2
        y = (a4_height - new_height) / 2
        
        # Draw image
        img_reader = ImageReader(BytesIO(image_data))
        c.drawImage(img_reader, x, y, width=new_width, height=new_height)
        
        c.save()
        
    except Exception as e:
        logger.error(f"Error creating PDF: {e}")
        raise


@api_router.post("/retry-scan")
async def retry_scan(scan_id: str):
    """Retry scanning a failed document"""
    try:
        # Get the failed scan from database
        failed_scan = await db.scan_results.find_one({"id": scan_id})
        
        if not failed_scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        if failed_scan.get('short_code') != 'ERROR':
            raise HTTPException(status_code=400, detail="Document is not in error state")
        
        # Check if we have the image
        image_base64 = failed_scan.get('image_base64')
        if not image_base64:
            raise HTTPException(status_code=400, detail="No image data to retry")
        
        # Decode image and retry scan
        import base64
        image_bytes = base64.b64decode(image_base64)
        
        # Create cropped image for OCR
        cropped_image_base64 = resize_image_for_api(image_bytes, crop_top_only=True, max_size=1280)
        
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
        
        # Create FULL image for preview/storage
        full_image_base64 = resize_image_for_api(content, crop_top_only=False, max_size=1536)
        
        # Create CROPPED image for OCR (faster!)
        cropped_image_base64 = resize_image_for_api(content, crop_top_only=True, max_size=1280)
        
        # Analyze with Vision API using CROPPED image
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
    Smart grouping: Trang không có tiêu đề sẽ được gán cùng tên với trang trước đó
    
    Quy tắc:
    - File có tiêu đề rõ (confidence > 0.7) → Giữ nguyên
    - File không có tiêu đề (CONTINUATION hoặc confidence < 0.3) → Copy tên file trước
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
        
        # Check if this is a continuation page
        is_continuation = (
            result.short_code == "CONTINUATION" or 
            result.confidence_score < 0.3 or
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
        # Semaphore to limit concurrent API calls (avoid rate limits)
        MAX_CONCURRENT = 10  # Process max 10 files at once
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        async def process_file(file, retry_count=0):
            async with semaphore:  # Control concurrency
                max_retries = 2
                try:
                    # Read file content
                    content = await file.read()
                    
                    # Create FULL image for preview
                    full_image_base64 = resize_image_for_api(content, max_size=1536, crop_top_only=False)
                    
                    # Create CROPPED image for OCR (only top 20% - MUCH FASTER!)
                    cropped_image_base64 = resize_image_for_api(content, max_size=1280, crop_top_only=True)
                    
                    # Analyze with Vision API using CROPPED image
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
        
        # Check if document exists first
        existing = await db.scan_results.find_one({"id": request.id})
        if not existing:
            raise HTTPException(status_code=404, detail=f"Document with id {request.id} not found")
        
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