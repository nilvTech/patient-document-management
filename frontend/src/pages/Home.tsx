import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="home-page">
      <div className="home-container">
        <h1>Patient Document Management</h1>

        <p className="home-subtitle">
          Select your role to continue
        </p>

        <div className="role-cards">
          <div className="role-card">
            <h2>Patient</h2>

            <p>
              Upload and view your medical documents
            </p>

            <button
              type="button"
              onClick={() => navigate("/patient/files")}
            >
              Continue as Patient
            </button>
          </div>

          <div className="role-card">
            <h2>Admin</h2>

            <p>
              View patients and their uploaded documents
            </p>

            <button
              type="button"
              onClick={() => navigate("/admin/patients")}
            >
              Continue as Admin
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;