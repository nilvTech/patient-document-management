import { useState, type ChangeEvent } from "react";

interface DocumentUploadProps {
  onUpload: (files: File[]) => Promise<void>;
  uploading: boolean;
}

const DocumentUpload = ({ onUpload, uploading }: DocumentUploadProps) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [validationError, setValidationError] = useState("");

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    setValidationError("");

    if (!files || files.length === 0) {
      setSelectedFiles([]);
      return;
    }

    const fileArray = Array.from(files);

    // const invalid = fileArray.filter(
    //   (file) => !file.name.toLowerCase().endsWith(".pdf"),
    // );
    const allowedExtensions = [
      ".pdf",
      ".doc",
      ".docx",
      ".xls",
      ".xlsx",
      ".ppt",
      ".pptx",
      ".jpg",
      ".jpeg",
      ".png",
      ".webp",
      ".csv",
      ".txt",
      ".html",
      ".htm",
      ".xml",
      ".json",
      ".rtf",
    ];

    const invalid = fileArray.filter((file) => {
      const extension = file.name
        .substring(file.name.lastIndexOf("."))
        .toLowerCase();

      return !allowedExtensions.includes(extension);
    });

    if (invalid.length > 0) {
      // setValidationError(
      //   `Please upload a valid file format (PDF only). Rejected: ${invalid
      //     .map((f) => f.name)
      //     .join(", ")}`,
      // );
      setValidationError(
        `Unsupported file format. Rejected: ${invalid
          .map((f) => f.name)
          .join(", ")}`,
      );
      setSelectedFiles(fileArray.filter((f) => !invalid.includes(f)));
      return;
    }

    setSelectedFiles(fileArray);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;
    try {
      await onUpload(selectedFiles);
      setSelectedFiles([]);
    } catch (error) {
      console.error("Upload failed:", error);
    }
  };

  return (
    <div className="document-upload">
      <h2>Upload Documents</h2>

      {/* <input
        type="file"
        accept=".pdf,application/pdf"
        multiple
        onChange={handleFileChange}
        disabled={uploading}
      /> */}
      <input
        type="file"
        accept="
    .pdf,
    .doc,
    .docx,
    .xls,
    .xlsx,
    .ppt,
    .pptx,
    .jpg,
    .jpeg,
    .png,
    .webp,
    .csv,
    .txt,
    .html,
    .htm,
    .xml,
    .json,
    .rtf
  "
        multiple
        onChange={handleFileChange}
        disabled={uploading}
      />

      <p className="supported-file-types">
        Supported formats: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, JPG, JPEG, PNG,
        WEBP, CSV, TXT, HTML, XML, JSON, RTF
      </p>

      {validationError && (
        <div className="error-message">{validationError}</div>
      )}

      {selectedFiles.length > 0 && (
        <div className="selected-files">
          <ul>
            {selectedFiles.map((file) => (
              <li key={`${file.name}-${file.lastModified}`}>{file.name}</li>
            ))}
          </ul>
        </div>
      )}

      <button
        type="button"
        onClick={handleUpload}
        disabled={selectedFiles.length === 0 || uploading}
      >
        {uploading ? "Uploading..." : "Upload Documents"}
      </button>
    </div>
  );
};

export default DocumentUpload;

// import { useState, type ChangeEvent } from "react";

// interface DocumentUploadProps {
//   onUpload: (files: File[]) => Promise<void>;
//   uploading: boolean;
// }

// const DocumentUpload = ({
//   onUpload,
//   uploading,
// }: DocumentUploadProps) => {
//   const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

//   const handleFileChange = (
//     event: ChangeEvent<HTMLInputElement>,
//   ) => {
//     const files = event.target.files;

//     if (!files || files.length === 0) {
//       setSelectedFiles([]);
//       return;
//     }

//     const fileArray = Array.from(files);

//     console.log("Selected files:", fileArray);

//     setSelectedFiles(fileArray);
//   };

//   const handleUpload = async () => {
//     if (selectedFiles.length === 0) {
//       return;
//     }

//     try {
//       await onUpload(selectedFiles);

//       // Clear selected files after successful upload
//       setSelectedFiles([]);
//     } catch (error) {
//       console.error("Upload failed:", error);
//     }
//   };

//   return (
//     <div className="document-upload">
//       <h2>Upload Documents</h2>

//       <input
//         type="file"
//         multiple
//         onChange={handleFileChange}
//         disabled={uploading}
//       />

//       {selectedFiles.length > 0 && (
//         <div className="selected-files">
//           <ul>
//             {selectedFiles.map((file) => (
//               <li
//                 key={`${file.name}-${file.lastModified}`}
//               >
//                 {file.name}
//               </li>
//             ))}
//           </ul>
//         </div>
//       )}

//       <button
//         type="button"
//         onClick={handleUpload}
//         disabled={
//           selectedFiles.length === 0 || uploading
//         }
//       >
//         {uploading
//           ? "Uploading..."
//           : "Upload Documents"}
//       </button>
//     </div>
//   );
// };

// export default DocumentUpload;
