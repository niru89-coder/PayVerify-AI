"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export function EmployeeMasterUploader({ projectId, onUploaded }: { projectId: number; onUploaded?: () => void }) {
  const [status, setStatus] = useState<"idle" | "uploading" | "done" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);

  async function handleFile(file: File) {
    setStatus("uploading");
    setMessage(null);
    try {
      const result = await api.uploadEmployeeMaster(projectId, file);
      setStatus("done");
      setMessage(`Processed ${result.rows_processed} rows (${result.employees_created} new employees).`);
      onUploaded?.();
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 space-y-3">
      <h3 className="font-medium text-slate-900">Employee Master</h3>
      <p className="text-xs text-slate-500">
        CSV columns: id, dob, age, nationality, is_pr, elected_pre_1998, doj, doe,
        unpaid_leave_days, employment_type, is_director_fee_only.
      </p>
      <input
        type="file"
        accept=".csv"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        className="block w-full text-sm text-slate-600 file:mr-4 file:rounded-md file:border-0 file:bg-indigo-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-indigo-700 hover:file:bg-indigo-100"
      />
      {status === "uploading" && <p className="text-sm text-slate-500">Uploading…</p>}
      {message && (
        <p className={`text-sm ${status === "error" ? "text-red-600" : "text-green-700"}`}>{message}</p>
      )}
    </div>
  );
}
