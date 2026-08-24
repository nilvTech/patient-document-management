import axios from "axios";
import type { Document, ExtractedField } from "../types/document";
import type { Patient } from "../types/patient";

const API_URL = import.meta.env.VITE_API_URL;

const api = axios.create({
  baseURL: API_URL,
});

// Admin get all patients
export const getPatientDocuments = async (
  patientId: number,
): Promise<Document[]> => {
  const response = await api.get<Document[]>(`/patient/${patientId}/documents`);

  return response.data;
};

export const uploadPatientDocuments = async (
  patientId: number,
  files: File[],
): Promise<Document[]> => {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await api.post<Document[]>(
    `/patient/${patientId}/documents`,
    formData,
  );

  return response.data;
};

export const getDocumentFileUrl = (
  patientId: number,
  documentId: number,
): string => {
  return `${API_URL}/patient/${patientId}/documents/${documentId}/file`;
};

// Admin API functions
export const getAdminPatients = async (): Promise<Patient[]> => {
  const response = await api.get<Patient[]>("/admin/patients");

  return response.data;
};

export const getAdminPatientDocuments = async (
  patientId: number,
): Promise<Document[]> => {
  const response = await api.get<Document[]>(
    `/admin/patient/${patientId}/documents`,
  );

  return response.data;
};

export const getExtractedData = async (
  patientId: number,
  documentId: number,
): Promise<ExtractedField[]> => {
  const response = await api.get<ExtractedField[]>(
    `/patient/${patientId}/documents/${documentId}/extracted-data`,
  );
  return response.data;
};

export default api;
