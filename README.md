# **AutoHaven - REST API for Used Car Sales with AI Sales Assistant**

Welcome to **AutoHaven**, a cutting-edge **REST API** designed for a fictional used car sales company. AutoHaven
leverages **OpenAI's GPT-4** as an **AI sales assistant** to craft engaging car descriptions and employs the **Resend
API** to automate professional email communications with potential buyers. This robust system effectively manages used
car data, enhancing both sales and customer engagement.

---

## **Features**

### **AI Sales Assistant**

- Utilize **OpenAI GPT-4** to generate captivating and professional car descriptions.
- Automatically create tailored pros and cons lists for each car to attract buyers.

### **Automated Email Campaigns**

- Send personalized and professional emails to potential buyers, including car details, descriptions, and pros/cons.
- Ensure reliable and scalable email delivery using the **Resend API**.

### **Used Car Data Management**

- Store and retrieve detailed information about used cars, such as brand, model, year, mileage, price, and more.
- Perform CRUD (Create, Read, Update, Delete) operations on car listings.

### **Image Storage**

- Upload and store car images using **Cloudinary**.
- Generate optimized image URLs for use in emails and listings.

### **RESTful API**

- Simple and intuitive API endpoints for managing cars, generating descriptions, and sending emails.
- Support for pagination, filtering, and sorting of car listings.

### **Error Handling & Logging**

- Robust error handling and logging for all operations.
- Detailed error messages to simplify debugging.

---

## **Technologies Used**

- **Backend Framework**: FastAPI
- **Database**: MongoDB (with Beanie ODM)
- **AI Integration**: OpenAI GPT-4
- **Image Storage**: Cloudinary
- **Email Service**: Resend API
- **Authentication**: JWT (JSON Web Tokens)
- **Logging**: Python `logging` module
- **Environment Management**: Python `dotenv`

---

## **Getting Started**

### **Prerequisites**

- Python 3.9 or higher
- MongoDB instance (local or cloud)
- OpenAI API key
- Resend API key
- Cloudinary API key and cloud name

### **Installation**

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/auto-haven.git
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```env
   MONGODB_URI=your_mongodb_uri
   OPENAI_API_KEY=your_openai_api_key
   RESEND_API_KEY=your_resend_api_key
   CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
   CLOUDINARY_API_KEY=your_cloudinary_api_key
   CLOUDINARY_API_SECRET=your_cloudinary_api_secret
   JWT_SECRET_KEY=your_jwt_secret_key
   ```

4. Run the application:
   ```bash
   uvicorn auto_haven.main:app --reload
   ```

5. Access the API documentation:
   Open your browser and navigate to `http://localhost:8000/docs`.

---

## **API Endpoints**

### **Cars**

- **GET `/cars`**: List all cars (paginated).
- **GET `/cars/{car_id}`**: Get details of a specific car.
- **POST `/cars`**: Create a new car listing.
- **PUT `/cars/{car_id}`**: Update a car listing.
- **DELETE `/cars/{car_id}`**: Delete a car listing.

### **Users**

- **POST `/register`**: Register a new user.
- **POST `/login`**: Log in and receive a JWT token.
- **GET `/me`**: Get details of the currently authenticated user.

---

## **Example Usage**

### **Create a Car Listing**

```bash
curl -X POST "http://localhost:8000/cars" \
     -H "Content-Type: application/json" \
     -d '{
           "brand": "Toyota",
           "model": "Corolla",
           "year": 2020,
           "mileage": 15000,
           "price": 25000,
           "image_url": "https://res.cloudinary.com/your_cloud_name/image/upload/v1234567890/car.jpg"
         }'
```

---

## **Environment Variables**

| Variable                | Description                         | Example Value                     |
|-------------------------|-------------------------------------|-----------------------------------|
| `MONGODB_URI`           | MongoDB connection URI              | `your_mongodb_uri`                |
| `OPENAI_API_KEY`        | OpenAI API key                      | `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `RESEND_API_KEY`        | Resend API key                      | `re_xxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name               | `your_cloud_name`                 |
| `CLOUDINARY_API_KEY`    | Cloudinary API key                  | `your_cloudinary_api_key`         |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret               | `your_cloudinary_api_secret`      |
| `JWT_SECRET_KEY`        | Secret key for JWT token generation | `your_jwt_secret_key`             |

---

## **Acknowledgments**

- **FastAPI** for the fantastic web framework.
- **OpenAI** for the incredible GPT-4 API.
- **Cloudinary** for dependable image storage and optimization.
- **Resend** for reliable email delivery.
- **Beanie ODM** for smooth MongoDB integration.

---
