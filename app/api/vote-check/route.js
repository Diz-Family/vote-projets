export async function GET(request) {
  const { searchParams } = new URL(request.url)
  const projet = searchParams.get('projet')
  const voter = searchParams.get('voter')
  const projetVotes = globalThis.votes?.[projet] || {}
  const note = projetVotes[voter]
  return Response.json({ voted: note !== undefined, note: note || null })
}
