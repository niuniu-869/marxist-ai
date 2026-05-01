// Reader 主壳 — v0.3 schema
// 三模式：30 秒概览 / 带支架阅读 / 句级精读
import { useState } from "react";
import type { Doc } from "../lib/reader-v2";
import OverviewView from "./OverviewView";
import ScaffoldView from "./ScaffoldView";
import DeepView from "./DeepView";

type Mode = "overview" | "scaffold" | "deep";

const MODE_LABELS: Record<Mode, string> = {
  overview: "30 秒概览",
  scaffold: "带支架阅读",
  deep: "句级精读",
};

const MODE_DESC: Record<Mode, string> = {
  overview: "篇章摘要 · 在反对谁 · 本文专有术语 · 难度与必读段",
  scaffold: "原文为主 · 段落难句下划线点击 · 段头反对谁 / 读前须知",
  deep: "每句发言人 / 立场 / 词级注释（仅展示通过质量审核的）",
};

export default function Reader({ doc }: { doc: Doc }) {
  const [mode, setMode] = useState<Mode>("scaffold"); // 默认主战场
  const [jumpTo, setJumpTo] = useState<number | null>(null);
  const meta = doc.meta || {};
  const paragraphs = doc.paragraphs || [];
  const glossary = meta.local_glossary || [];

  return (
    <div className="relative">
      {/* Tab Bar */}
      <div className="sticky top-0 z-20 bg-[var(--color-paper)] border-b border-[var(--color-line)] -mx-6 mb-10">
        <div className={mode === "overview" || mode === "deep" ? "reading-narrow px-6" : "container-ultra px-6"}>
          <div className="flex gap-1 flex-wrap">
            {(["overview", "scaffold", "deep"] as Mode[]).map((m) => (
              <button
                key={m}
                className="tab-btn"
                data-active={mode === m}
                onClick={() => {
                  setMode(m);
                  if (m !== "scaffold") setJumpTo(null);
                }}
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

      {mode === "overview" && (
        <div className="reading-narrow">
          <OverviewView
            meta={meta}
            onJumpToParagraph={(n) => {
              setMode("scaffold");
              setJumpTo(n);
            }}
          />
        </div>
      )}
      {mode === "scaffold" && (
        <ScaffoldView paragraphs={paragraphs} glossary={glossary} jumpTo={jumpTo} />
      )}
      {mode === "deep" && <DeepView paragraphs={paragraphs} />}

      {/* 诚实声明 */}
      <footer className="reading-narrow mt-20 pt-8 border-t border-[var(--color-line)] font-sans text-xs text-[var(--color-ink-muted)] leading-relaxed">
        <p className="mb-2">
          <strong className="text-[var(--color-ink-soft)]">关于本文的标注</strong>
        </p>
        <p>
          段意 / 难句拆解 / 读前须知 / 在反对谁 / 词级注释，皆由 AI 标注（mimo
          v2.5）后经硬规则过滤生成。我们不改写原文，标注只作辅助；如某段无支架，是工具判定不需要而非疏漏。<br />
          注释偶有不准；遇到分歧请以原文为准，我们也欢迎反馈。
        </p>
      </footer>
    </div>
  );
}
