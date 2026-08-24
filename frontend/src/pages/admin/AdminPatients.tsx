import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import PatientTable from "../../components/admin/patientTable";
import { getAdminPatients } from "../../services/api";
import type { Patient } from "../../types/patient";

const AdminPatients = () => {
  const navigate = useNavigate();

  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        setLoading(true);
        setError("");

        const data = await getAdminPatients();

        setPatients(data);
      } catch (error) {
        console.error(
          "Failed to load patients:",
          error,
        );

        setError("Failed to load patients.");
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
  }, []);

  const handleViewDocuments = (patientId: number) => {
    navigate(
      `/admin/patients/${patientId}/documents`,
    );
  };

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1>Patients</h1>

        <p>
          View patients and their uploaded documents.
        </p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <section className="patients-section">
        {loading ? (
          <p>Loading patients...</p>
        ) : (
          <PatientTable
            patients={patients}
            onViewDocuments={handleViewDocuments}
          />
        )}
      </section>
    </div>
  );
};

export default AdminPatients;