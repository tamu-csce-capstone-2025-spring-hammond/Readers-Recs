// src/api.js
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

console.log("Using backend URL:", BACKEND_URL);
export default BACKEND_URL;
