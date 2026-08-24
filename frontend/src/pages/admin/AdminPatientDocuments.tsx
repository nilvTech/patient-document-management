import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import DocumentList from "../../components/documents/documentList";
import { getAdminPatientDocuments } from "../../services/api";
import type { Document } from "../../types/document";

const AdminPatientDocuments = () => {
  const { patientId } = useParams();
  const navigate = useNavigate();

  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDocuments = async () => {
      if (!patientId) {
        setError("Patient ID is missing.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const data =
          await getAdminPatientDocuments(
            Number(patientId),
          );

        setDocuments(data);
      } catch (error) {
        console.error(
          "Failed to load patient documents:",
          error,
        );

        setError(
          "Failed to load patient documents.",
        );
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, [patientId]);

  return (
    <div className="admin-page">
      <div className="page-header">
        <button
          type="button"
          className="back-button"
          onClick={() => navigate("/admin/patients")}
        >
          ← Back to Patients
        </button>

        <h1>Patient Documents</h1>

        <p>
          Documents uploaded by patient #{patientId}
        </p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <section className="documents-section">
        {loading ? (
          <p>Loading documents...</p>
        ) : (
          <DocumentList documents={documents} />
        )}
      </section>
    </div>
  );
};

export default AdminPatientDocuments;