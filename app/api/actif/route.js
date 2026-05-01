export async function GET() {
  return Response.json(globalThis.projetActif || null)
}
export async function POST(request) {
  const data = await request.json()
  if (data.id) {
    globalThis.projetActif = (globalThis.projets || []).find(p => p.id === data.id) || null
  } else {
    globalThis.projetActif = null
  }
  return Response.json({ok: true})
}
