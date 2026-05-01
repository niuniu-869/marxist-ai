// 带支架阅读 — v0.3 主模式
// 设计：原文为主体（760px居中），右侧 380px 支架栏（≥1280px 时浮现）；窄屏支架栏变折叠
// importance_score 驱动视觉节奏：0=折叠/淡 / 1=常 / 2=灰条 / 3=红条+★

import { useEffect, useRef, useState } from "react";
import type {
  Paragraph,
  HardSentence,
  LocalGlossaryItem,
} from "../lib/reader-v2";
import {
  ARGUMENT_ROLE_LABEL,
  BLOCK_TYPE_LABEL,
  notLow,
  triggerIcon,
} from "../lib/reader-v2";

type ActiveScaffold =
  | { kind: "gist"; para: number }
  | { kind: "prereading"; para: number; idx: number }
  | { kind: "ref"; para: number; term_id: string }
  | { kind: "hard"; para: number; idx: number }
  | { kind: "polemic"; para: number };

type Props = {
  paragraphs: Paragraph[];
  glossary: LocalGlossaryItem[];
  jumpTo?: number | null;
};

export default function ScaffoldView({ paragraphs, glossary, jumpTo }: Props) {
  const [active, setActive] = useState<ActiveScaffold | null>(null);
  const [showLowImportance, setShowLowImportance] = useState(false);
  const paraRefs = useRef<Map<number, HTMLDivElement | null>>(new Map());

  // 跳转到指定段
  useEffect(() => {
    if (jumpTo == null) return;
    const el = paraRefs.current.get(jumpTo);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [jumpTo]);

  const lowImpCount = paragraphs.filter((p) => p.importance_score === 0).length;

  return (
    <div className="grid lg:grid-cols-[minmax(0,1fr)_380px] gap-x-12 max-w-[1700px] mx-auto">
      {/* 主原文区 */}
      <div className="reading-narrow lg:mx-0 lg:ml-auto lg:mr-0 w-full">
        <p className="font-sans text-xs text-[var(--color-ink-muted)] mb-8 leading-relaxed">
          <span className="text-[var(--color-accent)]">●</span>
          &nbsp;红色段是核心论点 &nbsp;·&nbsp;
          <span className="text-[var(--color-ink-muted)]">○</span>
          &nbsp;灰段是支撑 &nbsp;·&nbsp;
          段后图标点击展开支架（段意/难句/反对谁/读前须知）
        </p>

        {paragraphs.map((p) => {
          const skip = p.importance_score === 0 && !showLowImportance;
          if (skip) return null;
          return (
            <ParagraphCard
              key={p.n}
              p={p}
              active={active}
              onSelect={setActive}
              registerRef={(el) => paraRefs.current.set(p.n, el)}
            />
          );
        })}

        {lowImpCount > 0 && !showLowImportance && (
          <div className="my-12 text-center">
            <button
              onClick={() => setShowLowImportance(true)}
              className="font-sans text-sm text-[var(--color-ink-muted)] hover:text-[var(--color-ink)] underline underline-offset-4"
            >
              另有 {lowImpCount} 段辅助材料 / 跳读段，点这里展开
            </button>
          </div>
        )}
        {lowImpCount > 0 && showLowImportance && (
          <div className="my-8 text-center">
            <button
              onClick={() => setShowLowImportance(false)}
              className="font-sans text-xs text-[var(--color-ink-muted)] hover:text-[var(--color-ink)] underline underline-offset-4"
            >
              收起辅助段
            </button>
          </div>
        )}
      </div>

      {/* 右侧支架栏 - 只在 lg 以上展示 */}
      <aside className="hidden lg:block lg:sticky lg:top-24 lg:self-start lg:max-h-[calc(100vh-7rem)] lg:overflow-auto">
        <ScaffoldPanel
          active={active}
          paragraphs={paragraphs}
          glossary={glossary}
          onClose={() => setActive(null)}
        />
      </aside>
    </div>
  );
}

// ===================================================================
// 段落卡
// ===================================================================
function ParagraphCard({
  p,
  active,
  onSelect,
  registerRef,
}: {
  p: Paragraph;
  active: ActiveScaffold | null;
  onSelect: (a: ActiveScaffold) => void;
  registerRef: (el: HTMLDivElement | null) => void;
}) {
  const isActive = (kind: ActiveScaffold["kind"]) =>
    active?.kind === kind && (active as any).para === p.n;

  const score = p.importance_score ?? 1;
  const blockType = p.block_type || "author_text";
  const argRole =
    p.argument_role && p.argument_role !== "none" ? p.argument_role : null;
  const polemic = p.polemic_in_paragraph;
  const hsList = (p.hard_sentences || []).filter(notLow);
  const preList = (p.prereading_inline || []).filter(notLow);
  const refList = p.prereading_refs || [];

  // 视觉变量
  let railColor = "transparent";
  if (score === 3) railColor = "var(--color-accent)";
  else if (score === 2) railColor = "var(--color-line)";

  // block_type 特殊样式
  const titleLike = blockType === "title";
  const sigLike = blockType === "signature";
  const footnote = blockType === "footnote";

  return (
    <div
      ref={registerRef}
      id={`p${p.n}`}
      className={`relative pl-5 py-6 border-l-2 transition-colors ${score === 0 ? "opacity-60" : ""}`}
      style={{ borderColor: railColor }}
    >
      {/* 段头 meta */}
      <div className="flex items-center gap-3 mb-3 text-[var(--color-ink-muted)]">
        <span className="font-sans text-xs tabular-nums">§{p.n}</span>
        {score === 3 && (
          <span className="font-sans text-xs text-[var(--color-accent)] font-medium">
            ★ 核心
          </span>
        )}
        {argRole && ARGUMENT_ROLE_LABEL[argRole] && (
          <span className="font-sans text-xs" title={p.argument_link || ""}>
            {ARGUMENT_ROLE_LABEL[argRole].icon}{" "}
            {ARGUMENT_ROLE_LABEL[argRole].label}
          </span>
        )}
        {blockType !== "author_text" && BLOCK_TYPE_LABEL[blockType] && (
          <span className="font-sans text-xs px-1.5 py-0.5 bg-[var(--color-paper-warm)] rounded">
            {BLOCK_TYPE_LABEL[blockType]}
          </span>
        )}
      </div>

      {/* polemic banner */}
      {polemic?.is_polemical && polemic.target && (
        <button
          data-active={isActive("polemic")}
          onClick={() => onSelect({ kind: "polemic", para: p.n })}
          className="mb-3 text-left flex items-center gap-2 text-sm font-sans text-[var(--color-accent)] hover:underline"
        >
          🎯 在反对：<span className="font-medium">{polemic.target}</span>
        </button>
      )}

      {/* prereading 折叠条 */}
      {(preList.length > 0 || refList.length > 0) && (
        <div className="mb-3 flex flex-wrap gap-2">
          {preList.map((pr, i) => (
            <button
              key={i}
              data-active={isActive("prereading") && (active as any)?.idx === i}
              onClick={() =>
                onSelect({ kind: "prereading", para: p.n, idx: i })
              }
              className="font-sans text-xs px-2 py-1 rounded border border-[var(--color-line)] hover:border-[var(--color-accent)] text-[var(--color-ink-muted)] hover:text-[var(--color-accent)] transition-colors"
            >
              👁 {pr.topic}
            </button>
          ))}
          {refList.map((tid) => (
            <button
              key={tid}
              data-active={isActive("ref") && (active as any)?.term_id === tid}
              onClick={() => onSelect({ kind: "ref", para: p.n, term_id: tid })}
              className="font-sans text-xs px-2 py-1 rounded border border-dashed border-[var(--color-line)] hover:border-[var(--color-accent)] text-[var(--color-ink-muted)] hover:text-[var(--color-accent)] transition-colors"
            >
              📖 {tid}
            </button>
          ))}
        </div>
      )}

      {/* 原文 + 难句下划线 */}
      <p
        className={`leading-[2.05] text-[var(--color-ink)] ${
          titleLike
            ? "text-2xl md:text-3xl font-medium font-serif text-center my-6"
            : sigLike
              ? "text-sm text-right text-[var(--color-ink-muted)] italic"
              : footnote
                ? "text-sm pl-3 border-l-2 border-[var(--color-line)] text-[var(--color-ink-soft)]"
                : "text-lg"
        }`}
      >
        {renderOriginalWithHardSentences(
          p.original_plain,
          hsList,
          (idx) => onSelect({ kind: "hard", para: p.n, idx }),
          isActive("hard") ? (active as any)?.idx : -1,
        )}
      </p>

      {/* gist 触发按钮（不冲突时折叠到右栏，窄屏时段后展开） */}
      {p.gist && !titleLike && !sigLike && (
        <div className="mt-3 lg:hidden">
          <button
            onClick={() => onSelect({ kind: "gist", para: p.n })}
            className="font-sans text-xs text-[var(--color-ink-muted)] hover:text-[var(--color-accent)] underline underline-offset-4"
          >
            段意 / 论证作用
          </button>
        </div>
      )}
      {/* lg 时点段头点击高亮支架栏 */}
      {p.gist && !titleLike && !sigLike && (
        <button
          onClick={() => onSelect({ kind: "gist", para: p.n })}
          className="hidden lg:block absolute right-2 top-6 font-sans text-xs text-[var(--color-ink-muted)] hover:text-[var(--color-accent)]"
          title="查看段意"
        >
          ⓘ
        </button>
      )}

      {/* 窄屏支架卡 - 内联展开（lg 以下） */}
      {active && (active as any).para === p.n && (
        <div className="lg:hidden mt-4 rounded border border-[var(--color-line)] bg-[var(--color-paper-warm)] p-4">
          <ScaffoldCard
            active={active}
            paragraph={p}
            onClose={() => {}}
            inline
          />
        </div>
      )}
    </div>
  );
}

// ===================================================================
// 难句下划线渲染
// ===================================================================
function renderOriginalWithHardSentences(
  text: string,
  hsList: HardSentence[],
  onPick: (idx: number) => void,
  activeIdx: number,
): React.ReactNode {
  if (!hsList.length) return text;
  // 找到每个 hard_sentence quote 在文中的位置
  const hits: { start: number; end: number; idx: number; trigger?: string }[] =
    [];
  hsList.forEach((hs, i) => {
    const q = hs.quote;
    if (!q) return;
    const idx = text.indexOf(q);
    if (idx >= 0)
      hits.push({
        start: idx,
        end: idx + q.length,
        idx: i,
        trigger: hs.trigger,
      });
  });
  hits.sort((a, b) => a.start - b.start);

  // 拼接
  const parts: React.ReactNode[] = [];
  let cursor = 0;
  hits.forEach((h, i) => {
    if (cursor < h.start)
      parts.push(<span key={`t${i}`}>{text.slice(cursor, h.start)}</span>);
    const isActive = h.idx === activeIdx;
    parts.push(
      <button
        key={`h${i}`}
        onClick={() => onPick(h.idx)}
        className={`hard-sentence-mark ${isActive ? "is-active" : ""}`}
        title="难句拆解 · 点击展开"
      >
        {text.slice(h.start, h.end)}
        <sup className="ml-1 font-sans text-xs">{triggerIcon(h.trigger)}</sup>
      </button>,
    );
    cursor = h.end;
  });
  if (cursor < text.length)
    parts.push(<span key="tail">{text.slice(cursor)}</span>);
  return parts;
}

// ===================================================================
// 右侧支架栏（lg+）
// ===================================================================
function ScaffoldPanel({
  active,
  paragraphs,
  glossary,
  onClose,
}: {
  active: ActiveScaffold | null;
  paragraphs: Paragraph[];
  glossary: LocalGlossaryItem[];
  onClose: () => void;
}) {
  if (!active) {
    return (
      <div className="rounded border border-[var(--color-line)] bg-[var(--color-paper-warm)] p-6">
        <p className="font-sans text-sm text-[var(--color-ink-muted)] leading-relaxed">
          点击段落里的 <strong>下划线难句</strong>、段头的{" "}
          <strong>🎯 反对</strong> 或 <strong>👁 读前须知</strong> 按钮，
          <br />
          这里会显示对应的支架内容。
        </p>
      </div>
    );
  }
  const p = paragraphs.find((x) => x.n === active.para);
  if (!p) return null;
  return (
    <div className="rounded border border-[var(--color-line)] bg-white p-6 shadow-sm">
      <div className="flex items-baseline justify-between mb-4">
        <span className="font-sans text-xs uppercase tracking-widest text-[var(--color-accent)]">
          §{p.n} · {scaffoldTitle(active)}
        </span>
        <button
          onClick={onClose}
          className="font-sans text-sm text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
        >
          ✕
        </button>
      </div>
      <ScaffoldCard
        active={active}
        paragraph={p}
        glossary={glossary}
        onClose={onClose}
      />
    </div>
  );
}

function scaffoldTitle(a: ActiveScaffold): string {
  switch (a.kind) {
    case "gist":
      return "段意";
    case "prereading":
      return "读前须知";
    case "ref":
      return "本文术语";
    case "hard":
      return "难句拆解";
    case "polemic":
      return "在反对谁";
  }
}

// ===================================================================
// 支架卡内容（左右栏 + 窄屏内联通用）
// ===================================================================
function ScaffoldCard({
  active,
  paragraph,
  glossary,
}: {
  active: ActiveScaffold;
  paragraph: Paragraph;
  glossary?: LocalGlossaryItem[];
  onClose: () => void;
  inline?: boolean;
}) {
  if (active.kind === "gist") {
    return (
      <div>
        {paragraph.gist && (
          <p className="text-base leading-relaxed text-[var(--color-ink)] mb-3">
            {paragraph.gist}
          </p>
        )}
        {paragraph.argument_link && (
          <p className="font-sans text-sm text-[var(--color-ink-muted)] leading-relaxed">
            <span className="font-medium text-[var(--color-ink-soft)] mr-2">
              论证
            </span>
            {paragraph.argument_link}
          </p>
        )}
        {paragraph.importance_reason && (
          <p className="font-sans text-xs text-[var(--color-ink-muted)] mt-3 italic">
            为什么重要：{paragraph.importance_reason}
          </p>
        )}
      </div>
    );
  }

  if (active.kind === "prereading") {
    const pr = paragraph.prereading_inline?.[active.idx];
    if (!pr) return null;
    return (
      <div>
        <p className="font-serif font-medium text-lg text-[var(--color-ink)] mb-3">
          {pr.topic}
        </p>
        <p className="text-base leading-relaxed text-[var(--color-ink-soft)]">
          {pr.explain}
        </p>
      </div>
    );
  }

  if (active.kind === "ref") {
    const g = (glossary || []).find((x) => x.term_id === active.term_id);
    if (!g) {
      return (
        <p className="font-sans text-sm text-[var(--color-ink-muted)] italic">
          术语 <code>{active.term_id}</code> 未在本文术语表中找到。
        </p>
      );
    }
    return (
      <div>
        <p className="font-serif font-medium text-lg text-[var(--color-ink)] mb-1">
          {g.surface_zh}
        </p>
        {g.scope && (
          <p className="font-sans text-xs text-[var(--color-ink-muted)] mb-3">
            {g.scope}
          </p>
        )}
        <p className="text-base leading-relaxed text-[var(--color-ink-soft)]">
          {g.definition}
        </p>
      </div>
    );
  }

  if (active.kind === "hard") {
    const hs = paragraph.hard_sentences?.[active.idx];
    if (!hs) return null;
    return (
      <div className="space-y-4">
        <div className="font-serif text-base leading-relaxed text-[var(--color-ink)] bg-[var(--color-paper-warm)] p-3 rounded">
          「{hs.quote}」
        </div>
        {hs.reader_block && (
          <div>
            <p className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-1">
              卡在哪
            </p>
            <p className="text-sm leading-relaxed text-[var(--color-ink-soft)]">
              {hs.reader_block}
            </p>
          </div>
        )}
        {hs.parse?.claim && (
          <div>
            <p className="font-sans text-xs uppercase tracking-widest text-[var(--color-accent)] mb-1">
              主张
            </p>
            <p className="text-sm leading-relaxed text-[var(--color-ink)]">
              {hs.parse.claim}
            </p>
          </div>
        )}
        {hs.parse?.qualifiers && (
          <div>
            <p className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-1">
              限定
            </p>
            <p className="text-sm leading-relaxed text-[var(--color-ink-soft)]">
              {hs.parse.qualifiers}
            </p>
          </div>
        )}
        {hs.parse?.contrast_or_target && (
          <div>
            <p className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-1">
              对照 / 反驳
            </p>
            <p className="text-sm leading-relaxed text-[var(--color-ink-soft)]">
              {hs.parse.contrast_or_target}
            </p>
          </div>
        )}
        {hs.why?.explanation && (
          <div className="pt-3 border-t border-[var(--color-line)]">
            <p className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-1">
              在论证中的角色
            </p>
            <p className="text-sm leading-relaxed text-[var(--color-ink-soft)]">
              {hs.why.explanation}
            </p>
          </div>
        )}
        {hs.implication && (
          <div>
            <p className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-1">
              进一步推论
            </p>
            <p className="text-sm leading-relaxed text-[var(--color-ink-soft)]">
              {hs.implication}
            </p>
          </div>
        )}
      </div>
    );
  }

  if (active.kind === "polemic") {
    const pol = paragraph.polemic_in_paragraph;
    if (!pol?.is_polemical) return null;
    return (
      <div className="space-y-4">
        {pol.target && (
          <div>
            <p className="font-sans text-xs uppercase tracking-widest text-[var(--color-accent)] mb-1">
              对象
            </p>
            <p className="font-serif font-medium text-base text-[var(--color-ink)]">
              {pol.target}
            </p>
          </div>
        )}
        {pol.their_view && (
          <div>
            <p className="font-sans text-xs uppercase tracking-widest text-[var(--color-ink-muted)] mb-1">
              他们说
            </p>
            <p className="text-sm leading-relaxed text-[var(--color-ink-soft)]">
              {pol.their_view}
            </p>
          </div>
        )}
        {pol.author_response && (
          <div className="pt-3 border-t border-[var(--color-line)]">
            <p className="font-sans text-xs uppercase tracking-widest text-[var(--color-accent)] mb-1">
              作者答
            </p>
            <p className="text-sm leading-relaxed text-[var(--color-ink)]">
              {pol.author_response}
            </p>
          </div>
        )}
      </div>
    );
  }

  return null;
}
