import type { Patient } from "../../types/patient";

interface PatientTableProps {
  patients: Patient[];
  onViewDocuments: (patientId: number) => void;
}

const PatientTable = ({
  patients,
  onViewDocuments,
}: PatientTableProps) => {
  if (patients.length === 0) {
    return (
      <div className="empty-patients">
        <p>No patients found.</p>
      </div>
    );
  }

  return (
    <div className="patient-table-container">
      <table className="patient-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Patient Name</th>
            <th>Email</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {patients.map((patient) => (
            <tr key={patient.id}>
              <td>{patient.id}</td>

              <td>{patient.name}</td>

              <td>{patient.email}</td>

              <td>
                <button
                  type="button"
                  className="view-documents-button"
                  onClick={() =>
                    onViewDocuments(patient.id)
                  }
                >
                  View Documents
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PatientTable;