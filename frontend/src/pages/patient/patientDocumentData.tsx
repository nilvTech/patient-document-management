import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { getExtractedData, getPatientDocuments } from "../../services/api";
import type { ExtractedField } from "../../types/document";

interface PatientDocumentDataProps {
  patientId: number;
}

const PatientDocumentData = ({ patientId }: PatientDocumentDataProps) => {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();

  const [fields, setFields] = useState<ExtractedField[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [fileName, setFileName] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      if (!documentId) {
        setError("Document ID is missing.");
        setLoading(false);
        return;
      }

      const parsedDocumentId = Number(documentId);

      if (Number.isNaN(parsedDocumentId)) {
        setError("Invalid document ID.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        // Fetch document metadata
        const documents = await getPatientDocuments(patientId);

        const document = documents.find((doc) => doc.id === parsedDocumentId);

        if (!document) {
          setError("Document not found.");
          setFields([]);
          return;
        }

        setFileName(document.file_name.replace(/\.[^/.]+$/, ""));

        // Fetch extracted medical data
        console.log("Fetching extracted data:", {
          patientId,
          documentId: parsedDocumentId,
        });

        const data = await getExtractedData(patientId, parsedDocumentId);

        setFields(data);
      } catch (err) {
        console.error("Failed to load document data:", err);

        setError("Failed to load document data.");
        setFields([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [patientId, documentId]);

  return (
    <div className="patient-files-page">
      <div className="page-header">
        <button
          type="button"
          className="back-button"
          onClick={() => navigate("/patient/files")}
        >
          ← Back to My Files
        </button>

        <h1>Vitals</h1>

        <p>
          Extracted medical data from <strong>{fileName || "document"}</strong>
        </p>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <p>Loading document data...</p>
      ) : fields.length === 0 ? (
        <div className="empty-documents">
          <p>No extracted medical data found.</p>
        </div>
      ) : (
        <div className="patient-table-container">
          <table className="patient-table">
            <thead>
              <tr>
                <th>Field</th>
                <th>Value</th>
                <th>Unit</th>
                <th>Reference Range</th>
                <th>Abnormal</th>
              </tr>
            </thead>

            <tbody>
              {fields.map((field) => (
                <tr key={field.patient_document_data_id}>
                  <td>{field.field_name}</td>
                  <td>{field.field_value ?? "—"}</td>
                  <td>{field.unit ?? "—"}</td>
                  <td>{field.reference_range ?? "—"}</td>
                  <td>
                    {field.is_abnormal === null
                      ? "—"
                      : field.is_abnormal
                        ? "Yes"
                        : "No"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default PatientDocumentData;
