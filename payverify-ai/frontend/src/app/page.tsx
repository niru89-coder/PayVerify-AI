"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, Project } from "@/lib/api";

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listProjects()
      .then(setProjects)
      .catch((err) => setError(String(err.message ?? err)));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Projects</h1>
          <p className="text-sm text-slate-500">
            Client vs Platform vs Rule-Engine parallel-run validation projects.
          </p>
        </div>
        <Link
          href="/projects/new"
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
        >
          + New Project
        </Link>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 border border-red-200 p-4 text-sm text-red-700">
          Could not reach the API at the configured base URL. Make sure the FastAPI backend
          is running ({error}).
        </div>
      )}

      {projects && projects.length === 0 && (
        <div className="rounded-md border border-dashed border-slate-300 p-8 text-center text-slate-500">
          No projects yet. Create your first project to begin a parallel-run validation.
        </div>
      )}

      {projects && projects.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left text-xs font-medium uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Country</th>
                <th className="px-4 py-3">Pay Period</th>
                <th className="px-4 py-3">Created</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {projects.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{p.name}</td>
                  <td className="px-4 py-3 text-slate-600">{p.country}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {p.pay_period_year}-{String(p.pay_period_month).padStart(2, "0")}
                  </td>
                  <td className="px-4 py-3 text-slate-500">
                    {new Date(p.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link href={`/projects/${p.id}`} className="text-indigo-600 hover:underline">
                      Open →
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

