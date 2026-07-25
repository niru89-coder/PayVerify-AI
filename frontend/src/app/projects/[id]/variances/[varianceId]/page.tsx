"use client";

import Link from "next/link";
import { useEffect, useState, use as usePromise } from "react";
import { api, Variance } from "@/lib/api";
import { ClassificationBadge, ResolutionBadge, SuggestionBadge } from "@/components/Badges";

export default function VarianceDetailPage({
  params,
}: {
  params: Promise<{ id: string; varianceId: string }>;
}) {
  const { id, varianceId } = usePromise(params);
  const projectId = Number(id);
  const vId = Number(varianceId);

  const [variance, setVariance] = useState<Variance | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [explaining, setExplaining] = useState(false);
  const [action, setAction] = useState<"confirmed" | "rejected" | "needs_correction">("confirmed");
  const [consultant, setConsultant] = useState("");
  const [notes, setNotes] = useState("");
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  function load() {
    api.getVariance(vId).then(setVariance).catch((err) => setError(String(err.message ?? err)));
  }

  useEffect(load, [vId]);

  async function handleExplain() {
    setExplaining(true);
    try {
      const updated = await api.explainVariance(vId);
      setVariance(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setExplaining(false);
    }
  }

  async function handleFeedback(e: React.FormEvent) {
    e.preventDefault();
    setSubmittingFeedback(true);
    setFeedbackMessage(null);
    try {
      await api.submitFeedback(vId, { action, consultant, notes });
      setFeedbackMessage("Feedback recorded.");
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmittingFeedback(false);
    }
  }

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!variance) return <p className="text-sm text-slate-500">Loading…</p>;

  return (
    <div className="max-w-3xl space-y-6">
      <Link href={`/projects/${projectId}/variances`} className="text-sm text-indigo-600 hover:underline">
        ← Back to Variance Dashboard
      </Link>

      <div className="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-slate-900">
            Employee #{variance.employee_id} · {variance.component_code}
          </h1>
          <ClassificationBadge value={variance.classification} />
        </div>

        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-xs uppercase text-slate-400">Client Value</p>
            <p className="text-lg font-medium text-slate-800">{variance.client_value ?? "—"}</p>
          </div>
          <div>
            <p className="text-xs uppercase text-slate-400">Platform Value</p>
            <p className="text-lg font-medium text-slate-800">{variance.platform_value ?? "—"}</p>
          </div>
          <div>
            <p className="text-xs uppercase text-slate-400">Rule-Engine Expected</p>
            <p className="text-lg font-medium text-slate-800">{variance.expected_value ?? "—"}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs uppercase text-slate-400">Suggestion:</span>
          <SuggestionBadge value={variance.suggestion_outcome} />
          <span className="text-xs text-slate-500">({Math.round(variance.confidence_score * 100)}% confidence)</span>
        </div>

        <div>
          <p className="text-xs uppercase text-slate-400">Recommended Action</p>
          <p className="text-sm text-slate-700">{variance.recommended_action}</p>
        </div>

        {variance.rule_id && (
          <p className="text-xs text-slate-500">
            Evaluated against rule <span className="font-mono">{variance.rule_id}</span>: {variance.explanation}
          </p>
        )}

        <div className="border-t border-slate-100 pt-4">
          <div className="flex items-center justify-between">
            <p className="text-xs uppercase text-slate-400">AI Explanation</p>
            <button
              onClick={handleExplain}
              disabled={explaining}
              className="rounded-md bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-200 disabled:opacity-50"
            >
              {explaining ? "Generating…" : variance.ai_explanation ? "Regenerate" : "Generate Explanation"}
            </button>
          </div>
          {variance.ai_explanation && (
            <p className="mt-2 rounded-md bg-slate-50 p-3 text-sm text-slate-700">{variance.ai_explanation}</p>
          )}
        </div>

        <div className="border-t border-slate-100 pt-4">
          <p className="text-xs uppercase text-slate-400">Resolution Status</p>
          <ResolutionBadge value={variance.resolution_status} />
        </div>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
        <h2 className="font-medium text-slate-900">Consultant Feedback</h2>
        <form onSubmit={handleFeedback} className="space-y-3">
          <div className="flex gap-4">
            {(["confirmed", "rejected", "needs_correction"] as const).map((opt) => (
              <label key={opt} className="flex items-center gap-1.5 text-sm text-slate-700">
                <input
                  type="radio"
                  name="action"
                  value={opt}
                  checked={action === opt}
                  onChange={() => setAction(opt)}
                />
                {opt}
              </label>
            ))}
          </div>
          <input
            value={consultant}
            onChange={(e) => setConsultant(e.target.value)}
            placeholder="Consultant name"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Notes"
            rows={3}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <button
            type="submit"
            disabled={submittingFeedback}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {submittingFeedback ? "Submitting…" : "Submit Feedback"}
          </button>
          {feedbackMessage && <p className="text-sm text-green-700">{feedbackMessage}</p>}
        </form>
      </div>
    </div>
  );
}
