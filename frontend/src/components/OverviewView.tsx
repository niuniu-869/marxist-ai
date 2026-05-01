// 30 秒概览 — 读这篇前先看这一页
import type { DocMeta, ReadingPath } from "../lib/reader-v2";
import { DIFFICULTY_LABEL, langLabel, notLow } from "../lib/reader-v2";

type Props = {
  meta: DocMeta;
  onJumpToParagraph?: (n: number) => void;
};

export default function OverviewView({ meta, onJumpToParagraph }: Props) {
  const rp: ReadingPath | undefined = meta.reading_path;
  const polemic = meta.polemic_targets || [];
  const glossary = (meta.local_glossary || []).filter(notLow);

  return (
    <div className="space-y-12">
      {/* tldr 一句话 */}
      {meta.tldr_modern && (
        <section>
          <p className="text-2xl md:text-[1.7rem] leading-[1.7] text-[var(--color-ink)] font-serif">
            {meta.tldr_modern}
          </p>
        </section>
      )}

      {/* 难度 + 时间 + 速通段（reading_path） */}
      {rp &&
        (rp.difficulty ||
          rp.estimated_minutes ||
          (rp.essential_paragraphs?.length ?? 0) > 0) && (
          <section className="rounded p-5 bg-[var(--color-paper-warm)] border border-[var(--color-line)]">
            <div className="flex flex-wrap gap-x-8 gap-y-3 items-center">
              {rp.difficulty && (
                <div>
                  <span className="font-sans text-xs text-[var(--color-ink-muted)] uppercase tracking-widest mr-2">
                    难度
                  </span>
                  <span
                    className="font-sans text-sm font-medium"
                    style={{ color: DIFFICULTY_LABEL[rp.difficulty]?.color }}
                  >
                    {DIFFICULTY_LABEL[rp.difficulty]?.label || rp.difficulty}
                  </span>
                </div>
              )}
              {rp.estimated_minutes && (
                <div>
                  <span className="font-sans text-xs text-[var(--color-ink-muted)] uppercase tracking-widest mr-2">
                    预计
                  </span>
                  <span className="font-sans text-sm font-medium text-[var(--color-ink)]">
                    约 {rp.estimated_minutes} 分钟
                  </span>
                </div>
              )}
            </div>

            {rp.essential_paragraphs &&
              rp.essential_paragraphs.length > 0 &&
              onJumpToParagraph && (
                <div className="mt-4 pt-4 border-t border-[var(--color-line)]">
                  <p className="font-sans text-xs text-[var(--color-ink-muted)] mb-2">
                    没时间读全文？只看这 {rp.essential_paragraphs.length} 段也能
                    get 到核心
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {rp.essential_paragraphs.map((n) => (
                      <button
                        key={n}
                        onClick={() => onJumpToParagraph(n)}
                        className="font-sans text-sm px-3 py-1.5 rounded border border-[var(--color-accent)] text-[var(--color-accent)] hover:bg-[var(--color-accent-soft)] transition-colors tabular-nums"
                      >
                        §{n}
                      </button>
                    ))}
                  </div>
                </div>
              )}
          </section>
        )}

      {/* tldr_extended */}
      {meta.tldr_extended && meta.tldr_extended.length > 0 && (
        <section>
          <h3 className="heading-display text-lg mb-4 accent-rule">本文要点</h3>
          <ol className="space-y-4 list-none">
            {meta.tldr_extended.map((p, i) => (
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

      {/* historical_context */}
      {meta.historical_context && (
        <section>
          <h3 className="heading-display text-lg mb-4 accent-rule">写作背景</h3>
          <p className="text-base leading-loose text-[var(--color-ink-soft)]">
            {meta.historical_context}
          </p>
        </section>
      )}

      {/* polemic_targets */}
      {polemic.length > 0 && (
        <section>
          <h3 className="heading-display text-lg mb-4 accent-rule">在反对谁</h3>
          <div className="space-y-5">
            {polemic.map((t, i) => (
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
                      他们说
                    </span>
                    {t.view_being_refuted}
                  </p>
                )}
                {t.author_position && (
                  <p className="text-base leading-relaxed text-[var(--color-ink)]">
                    <span className="font-sans text-xs text-[var(--color-ink-muted)] mr-2">
                      作者答
                    </span>
                    {t.author_position}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* local_glossary：本文专有术语（v0.3 新数据源） */}
      {glossary.length > 0 && (
        <section>
          <h3 className="heading-display text-lg mb-2 accent-rule">
            本文专有术语
          </h3>
          <p className="font-sans text-xs text-[var(--color-ink-muted)] mb-5">
            这些词在本文有特定含义。日常用法可能不一样，先打个底。
          </p>
          <div className="space-y-4">
            {glossary.map((g, i) => (
              <div key={i} className="border-l border-[var(--color-line)] pl-4">
                <div className="flex items-baseline gap-3 mb-1">
                  <span className="font-serif font-medium text-[var(--color-ink)]">
                    {g.surface_zh}
                  </span>
                  {g.scope && (
                    <span className="font-sans text-xs text-[var(--color-ink-muted)]">
                      {g.scope}
                    </span>
                  )}
                </div>
                <p className="text-base leading-relaxed text-[var(--color-ink-soft)]">
                  {g.definition}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* provenance */}
      {meta.provenance && (
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
              <p>原文语种：{langLabel(meta.provenance.original_language)}</p>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
