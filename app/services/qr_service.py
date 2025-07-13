import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
import json
from typing import Dict, Any
from loguru import logger
import aiofiles
import os
from app.core.config import settings


async def generate_qr_code(data: Dict[str, Any]) -> str:
    """Generate QR code for purchase data and return URL"""
    
    try:
        # Convert data to JSON string
        qr_data = json.dumps(data, ensure_ascii=False)
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Generate filename
        purchase_code = data.get('purchase_code', 'unknown')
        filename = f"qr_{purchase_code}_{data.get('purchase_id', 'unknown')}.png"
        
        # Ensure upload directory exists
        upload_dir = settings.UPLOAD_FOLDER
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(buffer.getvalue())
        
        # Return URL (in production, this would be a proper URL)
        qr_url = f"/uploads/{filename}"
        
        logger.info(f"QR code generated: {qr_url}")
        return qr_url
        
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        raise


def decode_qr_data(qr_data_string: str) -> Dict[str, Any]:
    """Decode QR code data string back to dictionary"""
    try:
        return json.loads(qr_data_string)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding QR data: {str(e)}")
        raise ValueError("Invalid QR code data")


async def validate_qr_code(qr_code_data: str) -> Dict[str, Any]:
    """Validate QR code data and return parsed information"""
    
    try:
        data = decode_qr_data(qr_code_data)
        
        # Validate required fields
        required_fields = ['purchase_id', 'purchase_code', 'user_id', 'branch_id', 'items']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate items structure
        if not isinstance(data['items'], list) or len(data['items']) == 0:
            raise ValueError("Items must be a non-empty list")
        
        for item in data['items']:
            item_required = ['name', 'waste_type_id', 'waste_type_name', 'waste_type_category']
            for field in item_required:
                if field not in item:
                    raise ValueError(f"Missing required item field: {field}")
        
        logger.info(f"QR code validated for purchase: {data['purchase_code']}")
        return data
        
    except Exception as e:
        logger.error(f"QR code validation failed: {str(e)}")
        raise


async def generate_redemption_qr(redemption_code: str, reward_data: Dict[str, Any]) -> str:
    """Generate QR code for reward redemption"""
    
    qr_data = {
        "type": "reward_redemption",
        "redemption_code": redemption_code,
        "reward_id": reward_data.get("reward_id"),
        "reward_name": reward_data.get("reward_name"),
        "user_id": reward_data.get("user_id"),
        "expires_at": reward_data.get("expires_at")
    }
    
    return await generate_qr_code(qr_data)
