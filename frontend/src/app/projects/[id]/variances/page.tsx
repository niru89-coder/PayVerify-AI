"use client";

import Link from "next/link";
import { useEffect, useState, use as usePromise } from "react";
import { api, Variance } from "@/lib/api";
import { ClassificationBadge, ResolutionBadge, SuggestionBadge } from "@/components/Badges";

const CLASSIFICATIONS = [
  "no_variance",
  "component_not_calculated_one_side",
  "amount_mismatch_within_tolerance",
  "amount_mismatch_beyond_tolerance",
  "rate_slab_mismatch",
  "eligibility_mismatch",
  "data_quality_issue",
];

export default function VarianceDashboardPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = usePromise(params);
  const projectId = Number(id);

  const [variances, setVariances] = useState<Variance[] | null>(null);
  const [classificationFilter, setClassificationFilter] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listVariances(projectId, classificationFilter ? { classification: classificationFilter } : undefined)
      .then(setVariances)
      .catch((err) => setError(String(err.message ?? err)));
  }, [projectId, classificationFilter]);

  const nonBaseline = variances?.filter((v) => v.classification !== "no_variance") ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Variance Dashboard</h1>
          <p className="text-sm text-slate-500">
            {variances ? `${variances.length} total, ${nonBaseline.length} require attention` : "Loading…"}
          </p>
        </div>
        <select
          value={classificationFilter}
          onChange={(e) => setClassificationFilter(e.target.value)}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">All classifications</option>
          {CLASSIFICATIONS.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {variances && (
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left text-xs font-medium uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Employee</th>
                <th className="px-4 py-3">Component</th>
                <th className="px-4 py-3">Client</th>
                <th className="px-4 py-3">Platform</th>
                <th className="px-4 py-3">Expected</th>
                <th className="px-4 py-3">Classification</th>
                <th className="px-4 py-3">Suggestion</th>
                <th className="px-4 py-3">Confidence</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {variances.map((v) => (
                <tr key={v.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-700">#{v.employee_id}</td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-700">{v.component_code}</td>
                  <td className="px-4 py-3 text-slate-600">{v.client_value ?? "—"}</td>
                  <td className="px-4 py-3 text-slate-600">{v.platform_value ?? "—"}</td>
                  <td className="px-4 py-3 text-slate-600">{v.expected_value ?? "—"}</td>
                  <td className="px-4 py-3">
                    <ClassificationBadge value={v.classification} />
                  </td>
                  <td className="px-4 py-3">
                    <SuggestionBadge value={v.suggestion_outcome} />
                  </td>
                  <td className="px-4 py-3 text-slate-600">{Math.round(v.confidence_score * 100)}%</td>
                  <td className="px-4 py-3">
                    <ResolutionBadge value={v.resolution_status} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link href={`/projects/${projectId}/variances/${v.id}`} className="text-indigo-600 hover:underline">
                      Review →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
