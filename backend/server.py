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
from pypdf import PdfMerger
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
        
        # Initialize LlmChat
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"doc_scan_{uuid.uuid4()}",
            system_message="""Bạn là một AI chuyên gia về tài liệu đất đai Việt Nam. 
            Nhiệm vụ của bạn là phân tích hình ảnh tài liệu và xác định chính xác loại tài liệu.
            Trả lời CHÍNH XÁC theo format JSON được yêu cầu."""
        ).with_model("openai", "gpt-4o")
        
        # Create image content
        image_content = ImageContent(image_base64=image_base64)
        
        # Create user message with detailed prompt
        prompt = f"""Phân tích hình ảnh tài liệu này và xác định loại tài liệu từ danh sách sau:

{doc_types_list}

Yêu cầu:
1. Đọc kỹ nội dung tiêu đề, tiêu đề chính của tài liệu
2. So sánh với danh sách trên và tìm loại tài liệu khớp nhất
3. Trả lời CHỈ dưới dạng JSON với format:
{{
  "detected_full_name": "Tên đầy đủ loại tài liệu",
  "short_code": "Mã viết tắt",
  "confidence": 0.95
}}

Lưu ý: confidence từ 0.0 đến 1.0 thể hiện độ tin cậy của kết quả."""
        
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
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        
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


def resize_image_for_api(image_bytes: bytes, max_size: int = 2048) -> str:
    """Resize image and convert to base64"""
    try:
        img = Image.open(BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Resize if too large
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=85)
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


@api_router.post("/scan-document", response_model=ScanResult)
async def scan_document(file: UploadFile = File(...)):
    """Scan a single document and detect type"""
    try:
        # Read file content
        content = await file.read()
        
        # Resize and convert to base64
        image_base64 = resize_image_for_api(content)
        
        # Analyze with Vision API
        analysis_result = await analyze_document_with_vision(image_base64)
        
        # Create scan result
        scan_result = ScanResult(
            original_filename=file.filename,
            detected_type=analysis_result["detected_full_name"],
            detected_full_name=analysis_result["detected_full_name"],
            short_code=analysis_result["short_code"],
            confidence_score=analysis_result["confidence"],
            image_base64=image_base64
        )
        
        # Save to database
        doc = scan_result.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.scan_results.insert_one(doc)
        
        return scan_result
        
    except Exception as e:
        logger.error(f"Error scanning document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/batch-scan", response_model=List[ScanResult])
async def batch_scan(files: List[UploadFile] = File(...)):
    """Scan multiple documents at once"""
    try:
        results = []
        
        for file in files:
            # Read file content
            content = await file.read()
            
            # Resize and convert to base64
            image_base64 = resize_image_for_api(content)
            
            # Analyze with Vision API
            analysis_result = await analyze_document_with_vision(image_base64)
            
            # Create scan result
            scan_result = ScanResult(
                original_filename=file.filename,
                detected_type=analysis_result["detected_full_name"],
                detected_full_name=analysis_result["detected_full_name"],
                short_code=analysis_result["short_code"],
                confidence_score=analysis_result["confidence"],
                image_base64=image_base64
            )
            
            # Save to database
            doc = scan_result.model_dump()
            doc['timestamp'] = doc['timestamp'].isoformat()
            await db.scan_results.insert_one(doc)
            
            results.append(scan_result)
        
        return results
        
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
    """Update the short code for a scan result"""
    try:
        result = await db.scan_results.update_one(
            {"id": request.id},
            {"$set": {"short_code": request.new_short_code}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Scan result not found")
        
        return {"message": "Filename updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating filename: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/export-pdf-single")
async def export_pdf_single(request: ExportPDFRequest):
    """Export each scan as individual PDF"""
    try:
        # Get scan results
        results = await db.scan_results.find(
            {"id": {"$in": request.scan_ids}},
            {"_id": 0}
        ).to_list(1000)
        
        if not results:
            raise HTTPException(status_code=404, detail="No scan results found")
        
        # Create temp directory for PDFs
        temp_dir = tempfile.mkdtemp()
        pdf_files = []
        
        for result in results:
            short_code = result.get('short_code', 'UNKNOWN')
            output_path = os.path.join(temp_dir, f"{short_code}.pdf")
            
            # Create PDF
            create_pdf_from_image(
                result['image_base64'],
                output_path,
                short_code
            )
            pdf_files.append(output_path)
        
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