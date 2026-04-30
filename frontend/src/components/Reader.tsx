import { useEffect, useMemo, useState } from "react";

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
  summary: "30 秒看懂这篇在讲什么 · 含术语速查",
  compare: "原文 + 大白话改写并排 · 不懂的词点一下",
  deep: "段意 · 逐句白话 · 句级注释卡",
};

export default function Reader({ doc }: { doc: Doc }) {
  const [mode, setMode] = useState<Mode>("summary");
  const meta = doc.meta || {};
  const paragraphs = doc.paragraphs || [];
  const [activeNote, setActiveNote] = useState<{
    note: Note;
    surface: string;
    anchor: { x: number; y: number };
  } | null>(null);

  // 关闭弹卡：点空白处 / Esc
  useEffect(() => {
    if (!activeNote) return;
    const onKey = (e: KeyboardEvent) =>
      e.key === "Escape" && setActiveNote(null);
    const onClick = (e: MouseEvent) => {
      const t = e.target as HTMLElement;
      if (
        !t.closest("[data-note-trigger]") &&
        !t.closest("[data-note-popover]")
      ) {
        setActiveNote(null);
      }
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("click", onClick);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("click", onClick);
    };
  }, [activeNote]);

  // 全文术语去重聚合（给 Summary 的术语速查）
  const glossary = useMemo(() => buildGlossary(paragraphs), [paragraphs]);

  return (
    <div className="relative">
      {/* Tab Bar — sticky 顶栏；摘要/精读内容居中，对照模式利用全宽 */}
      <div className="sticky top-0 z-20 bg-[var(--color-paper)] border-b border-[var(--color-line)] -mx-6 mb-10">
        <div className={mode === "compare" ? "px-6" : "reading-narrow px-6"}>
          <div className="flex gap-1 flex-wrap">
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
      </div>

      {mode === "summary" && (
        <div className="reading-narrow">
          <SummaryView
            meta={meta}
            glossary={glossary}
            onPickNote={setActiveNote}
          />
        </div>
      )}
      {mode === "compare" && (
        <CompareView paragraphs={paragraphs} onPickNote={setActiveNote} />
      )}
      {mode === "deep" && (
        <div className="reading-narrow">
          <DeepView paragraphs={paragraphs} onPickNote={setActiveNote} />
        </div>
      )}

      {/* 全局弹卡（移动端友好：点空白关闭，Esc 关闭，箭头按钮关闭）*/}
      {activeNote && (
        <NotePopover
          note={activeNote.note}
          surface={activeNote.surface}
          anchor={activeNote.anchor}
          onClose={() => setActiveNote(null)}
        />
      )}
    </div>
  );
}

// =====================================================================
// Summary View
// =====================================================================
function SummaryView({
  meta,
  glossary,
  onPickNote,
}: {
  meta: any;
  glossary: GlossaryEntry[];
  onPickNote: PickFn;
}) {
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
              <div
                key={i}
                className="border-l-2 border-[var(--color-accent)] pl-5 py-1"
              >
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

      {/* 术语速查 — 这是关键新增 */}
      {glossary.length > 0 && (
        <section>
          <h3 className="heading-display text-lg mb-2 accent-rule">术语速查</h3>
          <p className="font-sans text-xs text-[var(--color-ink-muted)] mb-5">
            本文里这些词不懂？点一下看现代解释。
          </p>
          <GlossaryGrid entries={glossary} onPickNote={onPickNote} />
        </section>
      )}

      {meta.provenance &&
        (meta.provenance.source_collection ||
          meta.provenance.original_language ||
          meta.provenance.written_at) && (
          <section className="pt-8 border-t border-[var(--color-line)]">
            <h4 className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-3">
              出处
            </h4>
            <div className="font-sans text-sm text-[var(--color-ink-soft)] space-y-1">
              {meta.provenance.written_at && (
                <p>
                  写作时间：{meta.provenance.written_at}
                  {meta.provenance.written_in
                    ? `（于 ${meta.provenance.written_in}）`
                    : ""}
                </p>
              )}
              {meta.provenance.first_published_at && (
                <p>
                  首次发表：{meta.provenance.first_published_at}
                  {meta.provenance.first_published_in_publication
                    ? ` · ${meta.provenance.first_published_in_publication}`
                    : ""}
                </p>
              )}
              {meta.provenance.source_collection && (
                <p>
                  选自：《{meta.provenance.source_collection}》
                  {meta.provenance.source_volume
                    ? ` 第 ${meta.provenance.source_volume} 卷`
                    : ""}
                  {meta.provenance.source_pages
                    ? `，第 ${meta.provenance.source_pages} 页`
                    : ""}
                </p>
              )}
              {meta.provenance.original_language && (
                <p>
                  原文语种：
                  {({ de: "德文", ru: "俄文", en: "英文", fr: "法文" } as any)[
                    meta.provenance.original_language
                  ] || meta.provenance.original_language}
                </p>
              )}
            </div>
          </section>
        )}
    </div>
  );
}

// =====================================================================
// Glossary Grid (术语速查)
// =====================================================================
type GlossaryEntry = {
  surface: string;
  type: string;
  modern: string;
  highlight?: string | null;
  count: number;
};

function buildGlossary(paragraphs: Paragraph[]): GlossaryEntry[] {
  const map = new Map<string, GlossaryEntry>();
  for (const p of paragraphs) {
    for (const s of p.sentences || []) {
      for (const n of s.notes || []) {
        const surface = n.surface;
        if (!surface || !n.modern) continue;
        const key = `${n.type || ""}::${surface}`;
        if (map.has(key)) {
          map.get(key)!.count += 1;
        } else {
          map.set(key, {
            surface,
            type: n.type || "concept",
            modern: n.modern,
            highlight: n.highlight,
            count: 1,
          });
        }
      }
    }
  }
  // 按类型权重 + 出现次数 排序
  const TYPE_ORDER: Record<string, number> = {
    metaphor: 0,
    person: 1,
    event: 1,
    work: 1,
    org: 1,
    concept: 2,
    concept_archaic_translation: 3,
    place: 4,
    polemic_ref: 4,
    quote: 5,
    translator_note: 6,
    footnote_ref: 7,
  };
  return Array.from(map.values()).sort((a, b) => {
    const ta = TYPE_ORDER[a.type] ?? 9;
    const tb = TYPE_ORDER[b.type] ?? 9;
    if (ta !== tb) return ta - tb;
    if (b.count !== a.count) return b.count - a.count;
    return a.surface.localeCompare(b.surface);
  });
}

function GlossaryGrid({
  entries,
  onPickNote,
}: {
  entries: GlossaryEntry[];
  onPickNote: PickFn;
}) {
  // 按 type 分组
  const groups = useMemo(() => {
    const m = new Map<string, GlossaryEntry[]>();
    for (const e of entries) {
      if (!m.has(e.type)) m.set(e.type, []);
      m.get(e.type)!.push(e);
    }
    return Array.from(m.entries());
  }, [entries]);

  return (
    <div className="space-y-7">
      {groups.map(([type, list]) => (
        <div key={type}>
          <h4 className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-3">
            {labelType(type)}
            <span className="ml-2 text-[var(--color-ink-muted)] normal-case">
              · {list.length}
            </span>
          </h4>
          <div className="flex flex-wrap gap-2">
            {list.map((e, i) => (
              <button
                key={i}
                data-note-trigger
                onClick={(ev) => {
                  ev.stopPropagation();
                  const r = (
                    ev.currentTarget as HTMLElement
                  ).getBoundingClientRect();
                  onPickNote({
                    note: {
                      surface: e.surface,
                      type: e.type,
                      modern: e.modern,
                      highlight: e.highlight,
                    },
                    surface: e.surface,
                    anchor: {
                      x: r.left + r.width / 2,
                      y: r.bottom + window.scrollY + 6,
                    },
                  });
                }}
                className={`text-base px-3 py-1.5 rounded font-serif border border-[var(--color-line)] hover:border-[var(--color-accent)] hover:text-[var(--color-accent)] transition-colors ${
                  e.highlight === "metaphor" ? "bg-[#fff1d6]" : ""
                } ${e.highlight === "archaic" ? "bg-[var(--color-accent-soft)]" : ""}`}
              >
                {e.surface}
                {e.count > 1 && (
                  <span className="font-sans text-xs text-[var(--color-ink-muted)] ml-1.5">
                    ×{e.count}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// =====================================================================
// Compare View — 左原文（带 inline 注释）/ 右白话改写
// =====================================================================
function CompareView({
  paragraphs,
  onPickNote,
}: {
  paragraphs: Paragraph[];
  onPickNote: PickFn;
}) {
  return (
    <div className="space-y-10 max-w-[1500px] mx-auto">
      <p className="font-sans text-xs text-[var(--color-ink-muted)] mb-6">
        左：原文（一字未改，
        <span className="term-highlight px-0.5">不懂的词点一下</span>
        ）　·　右：白话改写
        <span className="lg:hidden ml-2 text-[var(--color-accent)]">
          （窄屏自动单栏）
        </span>
      </p>
      {paragraphs.map((p) => (
        <ComparePara key={p.n} p={p} onPickNote={onPickNote} />
      ))}
    </div>
  );
}

function ComparePara({ p, onPickNote }: { p: Paragraph; onPickNote: PickFn }) {
  const skipRewrite = p.block_type === "title" || !p.plain_rewrite;
  // 把段内所有句子的 notes 合并（作用于整段原文）
  const allNotes = useMemo(() => {
    const arr: Note[] = [];
    for (const s of p.sentences || []) {
      for (const n of s.notes || []) arr.push(n);
    }
    return arr;
  }, [p]);

  return (
    <div className="grid lg:grid-cols-2 gap-x-12 gap-y-6 pb-10 border-b border-[var(--color-line)] last:border-b-0">
      <div>
        <span className="font-sans text-xs text-[var(--color-ink-muted)] tabular-nums">
          {String(p.n).padStart(3, "0")} · 原文
        </span>
        <p className="prose-paragraph mt-2">
          {annotateText(p.original_plain, allNotes, onPickNote)}
        </p>
      </div>
      <div>
        <span className="font-sans text-xs text-[var(--color-accent)] tabular-nums">
          {String(p.n).padStart(3, "0")} · 白话
        </span>
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
          <p className="prose-paragraph mt-2 text-[var(--color-ink)]">
            {p.plain_rewrite}
          </p>
        )}
      </div>
    </div>
  );
}

// =====================================================================
// Deep View
// =====================================================================
function DeepView({
  paragraphs,
  onPickNote,
}: {
  paragraphs: Paragraph[];
  onPickNote: PickFn;
}) {
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
          onPickNote={onPickNote}
        />
      ))}
    </div>
  );
}

function DeepPara({
  p,
  isOpen,
  onToggle,
  onPickNote,
}: {
  p: Paragraph;
  isOpen: boolean;
  onToggle: () => void;
  onPickNote: PickFn;
}) {
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
          <p
            className={`text-base leading-relaxed ${
              isOpen
                ? "text-[var(--color-ink)]"
                : "text-[var(--color-ink-soft)] line-clamp-2"
            }`}
          >
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
              <p className="text-base leading-loose text-[var(--color-ink)]">
                {p.plain_rewrite}
              </p>
            </div>
          )}
          {p.sentences && p.sentences.length > 0 && (
            <div>
              <h5 className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-3">
                逐句精读
              </h5>
              <div className="space-y-5">
                {p.sentences.map((s) => (
                  <SentenceRow key={s.sid} s={s} onPickNote={onPickNote} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SentenceRow({ s, onPickNote }: { s: Sentence; onPickNote: PickFn }) {
  return (
    <div className="space-y-2 pb-4 border-b border-[var(--color-line)]/60 last:border-b-0">
      <p className="text-base leading-relaxed text-[var(--color-ink)]">
        <span className="font-sans text-[10px] uppercase tracking-widest text-[var(--color-ink-muted)] mr-2 align-middle">
          原文
        </span>
        {annotateText(s.original, s.notes || [], onPickNote)}
      </p>
      <p className="text-base leading-relaxed text-[var(--color-ink-soft)]">
        <span className="font-sans text-[10px] uppercase tracking-widest text-[var(--color-accent)] mr-2 align-middle">
          白话
        </span>
        {s.speaker && s.speaker !== "author" && (
          <span className="font-sans text-xs text-[var(--color-accent)] mr-2">
            [{labelSpeaker(s.speaker)}]
          </span>
        )}
        {s.plain || (
          <span className="text-[var(--color-ink-muted)] italic">（待补）</span>
        )}
      </p>
    </div>
  );
}

// =====================================================================
// Inline 注释渲染（点击触发，移动端友好）
// =====================================================================
type PickFn = (
  payload: {
    note: Note;
    surface: string;
    anchor: { x: number; y: number };
  } | null,
) => void;

function annotateText(
  text: string,
  notes: Note[],
  onPickNote: PickFn,
): React.ReactNode {
  if (!notes || notes.length === 0) return text;
  const sorted = [...notes]
    .filter((n) => n.surface && text.includes(n.surface))
    .sort((a, b) => b.surface!.length - a.surface!.length);

  const used: { start: number; end: number; note: Note }[] = [];
  for (const n of sorted) {
    let from = 0;
    while (from < text.length) {
      const idx = text.indexOf(n.surface!, from);
      if (idx === -1) break;
      const end = idx + n.surface!.length;
      const overlaps = used.some((u) => !(end <= u.start || idx >= u.end));
      if (!overlaps) {
        used.push({ start: idx, end, note: n });
        // 默认只标第一次出现，避免段内大量重复高亮
        break;
      }
      from = idx + 1;
    }
  }
  used.sort((a, b) => a.start - b.start);

  const parts: React.ReactNode[] = [];
  let cursor = 0;
  let key = 0;
  for (const u of used) {
    if (cursor < u.start) parts.push(text.slice(cursor, u.start));
    parts.push(
      <NoteSpan
        key={key++}
        note={u.note}
        surface={text.slice(u.start, u.end)}
        onPickNote={onPickNote}
      />,
    );
    cursor = u.end;
  }
  if (cursor < text.length) parts.push(text.slice(cursor));
  return parts;
}

function NoteSpan({
  note,
  surface,
  onPickNote,
}: {
  note: Note;
  surface: string;
  onPickNote: PickFn;
}) {
  let cls = "term-highlight";
  if (note.highlight === "metaphor") cls = "metaphor-highlight";
  else if (note.highlight === "archaic") cls = "archaic-highlight";

  return (
    <button
      data-note-trigger
      onClick={(ev) => {
        ev.stopPropagation();
        const r = (ev.currentTarget as HTMLElement).getBoundingClientRect();
        onPickNote({
          note,
          surface,
          anchor: { x: r.left + r.width / 2, y: r.bottom + window.scrollY + 6 },
        });
      }}
      className={`${cls} cursor-pointer`}
      type="button"
    >
      {surface}
    </button>
  );
}

function NotePopover({
  note,
  surface,
  anchor,
  onClose,
}: {
  note: Note;
  surface: string;
  anchor: { x: number; y: number };
  onClose: () => void;
}) {
  // 视口边界：避免左右溢出
  const POP_WIDTH = 320;
  const margin = 12;
  let left = anchor.x - POP_WIDTH / 2;
  if (typeof window !== "undefined") {
    if (left < margin) left = margin;
    if (left + POP_WIDTH > window.innerWidth - margin) {
      left = window.innerWidth - POP_WIDTH - margin;
    }
  }
  return (
    <div
      data-note-popover
      style={{
        position: "absolute",
        top: anchor.y,
        left,
        width: POP_WIDTH,
        zIndex: 50,
      }}
      className="note-popover-pop"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="flex items-baseline justify-between mb-2">
        <div>
          <span className="font-sans text-[10px] uppercase tracking-widest text-[var(--color-accent)]">
            {labelType(note.type)}
          </span>
        </div>
        <button
          onClick={onClose}
          className="font-sans text-sm text-[var(--color-ink-muted)] hover:text-[var(--color-ink)] -mt-1"
          aria-label="关闭"
        >
          ✕
        </button>
      </div>
      <p className="font-serif text-lg font-medium text-[var(--color-ink)] mb-2">
        {surface}
      </p>
      <p className="text-sm leading-relaxed text-[var(--color-ink-soft)]">
        {note.modern || "（暂无解释）"}
      </p>
    </div>
  );
}

// =====================================================================
// 标签
// =====================================================================
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
