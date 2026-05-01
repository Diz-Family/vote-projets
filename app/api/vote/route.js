export async function POST(request) {
  const { projet, voter, note } = await request.json()
  if (!globalThis.votes) globalThis.votes = {}
  if (!globalThis.votes[projet]) globalThis.votes[projet] = {}
  globalThis.votes[projet][voter] = note
  return Response.json({ok: true})
}
