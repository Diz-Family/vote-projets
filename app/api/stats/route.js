export async function GET(request) {
  const { searchParams } = new URL(request.url)
  const projet = searchParams.get('projet')
  const projetVotes = globalThis.votes?.[projet] || {}
  const notes = Object.values(projetVotes)
  const total = notes.length
  const moyenne = total > 0 ? Math.round((notes.reduce((a,b) => a+b, 0) / total) * 10) / 10 : 0
  const repartition = {}
  notes.forEach(n => { repartition[n] = (repartition[n] || 0) + 1 })
  return Response.json({ total, moyenne, repartition })
}
