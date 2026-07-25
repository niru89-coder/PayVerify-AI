"use client";

import Link from "next/link";
import { useEffect, useState, use as usePromise } from "react";
import { api, Project, ValidationRunResult } from "@/lib/api";
import { EmployeeMasterUploader } from "@/components/EmployeeMasterUploader";
import { RegisterUploader } from "@/components/RegisterUploader";
import { ClassificationBadge } from "@/components/Badges";

export default function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = usePromise(params);
  const projectId = Number(id);

  const [project, setProject] = useState<Project | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [validating, setValidating] = useState(false);
  const [result, setResult] = useState<ValidationRunResult | null>(null);

  useEffect(() => {
    api.getProject(projectId).then(setProject).catch((err) => setError(String(err.message ?? err)));
  }, [projectId]);

  async function handleValidate() {
    setValidating(true);
    setError(null);
    try {
      const r = await api.runValidation(projectId);
      setResult(r);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setValidating(false);
    }
  }

  if (error && !project) {
    return <p className="text-sm text-red-600">{error}</p>;
  }
  if (!project) {
    return <p className="text-sm text-slate-500">Loading…</p>;
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">{project.name}</h1>
        <p className="text-sm text-slate-500">
          {project.country} · Pay period {project.pay_period_year}-{String(project.pay_period_month).padStart(2, "0")}
        </p>
      </div>

      <section className="space-y-4">
        <h2 className="text-lg font-medium text-slate-800">1. Upload Data</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <EmployeeMasterUploader projectId={projectId} />
          <RegisterUploader projectId={projectId} registerType="client" label="Client Register" />
          <RegisterUploader projectId={projectId} registerType="platform" label="Platform (Darwinbox) Register" />
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-medium text-slate-800">2. Run Validation</h2>
        <div className="rounded-lg border border-slate-200 bg-white p-5 space-y-4">
          <p className="text-sm text-slate-600">
            Runs the deterministic rule engine and reconciliation engine across every employee,
            comparing Client vs Platform vs Rule-Engine expected values.
          </p>
          <button
            onClick={handleValidate}
            disabled={validating}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {validating ? "Running validation…" : "Run Validation"}
          </button>

          {error && <p className="text-sm text-red-600">{error}</p>}

          {result && (
            <div className="space-y-3 border-t border-slate-100 pt-4">
              <p className="text-sm text-slate-700">
                {result.variances_created} employee × component comparisons evaluated.
              </p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(result.classification_summary).map(([classification, count]) => (
                  <span key={classification} className="flex items-center gap-1.5">
                    <ClassificationBadge value={classification} />
                    <span className="text-xs text-slate-500">×{count}</span>
                  </span>
                ))}
              </div>
              <Link
                href={`/projects/${projectId}/variances`}
                className="inline-block rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
              >
                View Variance Dashboard →
              </Link>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
