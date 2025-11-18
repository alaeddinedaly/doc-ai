import { useCallback, useMemo, useState } from "react";
import { useDropzone } from "react-dropzone";
import clsx from "clsx";
import { uploadDocuments } from "../services/api";

const MAX_SIZE = 50 * 1024 * 1024;
const ACCEPTED = { "application/pdf": [], "image/png": [], "image/jpeg": [] };

interface UploadZoneProps {
  onUploaded: () => void;
}

export function UploadZone({ onUploaded }: UploadZoneProps) {
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      setError(null);
      if (!acceptedFiles.length) {
        return;
      }
      try {
        await uploadDocuments(acceptedFiles);
        setProgress(100);
        onUploaded();
      } catch (err) {
        setError("Upload failed. Please try again.");
      } finally {
        setTimeout(() => setProgress(0), 1500);
      }
    },
    [onUploaded],
  );

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: ACCEPTED,
    maxSize: MAX_SIZE,
    maxFiles: 10,
  });

  const previews = useMemo(
    () =>
      acceptedFiles.map((file) => (
        <div key={file.name} className="text-sm text-slate-300">
          {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
        </div>
      )),
    [acceptedFiles],
  );

  return (
    <section>
      <div
        {...getRootProps()}
        className={clsx(
          "border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition",
          isDragActive ? "border-sky-400 bg-slate-800" : "border-slate-600 bg-slate-900",
        )}
      >
        <input {...getInputProps()} />
        <p className="text-lg font-semibold">Drop invoices here, or click to select</p>
        <p className="text-sm text-slate-400">
          PDF, PNG, JPG — up to 50MB per file, max 10 files per batch.
        </p>
      </div>
      {progress > 0 && (
        <div className="mt-4 h-2 bg-slate-700 rounded-full">
          <div
            className="h-full bg-sky-500 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
      {error && <p className="text-red-400 mt-2">{error}</p>}
      <div className="mt-4 space-y-1">{previews}</div>
    </section>
  );
}

