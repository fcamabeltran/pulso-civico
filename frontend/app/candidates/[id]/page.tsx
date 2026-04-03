import Link from "next/link";
import { notFound } from "next/navigation";

import { CandidateProfile } from "@/components/CandidateProfile";
import { getCandidate, getFormulaMemberByName } from "@/lib/api";

export default async function CandidateDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  try {
    const { id } = await params;
    const candidate = await getCandidate(id);
    const hvMember = await getFormulaMemberByName(candidate.name);

    return (
      <main>
        <div className="section">
          <Link className="section-link" href="/candidates">
            ← Volver a candidatos
          </Link>
        </div>
        <CandidateProfile candidate={candidate} hvMember={hvMember} />
      </main>
    );
  } catch {
    notFound();
  }
}

