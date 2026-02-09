import "./globals.css";

export const metadata = {
  title: "Medical Disability Review - Form DWC032 to DWC068/69/73",
  description: "Modern DWC Form Management and Generator - Medical IDP System",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="antialiased">
        <main className="min-h-screen flex flex-col">
          <header className="sticky top-0 z-50 w-full border-b border-slate-200 bg-white-80 backdrop-blur-md">
            <div className="container mx-auto flex h-16 items-center justify-between">
              <div className="flex items-center gap-3">
                <div>
                  <h1 className="text-lg font-bold tracking-tight text-slate-900 m-0 leading-none">
                    Medical Disability Review
                  </h1>
                  <p className="text-xs-caps uppercase tracking-widest text-slate-500 font-bold mt-1">
                    Form DWC032 to DWC068/69/73
                  </p>
                </div>
              </div>
            </div>
          </header>

          <div className="flex-grow">
            {children}
          </div>

          <footer className="mt-20 border-t border-slate-200 py-16 bg-white">
            <div className="container mx-auto text-center">
              <p className="text-sm text-slate-400 font-bold uppercase tracking-[0.2em] mb-2">
                Medical IDP System
              </p>
              <p className="text-xs text-slate-500 font-medium">
                &copy; {new Date().getFullYear()} Professional Disability Review Tool. All rights reserved.
              </p>
            </div>
          </footer>
        </main>
      </body>
    </html>
  );
}
