import { useState, useMemo } from "react";

type Note = {
  surface?: string;
  type?: string;
  target?: string | null;
  modern?: string;
  highlight?: string | null;
};

type Sentence = {
  sid: string;
  original: string;
  plain?: string | null;
  speaker?: string | null;
  stance?: string | null;
  notes?: Note[];
};

type Paragraph = {
  n: number;
  original_plain: string;
  plain_rewrite?: string | null;
  gist?: string | null;
  block_type?: string | null;
  sentences?: Sentence[];
};

type PolemicTarget = {
  target_name_zh?: string;
  target_id?: string;
  view_being_refuted?: string;
  author_position?: string;
};

type Doc = {
  title?: string;
  paragraphs: Paragraph[];
  meta?: {
    tldr_modern?: string;
    tldr_extended?: string[];
    historical_context?: string;
    polemic_targets?: PolemicTarget[];
    key_concepts?: string[];
    key_persons?: string[];
    primary_category?: string;
    provenance?: any;
  };
};

type Mode = "summary" | "compare" | "deep";

const MODE_LABELS: Record<Mode, string> = {
  summary: "先看摘要",
  compare: "对照阅读",
  deep: "逐字精读",
};

const MODE_DESC: Record<Mode, string> = {
  summary: "30 秒看懂这篇在讲什么",
  compare: "原文 + 大白话改写并排",
  deep: "段意 · 逐句白话 · 概念注释",
};

export default function Reader({ doc }: { doc: Doc }) {
  const [mode, setMode] = useState<Mode>("summary");
  const meta = doc.meta || {};
  const paragraphs = doc.paragraphs || [];

  return (
    <div>
      {/* Tab Bar */}
      <div className="sticky top-0 z-20 bg-[var(--color-paper)] border-b border-[var(--color-line)] -mx-6 px-6 mb-10">
        <div className="flex gap-1">
          {(["summary", "compare", "deep"] as Mode[]).map((m) => (
            <button
              key={m}
              className="tab-btn"
              data-active={mode === m}
              onClick={() => setMode(m)}
            >
              {MODE_LABELS[m]}
            </button>
          ))}
        </div>
        <p className="font-sans text-xs text-[var(--color-ink-muted)] py-2">
          {MODE_DESC[mode]}
        </p>
      </div>

      {mode === "summary" && <SummaryView meta={meta} />}
      {mode === "compare" && <CompareView paragraphs={paragraphs} />}
      {mode === "deep" && <DeepView paragraphs={paragraphs} />}
    </div>
  );
}

function SummaryView({ meta }: { meta: any }) {
  return (
    <div className="space-y-12">
      {meta.tldr_modern && (
        <section>
          <p className="text-2xl leading-loose text-[var(--color-ink)] font-serif">
            {meta.tldr_modern}
          </p>
        </section>
      )}

      {meta.tldr_extended && meta.tldr_extended.length > 0 && (
        <section>
          <h3 className="heading-display text-lg mb-4 accent-rule">本文要点</h3>
          <ol className="space-y-4 list-none">
            {meta.tldr_extended.map((p: string, i: number) => (
              <li key={i} className="flex gap-4">
                <span className="font-sans text-sm text-[var(--color-accent)] font-medium tabular-nums shrink-0 mt-1">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span className="text-lg leading-relaxed">{p}</span>
              </li>
            ))}
          </ol>
        </section>
      )}

      {meta.historical_context && (
        <section>
          <h3 className="heading-display text-lg mb-4 accent-rule">写作背景</h3>
          <p className="text-base leading-loose text-[var(--color-ink-soft)]">
            {meta.historical_context}
          </p>
        </section>
      )}

      {meta.polemic_targets && meta.polemic_targets.length > 0 && (
        <section>
          <h3 className="heading-display text-lg mb-4 accent-rule">在反对谁</h3>
          <div className="space-y-5">
            {meta.polemic_targets.map((t: PolemicTarget, i: number) => (
              <div key={i} className="border-l-2 border-[var(--color-accent)] pl-5 py-1">
                <p className="font-sans text-sm font-medium text-[var(--color-accent)] mb-1">
                  {t.target_name_zh || t.target_id}
                </p>
                {t.view_being_refuted && (
                  <p className="text-base leading-relaxed text-[var(--color-ink-soft)] mb-2">
                    <span className="font-sans text-xs text-[var(--color-ink-muted)] mr-2">
                      对方观点
                    </span>
                    {t.view_being_refuted}
                  </p>
                )}
                {t.author_position && (
                  <p className="text-base leading-relaxed text-[var(--color-ink)]">
                    <span className="font-sans text-xs text-[var(--color-ink-muted)] mr-2">
                      作者立场
                    </span>
                    {t.author_position}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {(meta.key_concepts?.length || meta.key_persons?.length) && (
        <section className="grid md:grid-cols-2 gap-8 pt-8 border-t border-[var(--color-line)]">
          {meta.key_concepts?.length > 0 && (
            <div>
              <h4 className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-3">
                核心概念
              </h4>
              <p className="font-serif leading-relaxed">
                {meta.key_concepts.join(" · ")}
              </p>
            </div>
          )}
          {meta.key_persons?.length > 0 && (
            <div>
              <h4 className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-3">
                涉及人物
              </h4>
              <p className="font-serif leading-relaxed">
                {meta.key_persons.join(" · ")}
              </p>
            </div>
          )}
        </section>
      )}

      {meta.provenance && (meta.provenance.source_collection || meta.provenance.original_language) && (
        <section className="pt-8 border-t border-[var(--color-line)]">
          <h4 className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-3">
            出处
          </h4>
          <div className="font-sans text-sm text-[var(--color-ink-soft)] space-y-1">
            {meta.provenance.written_at && (
              <p>写作时间：{meta.provenance.written_at}{meta.provenance.written_in ? `（于 ${meta.provenance.written_in}）` : ""}</p>
            )}
            {meta.provenance.first_published_at && (
              <p>首次发表：{meta.provenance.first_published_at}{meta.provenance.first_published_in_publication ? ` · ${meta.provenance.first_published_in_publication}` : ""}</p>
            )}
            {meta.provenance.source_collection && (
              <p>选自：《{meta.provenance.source_collection}》{meta.provenance.source_volume ? ` 第 ${meta.provenance.source_volume} 卷` : ""}{meta.provenance.source_pages ? `，第 ${meta.provenance.source_pages} 页` : ""}</p>
            )}
            {meta.provenance.original_language && (
              <p>原文语种：{({ de: "德文", ru: "俄文", en: "英文", fr: "法文" } as any)[meta.provenance.original_language] || meta.provenance.original_language}</p>
            )}
          </div>
        </section>
      )}
    </div>
  );
}

function CompareView({ paragraphs }: { paragraphs: Paragraph[] }) {
  return (
    <div className="space-y-10">
      <p className="font-sans text-xs text-[var(--color-ink-muted)] mb-6">
        左：原文（一字未改）　·　右：白话改写（核心立场原样保留）
      </p>
      {paragraphs.map((p) => (
        <ComparePara key={p.n} p={p} />
      ))}
    </div>
  );
}

function ComparePara({ p }: { p: Paragraph }) {
  const skipRewrite = p.block_type === "title" || !p.plain_rewrite;
  return (
    <div className="grid md:grid-cols-2 gap-8 pb-8 border-b border-[var(--color-line)] last:border-b-0">
      <div>
        <span className="font-sans text-xs text-[var(--color-ink-muted)] tabular-nums">{String(p.n).padStart(3, "0")} · 原文</span>
        <p className="prose-paragraph mt-2">{p.original_plain}</p>
      </div>
      <div>
        <span className="font-sans text-xs text-[var(--color-accent)] tabular-nums">{String(p.n).padStart(3, "0")} · 白话</span>
        {p.gist && (
          <p className="font-sans text-sm text-[var(--color-ink-muted)] mt-2 mb-3 leading-relaxed italic">
            {p.gist}
          </p>
        )}
        {skipRewrite ? (
          <p className="prose-paragraph mt-2 text-[var(--color-ink-muted)]">
            （此段为标题/署名/引文 block，不作改写）
          </p>
        ) : (
          <p className="prose-paragraph mt-2 text-[var(--color-ink)]">{p.plain_rewrite}</p>
        )}
      </div>
    </div>
  );
}

function DeepView({ paragraphs }: { paragraphs: Paragraph[] }) {
  const [open, setOpen] = useState<number | null>(paragraphs[0]?.n ?? null);
  return (
    <div className="space-y-3">
      <p className="font-sans text-xs text-[var(--color-ink-muted)] mb-6">
        点击段落展开：段意 · 逐句白话 · 注释卡片
      </p>
      {paragraphs.map((p) => (
        <DeepPara
          key={p.n}
          p={p}
          isOpen={open === p.n}
          onToggle={() => setOpen(open === p.n ? null : p.n)}
        />
      ))}
    </div>
  );
}

function DeepPara({ p, isOpen, onToggle }: { p: Paragraph; isOpen: boolean; onToggle: () => void }) {
  return (
    <div className="border border-[var(--color-line)] rounded">
      <button
        onClick={onToggle}
        className="w-full text-left p-5 hover:bg-[var(--color-paper-warm)] transition-colors flex gap-4"
      >
        <span className="font-sans text-xs text-[var(--color-ink-muted)] tabular-nums shrink-0 mt-1">
          {String(p.n).padStart(3, "0")}
        </span>
        <span className="flex-1">
          {p.gist && (
            <p className="font-sans text-sm text-[var(--color-accent)] mb-2 leading-relaxed">
              {p.gist}
            </p>
          )}
          <p className={`text-base leading-relaxed ${isOpen ? "text-[var(--color-ink)]" : "text-[var(--color-ink-soft)] line-clamp-2"}`}>
            {p.original_plain}
          </p>
        </span>
        <span className="font-sans text-[var(--color-ink-muted)] shrink-0 mt-1">
          {isOpen ? "−" : "+"}
        </span>
      </button>
      {isOpen && (
        <div className="border-t border-[var(--color-line)] p-5 bg-[var(--color-paper-warm)]">
          {p.plain_rewrite && (
            <div className="mb-6">
              <h5 className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-2">
                整段白话
              </h5>
              <p className="text-base leading-loose text-[var(--color-ink)]">{p.plain_rewrite}</p>
            </div>
          )}
          {p.sentences && p.sentences.length > 0 && (
            <div>
              <h5 className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-3">
                逐句精读
              </h5>
              <div className="space-y-5">
                {p.sentences.map((s) => (
                  <SentenceRow key={s.sid} s={s} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SentenceRow({ s }: { s: Sentence }) {
  const renderedOriginal = useMemo(() => annotateText(s.original, s.notes || []), [s.original, s.notes]);
  return (
    <div className="grid md:grid-cols-[1fr_1fr] gap-4 pb-4 border-b border-[var(--color-line)]/60 last:border-b-0">
      <div className="text-base leading-relaxed">{renderedOriginal}</div>
      <div className="text-base leading-relaxed text-[var(--color-ink-soft)]">
        {s.speaker && s.speaker !== "author" && (
          <span className="font-sans text-xs text-[var(--color-accent)] mr-2">
            [{labelSpeaker(s.speaker)}]
          </span>
        )}
        {s.plain || <span className="text-[var(--color-ink-muted)] italic">（待补）</span>}
      </div>
    </div>
  );
}

function labelSpeaker(sp: string): string {
  const map: Record<string, string> = {
    quoted_marx: "引马克思",
    quoted_engels: "引恩格斯",
    quoted_lenin: "引列宁",
    quoted_opponent: "引论敌",
    editor: "编者",
    unknown: "出处不明",
  };
  return map[sp] || sp;
}

function annotateText(text: string, notes: Note[]): React.ReactNode {
  if (!notes || notes.length === 0) return text;
  // 按 surface 在文本中的首次出现位置切分（贪心，长 surface 优先）
  const sorted = [...notes]
    .filter((n) => n.surface && text.includes(n.surface))
    .sort((a, b) => (b.surface!.length - a.surface!.length));

  // 在文本上做不重叠 span 标记
  const used: { start: number; end: number; note: Note }[] = [];
  for (const n of sorted) {
    let idx = text.indexOf(n.surface!);
    while (idx !== -1) {
      const end = idx + n.surface!.length;
      const overlaps = used.some((u) => !(end <= u.start || idx >= u.end));
      if (!overlaps) {
        used.push({ start: idx, end, note: n });
        break;
      }
      idx = text.indexOf(n.surface!, idx + 1);
    }
  }
  used.sort((a, b) => a.start - b.start);

  const parts: React.ReactNode[] = [];
  let cursor = 0;
  let key = 0;
  for (const u of used) {
    if (cursor < u.start) parts.push(text.slice(cursor, u.start));
    parts.push(<NoteSpan key={key++} note={u.note} surface={text.slice(u.start, u.end)} />);
    cursor = u.end;
  }
  if (cursor < text.length) parts.push(text.slice(cursor));
  return parts;
}

function NoteSpan({ note, surface }: { note: Note; surface: string }) {
  const cls = note.highlight === "metaphor" ? "metaphor-highlight" : "term-highlight";
  return (
    <span className="relative inline-block group">
      <span className={cls}>{surface}</span>
      <span className="absolute z-30 left-1/2 -translate-x-1/2 bottom-full mb-2 w-72 hidden group-hover:block note-popover text-left">
        <span className="block font-sans text-xs text-[var(--color-accent)] mb-1">
          {labelType(note.type)}
        </span>
        <span className="block text-[var(--color-ink-soft)]">{note.modern || ""}</span>
      </span>
    </span>
  );
}

function labelType(t?: string): string {
  const map: Record<string, string> = {
    concept: "概念",
    concept_archaic_translation: "老译晦涩词",
    person: "人物",
    place: "地名",
    event: "历史事件",
    work: "著作",
    org: "组织",
    quote: "引文",
    metaphor: "比喻",
    polemic_ref: "论敌指代",
    translator_note: "译者注",
    footnote_ref: "脚注",
  };
  return map[t || ""] || "注";
}
