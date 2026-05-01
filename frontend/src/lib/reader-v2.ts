// v0.3 schema 类型 + 工具函数
// 设计原则：原文为主、支架可开关、importance_score 驱动节奏

export type ConfidenceLevel = "high" | "medium" | "low";

export type Note = {
  surface: string;
  type: string;
  modern: string;
  highlight?: string | null;
  confidence?: ConfidenceLevel;
  source_basis?: string;
  sense_id?: string;
};

export type Sentence = {
  sid: string;
  original: string;
  char_start?: number;
  char_end?: number;
  speaker?: string;
  stance?: string;
  notes?: Note[];
};

export type PrereadingInline = {
  topic: string;
  explain: string;
  why_needed?: string;
  confidence?: ConfidenceLevel;
  source_basis?: string;
};

export type HardSentence = {
  anchor: string;
  quote: string;
  trigger?: string;
  reader_block?: string;
  parse?: {
    claim?: string;
    qualifiers?: string;
    contrast_or_target?: string;
  };
  why?: {
    relation?: string;
    explanation?: string;
  };
  implication?: string | null;
  confidence?: ConfidenceLevel;
  source_basis?: string;
};

export type Polemic = {
  is_polemical: boolean;
  target?: string | null;
  their_view?: string | null;
  author_response?: string | null;
  polemic_kind?: string | null;
  confidence?: ConfidenceLevel | null;
};

export type ParagraphGates = {
  needs_prereading?: boolean;
  needs_hard_sentence?: boolean;
  needs_polemic?: boolean;
  prereading_reason?: string;
  hard_sentence_reason?: string;
  polemic_reason?: string;
};

export type Paragraph = {
  n: number;
  original_plain: string;
  original_html?: string | null;
  block_type?: string | null;
  gist?: string | null;
  importance_score?: number | null;
  importance_reason?: string | null;
  argument_role?: string | null;
  argument_link?: string | null;
  paragraph_gates?: ParagraphGates;
  prereading_refs?: string[];
  prereading_inline?: PrereadingInline[];
  hard_sentences?: HardSentence[];
  polemic_in_paragraph?: Polemic;
  sentences?: Sentence[];
};

export type LocalGlossaryItem = {
  term_id: string;
  surface_zh: string;
  scope?: string;
  definition: string;
  first_appearance_paragraph_n?: number;
  confidence?: ConfidenceLevel;
};

export type ReadingPath = {
  difficulty?: "easy" | "moderate" | "hard" | "expert";
  best_read_after?: string[];
  recommended_for?: string[];
  essential_paragraphs?: number[];
  estimated_minutes?: number;
};

export type PolemicTarget = {
  target_type?: string;
  target_id?: string;
  target_name_zh?: string;
  view_being_refuted?: string;
  author_position?: string;
};

export type DocMeta = {
  tldr_modern?: string;
  tldr_extended?: string[];
  historical_context?: string;
  polemic_targets?: PolemicTarget[];
  local_glossary?: LocalGlossaryItem[];
  key_concepts?: string[];
  primary_category?: string;
  reading_path?: ReadingPath;
  provenance?: any;
};

export type Doc = {
  id?: string;
  title?: string;
  title_local?: string | null;
  author_id?: string;
  year?: string | number;
  paragraphs: Paragraph[];
  meta?: DocMeta;
  footnotes?: any[];
};

// ===================================================================
// 工具
// ===================================================================

/** confidence: low 不展示（避免低质污染前端） */
export function notLow<T extends { confidence?: ConfidenceLevel }>(x: T): boolean {
  return x.confidence !== "low";
}

/** 段落对应 importance 视觉权重 */
export function importanceClass(score?: number | null): string {
  if (score === 3) return "p-importance-3";
  if (score === 2) return "p-importance-2";
  if (score === 1) return "p-importance-1";
  return "p-importance-0";
}

/** block_type 中文标签 */
export const BLOCK_TYPE_LABEL: Record<string, string> = {
  author_text: "正文",
  quote_block: "引文",
  aphorism: "警句",
  program_clause: "纲领",
  narrative: "叙事",
  footnote: "脚注",
  title: "标题",
  signature: "署名",
};

/** argument_role 中文标签 + 图标 */
export const ARGUMENT_ROLE_LABEL: Record<string, { label: string; icon: string }> = {
  continues: { label: "承接上段", icon: "↳" },
  contrasts: { label: "对照", icon: "⇆" },
  example: { label: "举例", icon: "📌" },
  conclusion: { label: "推论", icon: "→" },
  definition: { label: "定义", icon: "≡" },
  transition: { label: "过渡", icon: "—" },
  none: { label: "", icon: "" },
};

/** speaker 中文标签 */
export function speakerLabel(sp?: string): string {
  const map: Record<string, string> = {
    quoted_marx: "引马克思",
    quoted_engels: "引恩格斯",
    quoted_lenin: "引列宁",
    quoted_stalin: "引斯大林",
    quoted_opponent: "引论敌",
    editor: "编者",
    unknown: "出处不明",
    author: "",
  };
  return map[sp || "author"] || "";
}

/** stance 图标 */
export function stanceIcon(s?: string): string {
  const map: Record<string, string> = {
    self: "✏️",
    endorsed: "✅",
    criticized: "❌",
    neutral_citation: "📋",
  };
  return map[s || "self"] || "";
}

/** type 标签 */
export const NOTE_TYPE_LABEL: Record<string, string> = {
  concept: "概念",
  metaphor: "比喻",
  archaic: "古译",
  person: "人物",
  social_group: "社会群体",
  place: "地名",
  event: "事件",
  org: "组织",
  work: "著作",
  quote: "引文",
  slogan: "口号",
  program_clause: "纲领",
  polemic_ref: "论敌指代",
  translator_note: "译者注",
  footnote_ref: "脚注",
};

/** 难度标签 */
export const DIFFICULTY_LABEL: Record<string, { label: string; color: string }> = {
  easy: { label: "好读", color: "#3a7d44" },
  moderate: { label: "需要点耐心", color: "#7a6c2e" },
  hard: { label: "硬骨头", color: "#a86524" },
  expert: { label: "需对领域有底", color: "#a82a23" },
};

/** original_language 中文 */
export function langLabel(code?: string): string {
  return ({ de: "德文", ru: "俄文", en: "英文", fr: "法文" } as any)[code || ""] || code || "";
}

/** trigger 类型图标（hard_sentence） */
export function triggerIcon(trigger?: string): string {
  const map: Record<string, string> = {
    inverted_logic: "🔁",
    rhetorical: "❓",
    rhetorical_omission: "❓",
    allusion: "📜",
    term_polysemy: "⚖️",
    term_density: "🧩",
    cross_ref: "↗",
    long_nested: "🪜",
    text_anomaly: "⚠",
  };
  return map[trigger || ""] || "💡";
}
