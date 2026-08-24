import { useEffect, useState } from "react";

import DocumentList from "../../components/documents/documentList";
import DocumentUpload from "../../components/documents/documentUpload";
import {
  getPatientDocuments,
  uploadPatientDocuments,
} from "../../services/api";
import type { Document } from "../../types/document";

interface PatientFilesProps {
  patientId: number;
}

const PatientFiles = ({ patientId }: PatientFilesProps) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getPatientDocuments(patientId);

      console.log("Documents API response:", data);
      console.log("Is array:", Array.isArray(data));

      if (Array.isArray(data)) {
        setDocuments(data);
      } else {
        console.error("Unexpected documents response:", data);
        setDocuments([]);
        setError("Invalid documents response from server.");
      }
    } catch (err) {
      console.error("Failed to load documents:", err);

      setError(err?.response?.data?.detail ?? "Failed to upload documents.");
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [patientId]);

  const handleUpload = async (files: File[]) => {
    try {
      setUploading(true);
      setError("");

      await uploadPatientDocuments(patientId, files);

      await fetchDocuments();
    } catch (err) {
      console.error("Failed to upload documents:", err);

      setError("Failed to upload documents.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="patient-files-page">

      {error && <div className="error-message">{error}</div>}

      <DocumentUpload onUpload={handleUpload} uploading={uploading} />

      <section className="documents-section">
        <h2>My Documents</h2>

        {loading ? (
          <p>Loading documents...</p>
        ) : (
          <DocumentList documents={documents} />
        )}
      </section>
    </div>
  );
};

export default PatientFiles;
