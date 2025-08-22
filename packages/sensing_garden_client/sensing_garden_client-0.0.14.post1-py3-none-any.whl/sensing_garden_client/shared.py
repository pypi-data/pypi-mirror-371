"""
Shared utilities for the Sensing Garden client.

This module contains common functionality used across the client components.
"""
import base64
from typing import Dict, Optional, Any


def build_common_params(
    device_id: Optional[str] = None,
    model_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100,
    next_token: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_desc: bool = False
) -> Dict[str, str]:
    """
    Build common query parameters for GET requests.
    
    Args:
        device_id: Optional filter by device ID
        model_id: Optional filter by model ID
        start_time: Optional start time for filtering (ISO-8601)
        end_time: Optional end time for filtering (ISO-8601)
        limit: Maximum number of items to return
        next_token: Token for pagination
        sort_by: Attribute to sort by (e.g., 'timestamp', 'device_id')
        sort_desc: If True, sort in descending order, otherwise ascending
        
    Returns:
        Dictionary with query parameters
    """
    # Build query parameters dictionary with only non-None values
    params = {}
    
    if device_id:
        params['device_id'] = device_id
    if model_id:
        params['model_id'] = model_id
    if start_time:
        params['start_time'] = start_time
    if end_time:
        params['end_time'] = end_time
    if limit:
        params['limit'] = str(limit)
    if next_token:
        params['next_token'] = next_token
    if sort_by:
        if not isinstance(sort_desc, bool):
            raise ValueError("sort_desc must be a boolean value")
        params['sort_by'] = sort_by
        # Always include sort_desc when sort_by is specified
        params['sort_desc'] = str(sort_desc).lower()
    
    return params


def prepare_image_payload(
    device_id: str,
    model_id: str,
    image_data: bytes,
    timestamp: str
) -> Dict[str, Any]:
    """
    Prepare common payload data for API requests with images.
    
    Args:
        device_id: Unique identifier for the device
        model_id: Identifier for the model to use
        image_data: Raw image data as bytes
        timestamp: ISO-8601 formatted timestamp
        
    Returns:
        Dictionary with common payload fields
    """
    if not device_id or not model_id:
        raise ValueError("device_id and model_id must be provided")
    
    if not image_data:
        raise ValueError("image_data cannot be empty")
    
    # Convert image to base64
    base64_image = base64.b64encode(image_data).decode('utf-8')
    
    # Create payload with required fields
    payload = {
        "device_id": device_id,
        "model_id": model_id,
        "image": base64_image,
        "timestamp": timestamp
    }
    
    return payload


def prepare_video_payload(
    device_id: str,
    video_data: bytes,
    description: str,
    timestamp: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Prepare payload data for API requests with videos.
    
    Args:
        device_id: Unique identifier for the device
        video_data: Raw video data as bytes
        description: Description of the video content
        timestamp: ISO-8601 formatted timestamp (optional)
        metadata: Additional metadata about the video (optional)
        
    Returns:
        Dictionary with video payload fields
    """
    if not device_id:
        raise ValueError("device_id must be provided")
    
    if not video_data:
        raise ValueError("video_data cannot be empty")
    
    if not description:
        raise ValueError("description must be provided")
    
    # Convert video to base64
    base64_video = base64.b64encode(video_data).decode('utf-8')
    
    # Create payload with required fields
    payload = {
        "device_id": device_id,
        "video": base64_video,
        "description": description
    }
    
    # Add optional fields if provided
    if timestamp:
        payload["timestamp"] = timestamp
        
    if metadata:
        payload["metadata"] = metadata
    
    return payload


def prepare_multipart_initiate_payload(
    device_id: str,
    content_type: str,
    total_parts: int,
    total_size_bytes: int,
    timestamp: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Prepare payload data for initiating a multipart video upload.
    
    Args:
        device_id: Unique identifier for the device
        content_type: MIME type of the video (e.g., 'video/mp4')
        total_parts: Total number of parts in the multipart upload
        total_size_bytes: Total size of the video in bytes
        timestamp: Optional ISO-8601 timestamp
        metadata: Optional metadata dict
    Returns:
        Payload dict for multipart upload initiation
    """
    if total_parts <= 0:
        raise ValueError("total_parts must be greater than 0")
    
    if total_size_bytes <= 0:
        raise ValueError("total_size_bytes must be greater than 0")
    
    # Create payload with required fields
    payload = {
        "device_id": device_id,
        "content_type": content_type,
        "total_parts": total_parts,
        "total_size_bytes": total_size_bytes
    }
    
    # Add optional fields if provided
    if timestamp:
        payload["timestamp"] = timestamp
    if metadata:
        payload["metadata"] = metadata
    return payload
