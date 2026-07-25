"use client";

import { useEffect, useState } from "react";
import { api, RuleSummary } from "@/lib/api";

export default function RulesPage() {
  const [rules, setRules] = useState<RuleSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listRules().then(setRules).catch((err) => setError(String(err.message ?? err)));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Rule Catalog</h1>
        <p className="text-sm text-slate-500">
          Deterministic statutory rules implemented in the rule engine, with full traceability
          back to source documents.
        </p>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {rules && (
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left text-xs font-medium uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Rule ID</th>
                <th className="px-4 py-3">Component</th>
                <th className="px-4 py-3">Country</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Version</th>
                <th className="px-4 py-3">Effective Date</th>
                <th className="px-4 py-3">Source Document</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rules.map((r) => (
                <tr key={r.rule_id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono text-xs text-slate-800">{r.rule_id}</td>
                  <td className="px-4 py-3 text-slate-700">{r.component}</td>
                  <td className="px-4 py-3 text-slate-600">{r.country}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        r.status === "implemented"
                          ? "bg-green-100 text-green-800"
                          : "bg-amber-100 text-amber-800"
                      }`}
                    >
                      {r.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{r.version}</td>
                  <td className="px-4 py-3 text-slate-600">{r.effective_date}</td>
                  <td className="px-4 py-3 text-xs text-slate-500">{r.source_document}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
