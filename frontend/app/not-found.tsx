import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[var(--surface-dark,#0B0E14)] text-[var(--text,#F1F5F9)] flex flex-col items-center justify-center p-6 text-center">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo-500/10 text-indigo-400 text-3xl font-bold mb-4 border border-indigo-500/20">
        404
      </div>
      <h1 className="text-2xl font-bold mb-2">Page Not Found</h1>
      <p className="text-sm text-slate-400 max-w-md mb-6">
        The requested route could not be found or has been relocated.
      </p>
      <Link
        href="/"
        className="px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-colors"
      >
        Return to Home
      </Link>
    </div>
  );
}
