export async function GET() {
  return Response.json(globalThis.projets || [])
}
export async function POST(request) {
  const data = await request.json()
  if ((globalThis.projets || []).length >= 50) return Response.json({error:'Max 50 projets'}, {status:400})
  const projet = { id: Date.now().toString(), nom: data.nom, description: data.description || '' }
  if (!globalThis.projets) globalThis.projets = []
  globalThis.projets.push(projet)
  return Response.json(globalThis.projets)
}
