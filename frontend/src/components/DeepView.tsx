// 句级精读：在 ScaffoldView 的基础上加每句 speaker/stance + 词级 notes
import { useState } from "react";
import type { Paragraph, Sentence, Note } from "../lib/reader-v2";
import {
  speakerLabel,
  stanceIcon,
  NOTE_TYPE_LABEL,
  notLow,
} from "../lib/reader-v2";

type Props = {
  paragraphs: Paragraph[];
};

export default function DeepView({ paragraphs }: Props) {
  const [open, setOpen] = useState<number | null>(paragraphs[0]?.n ?? null);
  return (
    <div className="reading-narrow space-y-3">
      <p className="font-sans text-xs text-[var(--color-ink-muted)] mb-6 leading-relaxed">
        点击段落展开：每句的发言人 / 立场 / 词级注释。注释只显示通过质量审核（confidence ≥ medium）的项。
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

function DeepPara({
  p,
  isOpen,
  onToggle,
}: {
  p: Paragraph;
  isOpen: boolean;
  onToggle: () => void;
}) {
  const sentences = p.sentences || [];
  return (
    <div className="border border-[var(--color-line)] rounded">
      <button
        onClick={onToggle}
        className="w-full text-left p-5 hover:bg-[var(--color-paper-warm)] transition-colors flex gap-4"
      >
        <span className="font-sans text-xs text-[var(--color-ink-muted)] tabular-nums shrink-0 mt-1">
          §{p.n}
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
      {isOpen && sentences.length > 0 && (
        <div className="border-t border-[var(--color-line)] p-5 bg-[var(--color-paper-warm)]">
          <h5 className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-3">
            逐句精读
          </h5>
          <div className="space-y-5">
            {sentences.map((s) => (
              <SentenceRow key={s.sid} s={s} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function SentenceRow({ s }: { s: Sentence }) {
  const sp = s.speaker || "author";
  const spLabel = speakerLabel(sp);
  const isOpponent = sp === "quoted_opponent";
  const notes = (s.notes || []).filter(notLow);

  return (
    <div className="space-y-2 pb-4 border-b border-[var(--color-line)]/60 last:border-b-0">
      <div className="flex items-baseline gap-2 flex-wrap">
        {spLabel && (
          <span
            className={`font-sans text-xs px-1.5 py-0.5 rounded ${
              isOpponent
                ? "bg-[var(--color-accent-soft)] text-[var(--color-accent)]"
                : "bg-[var(--color-paper)] text-[var(--color-ink-muted)] border border-[var(--color-line)]"
            }`}
          >
            [{spLabel}]
          </span>
        )}
        {s.stance && s.stance !== "self" && (
          <span className="font-sans text-xs text-[var(--color-ink-muted)]" title={s.stance}>
            {stanceIcon(s.stance)}
          </span>
        )}
      </div>
      <p
        className={`text-base leading-relaxed ${
          isOpponent
            ? "border-l-2 border-[var(--color-accent)] pl-3 text-[var(--color-ink-soft)]"
            : "text-[var(--color-ink)]"
        }`}
      >
        {s.original}
      </p>
      {notes.length > 0 && (
        <div className="mt-3 space-y-2">
          {notes.map((n, i) => (
            <NoteCard key={i} n={n} />
          ))}
        </div>
      )}
    </div>
  );
}

function NoteCard({ n }: { n: Note }) {
  return (
    <div className="rounded bg-white border border-[var(--color-line)] p-3 text-sm leading-relaxed">
      <div className="flex items-baseline gap-2 mb-1 flex-wrap">
        <span className="font-serif font-medium text-[var(--color-ink)]">
          {n.surface}
        </span>
        <span className="font-sans text-[10px] uppercase tracking-widest text-[var(--color-ink-muted)]">
          {NOTE_TYPE_LABEL[n.type] || n.type}
        </span>
        {n.sense_id && (
          <code className="font-sans text-[10px] text-[var(--color-ink-muted)] bg-[var(--color-paper-warm)] px-1.5 py-0.5 rounded">
            {n.sense_id}
          </code>
        )}
        {n.confidence === "medium" && (
          <span className="font-sans text-[10px] text-[var(--color-ink-muted)]" title="中等可信度">
            ◐
          </span>
        )}
      </div>
      <p className="text-[var(--color-ink-soft)]">{n.modern}</p>
      {n.source_basis && (
        <p className="font-sans text-[10px] text-[var(--color-ink-muted)] mt-1">
          依据：
          {({
            whitelist: "白名单",
            text_evidence: "文本证据",
            metadata: "篇章元数据",
            known_history: "公认史实",
            inferred: "推断",
          } as any)[n.source_basis] || n.source_basis}
        </p>
      )}
    </div>
  );
}
