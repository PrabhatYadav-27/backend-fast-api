````markdown


## 📌 Overview
This project implements a FastAPI-based backend service for consolidating contact information across multiple purchases. The service processes incoming requests containing `email` and `phoneNumber`, identifies related contacts, and maintains a structured contact linkage system.

## 🏡 Code Structure & Functionality

### 1⃣ `main.py` (Entry Point)
- Initializes FastAPI app.
- Defines the `/identify` endpoint.
- Calls necessary functions to process and store contact data.

### 2⃣ Database Setup
- Uses **SQLite** as the database (`contacts.db`).
- `sqlalchemy` is used for ORM-based database interactions.
- `SessionLocal` manages database sessions.

### 3⃣ `Contact` Model (Database Schema)
- `id`: Unique identifier for each contact.
- `phoneNumber`: Phone number of the contact.
- `email`: Email address of the contact.
- `linkedId`: Reference to another contact (if secondary).
- `linkPrecedence`: Specifies whether the contact is `primary` or `secondary`.
- `createdAt`, `updatedAt`, `deletedAt`: Timestamps for record tracking.

### 4⃣ `/identify` Endpoint
- **Request Body:**
```json
{
  "email": "doc@example.com",
  "phoneNumber": "1234567890"
}
```

- **Functionality:**
  1. Checks if the given email or phone number exists in the database.
  2. If no match is found, creates a new **primary contact**.
  3. If a match is found, determines the **primary contact** and links secondary contacts accordingly.
  4. Returns a structured response with `primaryContactId`, `emails`, `phoneNumbers`, and `secondaryContactIds`.
- **Response Example:**

```json
{
  "primaryContactId": 1,
  "emails": ["doc@example.com"],
  "phoneNumbers": ["1234567890"],
  "secondaryContactIds": []
}
```

### 5⃣ Helper Functions

- `format_response(primary_contact, secondary_contacts)`: Formats and returns the JSON response.
  ```python
  def format_response(primary_contact, secondary_contacts):
      return {
          "primaryContactId": primary_contact.id,
          "emails": list(set([c.email for c in [primary_contact] + secondary_contacts if c.email])),
          "phoneNumbers": list(set([c.phoneNumber for c in [primary_contact] + secondary_contacts if c.phoneNumber])),
          "secondaryContactIds": [c.id for c in secondary_contacts]
      }
  ```
- `get_timestamp()`: Returns the current timestamp for database entries.
  ```python
  from datetime import datetime

  def get_timestamp():
      return datetime.utcnow()
  ```

## 🚀 Running the Project

### **1⃣ Install Dependencies**

```bash
pip install fastapi pydantic sqlalchemy uvicorn
```

### **2⃣ Set Up Database**

```bash
python
>>> from main import Base, engine
>>> Base.metadata.create_all(bind=engine)
>>> exit()
```

### **3⃣ Run the Server**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### **4⃣ Test the API**

#### Using `curl`

```bash
curl -X 'POST' 'http://localhost:8000/identify' \
     -H 'Content-Type: application/json' \
     -d '{"email": "doc@example.com", "phoneNumber": "1234567890"}'
```

#### Using `httpie`

```bash
http POST http://localhost:8000/identify email="doc@example.com" phoneNumber="1234567890"
```

#### Using Postman

1. Open Postman.
2. Create a new **POST** request.
3. Set the URL to `http://localhost:8000/identify`.
4. In the **Body** tab, select **raw** and choose **JSON** format.
5. Enter the JSON payload:

   ```json
   {
     "email": "doc@example.com",
     "phoneNumber": "1234567890"
   }
   ```
6. Click **Send** and check the response.



```
```

