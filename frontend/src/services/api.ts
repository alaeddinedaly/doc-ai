import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  withCredentials: false,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API error", error);
    return Promise.reject(error);
  },
);

export const uploadDocuments = (files: File[]) => {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  return api.post("/api/v1/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const fetchDocuments = (params?: Record<string, string | number>) =>
  api.get("/api/v1/documents", { params }).then((res) => res.data);

export const fetchDocument = (id: string) =>
  api.get(`/api/v1/documents/${id}`).then((res) => res.data);

export const updateExtraction = (id: string, payload: unknown) =>
  api.patch(`/api/v1/documents/${id}/extracted-data`, payload).then((res) => res.data);

export const fetchTask = (taskId: string) =>
  api.get(`/api/v1/tasks/${taskId}`).then((res) => res.data);

export default api;

