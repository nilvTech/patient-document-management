import { useNavigate } from "react-router-dom";
import type { Document } from "../../types/document";

interface DocumentItemProps {
  document: Document;
}

const statusLabels: Record<
  Document["extraction_status"],
  string
> = {
  pending: "Pending",
  processing: "Processing…",
  completed: "Data extracted",
  failed: "Extraction failed",
};

const DocumentItem = ({
  document,
}: DocumentItemProps) => {
  const navigate = useNavigate();

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleString();
  };

  const handleView = () => {
    navigate(`/patient/files/${document.id}`);
  };

  return (
    <div className="document-item">
      <div className="document-info">
        <h3>{document.file_name.replace(/\.[^/.]+$/, "")}</h3>

        <div className="document-meta">
          <span>{document.file_type}</span>

          <span>
            {formatFileSize(document.file_size)}
          </span>

          <span>
            {formatDate(document.uploaded_at)}
          </span>

          <span>
            {statusLabels[document.extraction_status]}
          </span>
        </div>

        {document.extraction_status === "failed" &&
          document.extraction_error && (
            <div className="error-message">
              {document.extraction_error}
            </div>
          )}
      </div>

      <button
        type="button"
        className="document-view-button"
        onClick={handleView}
        disabled={
          document.extraction_status !== "completed"
        }
      >
        View
      </button>
    </div>
  );
};

export default DocumentItem;