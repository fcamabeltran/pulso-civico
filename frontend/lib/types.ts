export type Proposal = {
  id: number;
  candidate_id: number;
  axis: string;
  title: string;
  content: string;
  source_name: string;
  source_url: string;
};

export type PromiseItem = {
  id: number;
  candidate_id: number;
  title: string;
  description: string;
  status: "cumplida" | "pendiente" | "incumplida" | "parcial";
  source_name: string;
  source_url: string;
  evidence_note?: string | null;
};

export type Candidate = {
  id: number;
  name: string;
  party: string;
  region: string;
  office?: string | null;
  biography?: string | null;
  metadata?: {
    election_year?: number;
    photo_url?: string | null;
    party_logo_url?: string | null;
    summary_pdf_url?: string | null;
    full_plan_pdf_url?: string | null;
    local_full_plan_path?: string | null;
    local_summary_path?: string | null;
    imported_from?: string | null;
    source_article?: string | null;
    hoja_vida_id?: number | null;
    hoja_vida_url?: string | null;
    local_hoja_vida_path?: string | null;
    hoja_vida_summary?: {
      experiencia_laboral_registros?: number;
      sentencias_penales_registros?: number;
      sentencias_civiles_registros?: number;
      declaracion_bienes_registros?: number;
    } | null;
    [key: string]: unknown;
  } | null;
};

export type CandidateDetail = Candidate & {
  proposals: Proposal[];
  promises: PromiseItem[];
};

export type SearchResult = {
  candidate_id: number;
  candidate_name: string;
  party: string;
  axis: string;
  title: string;
  snippet: string;
  source_name: string;
  source_url: string;
};

export type CompareResponse = {
  left_candidate: Candidate;
  right_candidate: Candidate;
  left_proposals: Proposal[];
  right_proposals: Proposal[];
  insights?: {
    differences: string;
    coincidences: string;
    detail: string;
    evidence_gaps: string;
  } | null;
};

export type ChatSource = {
  candidate_name: string;
  axis: string;
  title: string;
  source_name: string;
  source_url: string;
  excerpt: string;
  page_number?: number | null;
};

export type ChatStructuredResponse = {
  summary: string;
  findings: string[];
  evidence_gaps: string[];
  inferences: string[];
  follow_ups: string[];
};

export type ChatResponse = {
  answer: string;
  sources: ChatSource[];
  provider: string;
  evidence_found: boolean;
  structured?: ChatStructuredResponse | null;
};

export type SimplifyResponse = {
  simplified: string;
  provider: string;
};

export type FormulaCandidate = {
  id_cargo: number;
  cargo: string;
  nombre: string;
  foto_url: string;
  dni: string;
  posicion: number;
};

export type PresidentialFormula = {
  id: number;
  nombre_partido: string;
  logo_url: string;
  candidatos: FormulaCandidate[];
};

export type FormulaMemberSummary = {
  id: number;
  organization_id: number;
  party_name: string;
  party_slug: string;
  candidate_name: string;
  office: string;
  position: number;
  photo_url?: string | null;
  party_logo_url?: string | null;
  hoja_vida_url?: string | null;
  annual_income_total?: number | null;
  public_income_total?: number | null;
  private_income_total?: number | null;
  movable_assets_count: number;
  immovable_assets_count: number;
  assets_declared_value?: number | null;
  labor_records_count: number;
  elected_offices_count: number;
  party_roles_count: number;
  university_education_count: number;
  postgraduate_records_count: number;
  penal_sentences_count: number;
  civil_sentences_count: number;
  obligations_count: number;
  additional_notes_count: number;
  marginal_annotations_count: number;
  summary?: string | null;
};

export type FormulaProfile = {
  organization_id: number;
  party_name: string;
  party_slug: string;
  members: FormulaMemberSummary[];
};

export type EducationRecord = {
  institution: string;
  degree: string;
  completed: boolean;
  year?: string | null;
  comment?: string | null;
};

export type WorkExperienceRecord = {
  organization: string;
  position: string;
  year_from?: string | null;
  year_to?: string | null;
  country?: string | null;
};

export type ElectedOfficeRecord = {
  party: string;
  office: string;
  year_from?: string | null;
  year_to?: string | null;
  comment?: string | null;
};

export type SentenceRecord = {
  description: string;
  year?: string | null;
  comment?: string | null;
};

export type AssetRecord = {
  description: string;
  value?: number | null;
  location?: string | null;
};

export type FormulaMemberDetail = FormulaMemberSummary & {
  university_education: EducationRecord[];
  postgraduate_education: EducationRecord[];
  work_experience: WorkExperienceRecord[];
  elected_offices: ElectedOfficeRecord[];
  party_roles: { party: string; role: string; year_from?: string | null; year_to?: string | null }[];
  penal_sentences: SentenceRecord[];
  civil_sentences: SentenceRecord[];
  immovable_assets: AssetRecord[];
  movable_assets: AssetRecord[];
};
