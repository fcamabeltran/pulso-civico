import { CompareBuilder } from "@/components/CompareBuilder";
import { getCandidates } from "@/lib/api";

export default async function ComparePage() {
  const candidates = await getCandidates();

  return <CompareBuilder candidates={candidates} />;
}

