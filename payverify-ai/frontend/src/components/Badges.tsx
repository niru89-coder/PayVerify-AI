const CLASSIFICATION_STYLES: Record<string, string> = {
  no_variance: "bg-green-100 text-green-800",
  component_not_calculated_one_side: "bg-amber-100 text-amber-800",
  amount_mismatch_within_tolerance: "bg-blue-100 text-blue-800",
  amount_mismatch_beyond_tolerance: "bg-red-100 text-red-800",
  rate_slab_mismatch: "bg-orange-100 text-orange-800",
  eligibility_mismatch: "bg-purple-100 text-purple-800",
  data_quality_issue: "bg-pink-100 text-pink-800",
};

const SUGGESTION_STYLES: Record<string, string> = {
  platform_correct_client_review: "bg-sky-100 text-sky-800",
  client_correct_platform_review: "bg-teal-100 text-teal-800",
  inconclusive_clarification_required: "bg-gray-200 text-gray-800",
  not_applicable: "bg-slate-100 text-slate-600",
};

function humanize(value: string): string {
  return value
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export function ClassificationBadge({ value }: { value: string }) {
  const style = CLASSIFICATION_STYLES[value] ?? "bg-slate-100 text-slate-700";
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${style}`}>
      {humanize(value)}
    </span>
  );
}

export function SuggestionBadge({ value }: { value: string }) {
  const style = SUGGESTION_STYLES[value] ?? "bg-slate-100 text-slate-700";
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${style}`}>
      {humanize(value)}
    </span>
  );
}

export function ResolutionBadge({ value }: { value: string }) {
  const style: Record<string, string> = {
    open: "bg-slate-100 text-slate-700",
    pending_client: "bg-amber-100 text-amber-800",
    pending_internal: "bg-orange-100 text-orange-800",
    resolved: "bg-green-100 text-green-800",
  };
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${style[value] ?? "bg-slate-100 text-slate-700"}`}>
      {humanize(value)}
    </span>
  );
}
