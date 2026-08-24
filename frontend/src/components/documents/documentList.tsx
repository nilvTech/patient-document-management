import type { Document } from "../../types/document";
import DocumentItem from "./documentItem";

interface DocumentListProps {
  documents: Document[];
}

const DocumentList = ({ documents }: DocumentListProps) => {
  if (documents.length === 0) {
    return (
      <div className="empty-documents">
        <p>No documents uploaded yet.</p>
      </div>
    );
  }

  return (
    <div className="document-list">
      {documents.map((document) => (
        <DocumentItem
          key={document.id}
          document={document}
        />
      ))}
    </div>
  );
};

export default DocumentList;