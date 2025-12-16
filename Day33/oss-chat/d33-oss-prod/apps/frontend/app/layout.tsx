import "./globals.css";

export const metadata = {
  title: "d33-oss-prod Chat",
  description: "Next.js chat UI for FastAPI + Ollama"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="container">{children}</div>
      </body>
    </html>
  );
}
