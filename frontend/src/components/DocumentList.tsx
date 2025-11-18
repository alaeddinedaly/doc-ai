import { useQuery } from "@tanstack/react-query";
import { fetchDocuments } from "../services/api";
import { DocumentItem } from "../types";

interface DocumentListProps {
  onSelect: (doc: DocumentItem) => void;
  refreshKey: number;
}

export function DocumentList({ onSelect, refreshKey }: DocumentListProps) {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["documents", refreshKey],
    queryFn: () => fetchDocuments(),
  });

  if (isLoading) {
    return <p className="text-slate-400">Loading documents...</p>;
  }

  const documents: DocumentItem[] = data?.data ?? [];
  return (
    <div className="bg-slate-900 rounded-xl border border-slate-800">
      <div className="px-4 py-3 border-b border-slate-800 flex justify-between items-center">
        <h3 className="text-lg font-semibold">Documents</h3>
        <button
          className="text-sm text-sky-400 hover:text-sky-300"
          onClick={() => refetch()}
        >
          Refresh
        </button>
      </div>
      <div className="divide-y divide-slate-800">
        {documents.map((doc) => (
          <button
            key={doc.id}
            onClick={() => onSelect(doc)}
            className="w-full flex justify-between px-4 py-3 hover:bg-slate-800 text-left"
          >
            <div>
              <p className="font-medium">{doc.filename}</p>
              <p className="text-xs text-slate-400">
                {doc.document_type ?? "Unknown"} • {doc.status}
              </p>
            </div>
            <span className="text-xs text-slate-500">
              {(doc.file_size / 1024).toFixed(0)} KB
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

