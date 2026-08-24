// import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

// import Home from "./pages/Home";
// import PatientFiles from "./pages/patient/patientFiles";
// import AdminPatients from "./pages/admin/AdminPatients";
// import AdminPatientDocuments from "./pages/admin/AdminPatientDocuments";
// import PatientDocumentData from "./pages/patient/patientDocumentData";

// function App() {
//   const patientId = 2;

//   return (
//     <BrowserRouter>
//       <Routes>
//         {/* Home */}
//         <Route path="/" element={<Home />} />

//         {/* Patient */}
//         <Route
//           path="/patient/files"
//           element={<PatientFiles patientId={patientId} />}
//         />

//         {/* Patient file data */}
//         <Route
//           path="/patient/files/:documentId"
//           element={<PatientDocumentData />}
//         />

//         {/* Admin */}
//         <Route path="/admin/patients" element={<AdminPatients />} />

//         <Route
//           path="/admin/patients/:patientId/documents"
//           element={<AdminPatientDocuments />}
//         />

//         {/* Unknown route */}
//         <Route path="*" element={<Navigate to="/" replace />} />
//       </Routes>
//     </BrowserRouter>
//   );
// }

// export default App;


import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import Home from "./pages/Home";
import PatientFiles from "./pages/patient/patientFiles";
import PatientDocumentData from "./pages/patient/patientDocumentData";
import AdminPatients from "./pages/admin/AdminPatients";
import AdminPatientDocuments from "./pages/admin/AdminPatientDocuments";

function App() {
  const patientId = 2;

  return (
    <BrowserRouter>
      <Routes>

        {/* Home */}
        <Route
          path="/"
          element={<Home />}
        />

        {/* Patient */}
        <Route
          path="/patient/files"
          element={
            <PatientFiles patientId={patientId} />
          }
        />

        <Route
          path="/patient/files/:documentId"
          element={
            <PatientDocumentData
              patientId={patientId}
            />
          }
        />

        {/* Admin */}
        <Route
          path="/admin/patients"
          element={<AdminPatients />}
        />

        <Route
          path="/admin/patients/:patientId/documents"
          element={<AdminPatientDocuments />}
        />

        {/* Unknown route */}
        <Route
          path="*"
          element={
            <Navigate to="/" replace />
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;