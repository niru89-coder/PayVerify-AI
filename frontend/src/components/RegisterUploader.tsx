"use client";

import { useState } from "react";
import { api, MappingSuggestion } from "@/lib/api";

const CANONICAL_COMPONENTS = [
  "", "EMPLOYEE_ID", "EMPLOYEE_NAME", "DATE_OF_BIRTH", "NATIONALITY", "IS_PERMANENT_RESIDENT",
  "ELECTED_BEFORE_1998_08_01", "DATE_OF_JOINING", "DATE_OF_EXIT", "UNPAID_LEAVE_DAYS",
  "EMPLOYMENT_TYPE", "IS_DIRECTOR_FEE_ONLY", "BASIC", "TRANSPORT_ALLOWANCE", "FIXED_ALLOWANCE",
  "OT_NORMAL", "OT_REST_DAY", "OT_PUBLIC_HOLIDAY", "EPF_EMPLOYEE", "EPF_EMPLOYER",
  "SOCSO_EMPLOYEE", "SOCSO_EMPLOYER", "EIS_EMPLOYEE", "EIS_EMPLOYER", "HRDF_LEVY", "PCB",
];

interface Props {
  projectId: number;
  registerType: "client" | "platform";
  label: string;
  onUploaded?: () => void;
}

export function RegisterUploader({ projectId, registerType, label, onUploaded }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [suggestions, setSuggestions] = useState<MappingSuggestion[] | null>(null);
  const [overrides, setOverrides] = useState<Record<string, string>>({});
  const [status, setStatus] = useState<"idle" | "previewing" | "ready" | "uploading" | "done" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);

  async function handleFileSelected(selected: File) {
    setFile(selected);
    setStatus("previewing");
    setMessage(null);
    try {
      const preview = await api.previewRegisterMapping(projectId, selected);
      setSuggestions(preview.suggestions);
      const initial: Record<string, string> = {};
      preview.suggestions.forEach((s) => {
        initial[s.source_column] = s.canonical_code ?? "";
      });
      setOverrides(initial);
      setStatus("ready");
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : String(err));
    }
  }

  async function handleConfirm() {
    if (!file) return;
    setStatus("uploading");
    setMessage(null);
    const columnMap: Record<string, string> = {};
    Object.entries(overrides).forEach(([col, code]) => {
      if (code) columnMap[col] = code;
    });
    try {
      const result = await api.uploadRegister(projectId, registerType, file, columnMap);
      setStatus("done");
      setMessage(
        `Uploaded ${result.row_count} rows (${result.employees_created} new employees, ${result.employees_matched} matched).`
      );
      onUploaded?.();
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 space-y-4">
      <h3 className="font-medium text-slate-900">{label}</h3>

      <input
        type="file"
        accept=".csv"
        onChange={(e) => e.target.files?.[0] && handleFileSelected(e.target.files[0])}
        className="block w-full text-sm text-slate-600 file:mr-4 file:rounded-md file:border-0 file:bg-indigo-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-indigo-700 hover:file:bg-indigo-100"
      />

      {status === "previewing" && <p className="text-sm text-slate-500">Analyzing column headers…</p>}

      {suggestions && status !== "previewing" && (
        <div className="space-y-3">
          <p className="text-xs text-slate-500">
            Review the suggested column mapping below. Columns with low confidence are highlighted -
            adjust the dropdown if the suggestion is wrong, or leave blank to ignore that column.
          </p>
          <div className="max-h-64 overflow-y-auto rounded-md border border-slate-100">
            <table className="min-w-full text-xs">
              <thead className="bg-slate-50 text-left uppercase text-slate-500">
                <tr>
                  <th className="px-3 py-2">Source Column</th>
                  <th className="px-3 py-2">Suggested</th>
                  <th className="px-3 py-2">Confidence</th>
                  <th className="px-3 py-2">Confirm Mapping</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {suggestions.map((s) => (
                  <tr key={s.source_column} className={s.method !== "exact" ? "bg-amber-50" : undefined}>
                    <td className="px-3 py-2 font-medium text-slate-800">{s.source_column}</td>
                    <td className="px-3 py-2 text-slate-600">{s.canonical_code ?? "—"}</td>
                    <td className="px-3 py-2 text-slate-600">{Math.round(s.confidence * 100)}%</td>
                    <td className="px-3 py-2">
                      <select
                        value={overrides[s.source_column] ?? ""}
                        onChange={(e) =>
                          setOverrides((prev) => ({ ...prev, [s.source_column]: e.target.value }))
                        }
                        className="rounded border border-slate-300 px-2 py-1 text-xs"
                      >
                        {CANONICAL_COMPONENTS.map((code) => (
                          <option key={code || "blank"} value={code}>
                            {code || "(ignore)"}
                          </option>
                        ))}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button
            onClick={handleConfirm}
            disabled={status === "uploading"}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {status === "uploading" ? "Uploading…" : "Confirm Mapping & Upload"}
          </button>
        </div>
      )}

      {message && (
        <p className={`text-sm ${status === "error" ? "text-red-600" : "text-green-700"}`}>{message}</p>
      )}
    </div>
  );
}
