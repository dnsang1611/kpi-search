import { Open_Sans } from 'next/font/google'
import "./index.css"

const openSans = Open_Sans({ subsets: ['latin'], display: 'swap' })

export const metadata = {
  title: 'MMSearch',
  description: 'Multimedia Video Retrieval Website',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={openSans.className}>
      <body>
        {children}
      </body>
    </html>
  )
}