import { useEffect, useState } from "react";
import { fetchDocument, updateExtraction } from "../services/api";
import { DocumentItem, ExtractionData } from "../types";

interface DocumentViewerProps {
  document: DocumentItem | null;
}

export function DocumentViewer({ document }: DocumentViewerProps) {
  const [data, setData] = useState<ExtractionData | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [ocrText, setOcrText] = useState("");

  useEffect(() => {
    const load = async () => {
      if (!document) return;
      const full = await fetchDocument(document.id);
      setData(full.extracted_data ?? null);
      setOcrText(full.ocr_text ?? "");
    };
    load();
  }, [document]);

  if (!document) {
    return <p className="text-slate-400">Select a document to inspect.</p>;
  }

  const handleSave = async () => {
    if (!data) return;
    await updateExtraction(document.id, { extracted_data: data });
    setMessage("Saved corrections.");
    setTimeout(() => setMessage(null), 2000);
  };

  return (
    <div className="bg-slate-900 rounded-xl p-4 border border-slate-800">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h3 className="text-xl font-semibold">{document.filename}</h3>
          <p className="text-sm text-slate-400">{document.document_type ?? "Unknown"}</p>
        </div>
        <button
          className="px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-sm font-semibold"
          onClick={handleSave}
        >
          Save changes
        </button>
      </div>
      {message && <p className="text-emerald-400 text-sm mb-2">{message}</p>}
      <div className="grid md:grid-cols-2 gap-4">
        <section>
          <p className="text-sm text-slate-500 mb-2">PDF preview</p>
          <div className="bg-slate-800 rounded-lg h-64 flex items-center justify-center text-slate-500">
            PDF viewer placeholder
          </div>
        </section>
        <section>
          <p className="text-sm text-slate-500 mb-2">Extracted fields</p>
          <div className="space-y-3">
            {Object.entries(data ?? {}).map(([key, value]) => (
              <label key={key} className="block">
                <span className="text-xs uppercase text-slate-400">{key}</span>
                <input
                  className="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
                  value={value ?? ""}
                  onChange={(event) =>
                    setData((prev) => ({ ...(prev ?? {}), [key]: event.target.value }))
                  }
                />
              </label>
            ))}
          </div>
        </section>
      </div>
      <section className="mt-6">
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm text-slate-500">Full OCR text</p>
          <span className="text-xs text-slate-500">
            {ocrText ? `${ocrText.length} chars` : "No OCR data"}
          </span>
        </div>
        <textarea
          className="w-full h-48 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 resize-none"
          value={ocrText}
          readOnly
        />
      </section>
    </div>
  );
}

