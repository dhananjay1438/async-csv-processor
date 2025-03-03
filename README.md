# *Async CSV Image Processing Service*

This project is an **asynchronous image processing system** built using FastAPI, Celery, Redis, and Firestore. The system processes images provided in a CSV file by compressing them and storing the output URLs.

---

## *Tech Stack*

- **Backend:** FastAPI (Python)
- **Task Queue:** Celery
- **Message Broker:** Redis
- **Database:** Firestore (used for storing product data and processed images)
- **Storage:** Firestore (also used for storing CSV files)
- **Async Processing:** Celery workers for handling image compression

---

## *Features*

✅ Upload CSV file containing product names and input image URLs.  
✅ Asynchronously process images by compressing them to **50% of their original quality**.  
✅ Store processed image URLs in Firestore.  
✅ Provide a **unique request ID** to track processing status.  
✅ Offer a status API to query processing progress.  
✅ Webhook support to notify clients once processing is completed.  

---

## *API Endpoints*

### **1. Upload CSV File**
**Endpoint:** `POST /upload`  
**Description:** Accepts a CSV file, validates it, and returns a unique request ID.  

**Request:**  
- `multipart/form-data`
  - `file`: CSV file with columns:  
    1. Serial Number  
    2. Product Name  
    3. Input Image URLs (comma-separated)

**Response:**  
```json
{
  "request_id": "unique-request-id"
}
```
 **Status Code:**
- `202 Accepted` - Request accepted

### 2. **Check Processing Status**

**Endpoint:**
`GET /status/{request_id}`

**Description:**
Returns the current status of a request, including whether it is still processing, completed, or failed.

**Request Parameters:**   
- `request_id` *(string, path parameter)*: Unique request identifier received during CSV upload.

**Response:**

**Success Response (Processing):**   
```json
{
  "request_id": "unique-request-id",
  "status": "in progress"
}
```
**Success Response (completed):**   

```json
{
  "request_id": "completed",
  "status": "in progress",
  "csv_url": "unique-csv-url"
}
```
 **Status Codes:**
- `200 OK` - Successful response with the current processing status.
- `400 Bad Request` - Invalid request parameters or missing request ID.
- `404 Not Found` - Request ID does not exist.
- `500 Internal Server Error` - Server encountered an error while processing the request.

### **3. Webhook Notification**

**Endpoint:**
`POST /webhook`

**Description:**   
Triggers a webhook notification when image processing is completed. The webhook sends a payload containing the request ID, status, and the URL of the processed CSV file.

**Request Body:**   
- `request_id` *(string, required)*: Unique request identifier.
- `status` *(string, required)*: The processing status, always `"completed"` for this webhook.
- `csv_url` *(string, required)*: URL of the processed CSV file.

**Request Example:**   
```json
{
  "request_id": "unique-request-id",
  "status": "completed",
  "csv_url": "https://firestore-storage-link/output.csv"
}
```
