import { CandidatesExplorer } from "@/components/CandidatesExplorer";
import { getCandidates } from "@/lib/api";

export default async function CandidatesPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const candidates = await getCandidates();
  const params = await searchParams;

  return <CandidatesExplorer candidates={candidates} query={params.q} />;
}

