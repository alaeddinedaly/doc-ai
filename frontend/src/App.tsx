import { useMemo, useState } from "react";
import { UploadZone } from "./components/UploadZone";
import { DocumentList } from "./components/DocumentList";
import { DocumentViewer } from "./components/DocumentViewer";
import { DocumentItem } from "./types";

function App() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [selected, setSelected] = useState<DocumentItem | null>(null);

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <p className="text-sm uppercase tracking-[0.4em] text-slate-500">Mobelite</p>
            <h1 className="text-2xl font-bold">DOC-IA Control Center</h1>
          </div>
          <button className="px-4 py-2 text-sm rounded-full border border-slate-800 text-slate-300 hover:text-white">
            Export
          </button>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-6 py-8 space-y-8">
        <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-8">
          <UploadZone onUploaded={() => setRefreshKey((key) => key + 1)} />
          <DocumentList onSelect={setSelected} refreshKey={refreshKey} />
        </div>
        <DocumentViewer document={selected} />
      </main>
    </div>
  );
}

export default App;
