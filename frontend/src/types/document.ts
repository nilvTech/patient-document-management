export type ExtractionStatus = "pending" | "processing" | "completed" | "failed";

export interface Document {
  id: number;
  patient_id: number;
  file_name: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
  extraction_status: ExtractionStatus;
  extraction_error?: string | null;
}

export interface ExtractedField {
  patient_document_data_id: number;
  patient_document_id: number;
  field_name: string;
  field_value: string | null;
  unit: string | null;
  reference_range: string | null;
  is_abnormal: boolean | null;
  display_order: number | null;
}









// export interface Document {
//     id:number;
//     patient_id:number;
//     file_name:number;
//     file_type:number;
//     file_size:number;
//     uploaded_at:number;
// }