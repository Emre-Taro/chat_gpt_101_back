# Image Upload API Documentation

## Overview
The image upload API allows users to upload images and get AI-powered analysis using OpenAI's vision capabilities. The API supports multipart/form-data uploads and integrates with the chat system.

## Endpoint
```
POST /{user_id}/{chat_id}/upload_image
```

## Parameters
- `user_id` (path): UUID of the user
- `chat_id` (path): UUID of the chat
- `file` (form): Image file to upload
- `prompt` (form, optional): Custom prompt for image analysis (default: "What do you see in this image?")

## Supported File Types
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

## File Size Limit
- Maximum file size: 10MB

## Request Example
```bash
curl -X POST "http://localhost:8000/{user_id}/{chat_id}/upload_image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg" \
  -F "prompt=Describe what you see in this image"
```

## Response Format
```json
{
  "message": "Image uploaded and processed successfully",
  "file_path": "static/uploads/uuid-filename.jpg",
  "user_message": {
    "messageId": "uuid",
    "chatId": "uuid",
    "userId": "uuid",
    "content": "prompt text",
    "role": "user",
    "imageFilename": "uuid-filename.jpg",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "assistant_message": {
    "messageId": "uuid",
    "chatId": "uuid",
    "userId": null,
    "content": "AI analysis of the image",
    "role": "assistant",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

## Error Responses

### 400 Bad Request
- Invalid file type
- File size too large
- Invalid UUID format

### 404 Not Found
- Chat not found or access denied

### 500 Internal Server Error
- File upload failure
- OpenAI API error
- Database error

## Features

### 1. File Validation
- Validates file type against allowed extensions
- Checks file size (max 10MB)
- Generates unique filenames to prevent conflicts

### 2. User Authentication
- Validates user exists and has access to the chat
- Ensures chat ownership

### 3. AI Integration
- Uses OpenAI's GPT-4o model with vision capabilities
- Supports custom prompts for image analysis
- Handles API errors gracefully

### 4. Database Integration
- Saves user message with image filename
- Saves AI response as assistant message
- Updates chat title for new conversations

### 5. Error Handling
- Comprehensive error handling for all operations
- Detailed error messages for debugging
- Graceful degradation when OpenAI API fails

## Implementation Details

### Vision Message Creation
The API creates vision messages using base64-encoded images:
```python
def create_vision_message(content: str, image_path: str) -> dict:
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": content},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
        ]
    }
```

### Database Schema
The Message model includes an `imageFilename` field to store image references:
```python
class Message(BaseModel):
    # ... other fields
    imageFilename = Column(String, nullable=True)
```

### File Storage
Images are stored in `static/uploads/` directory with UUID-based filenames to prevent conflicts.

## Testing
Use the provided test script to verify functionality:
```bash
python test_image_upload.py
```

## Security Considerations
1. File type validation prevents malicious file uploads
2. File size limits prevent DoS attacks
3. User authentication ensures proper access control
4. UUID-based filenames prevent path traversal attacks

## Dependencies
- FastAPI for API framework
- SQLAlchemy for database operations
- OpenAI Python SDK for AI integration
- Python's built-in base64 for image encoding 