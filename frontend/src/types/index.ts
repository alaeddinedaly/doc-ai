export type DocumentStatus = "pending" | "processing" | "completed" | "failed";

export interface ExtractionData {
  invoice_number?: string | null;
  supplier?: string | null;
  date?: string | null;
  amount_ht?: number | null;
  tva?: number | null;
  amount_ttc?: number | null;
  currency?: string | null;
  confidence_score?: number | null;
}

export interface DocumentItem {
  id: string;
  filename: string;
  status: DocumentStatus;
  mime_type: string;
  file_size: number;
  uploaded_at: string;
  processed_at?: string | null;
  document_type?: string | null;
  extracted_data?: ExtractionData | null;
  confidence_scores?: Record<string, number> | null;
}

