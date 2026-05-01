export async function POST() {
  globalThis.votes = {}
  globalThis.projetActif = null
  return Response.json({ok: true})
}
