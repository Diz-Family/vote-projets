export const metadata = { title: 'Vote Projets', viewport: 'width=device-width, initial-scale=1, user-scalable=no' }
export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body style={{margin:0, padding:0, fontFamily:'-apple-system, BlinkMacSystemFont, sans-serif', background:'#f0f2f5'}}>
        {children}
      </body>
    </html>
  )
}
