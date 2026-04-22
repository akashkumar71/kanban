"use client";

import { useState, type FormEvent } from "react";
import { checkCredentials, signIn } from "@/lib/auth";

interface Props {
  onSignIn: () => void;
}

export const SignInPage = ({ onSignIn }: Props) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (checkCredentials(username, password)) {
      signIn();
      onSignIn();
    } else {
      setError("Invalid username or password.");
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden">
      <div className="pointer-events-none absolute left-0 top-0 h-[420px] w-[420px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(32,157,215,0.25)_0%,_rgba(32,157,215,0.05)_55%,_transparent_70%)]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[520px] w-[520px] translate-x-1/4 translate-y-1/4 rounded-full bg-[radial-gradient(circle,_rgba(117,57,145,0.18)_0%,_rgba(117,57,145,0.05)_55%,_transparent_75%)]" />

      <div className="relative w-full max-w-sm rounded-[32px] border border-[var(--stroke)] bg-white/90 p-10 shadow-[var(--shadow)] backdrop-blur">
        <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
          Single Board Kanban
        </p>
        <h1 className="mt-3 font-display text-3xl font-semibold text-[var(--navy-dark)]">
          Kanban Studio
        </h1>
        <p className="mt-2 text-sm leading-6 text-[var(--gray-text)]">
          Sign in to access your board.
        </p>

        <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-4" data-testid="sign-in-form">
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="username"
              className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)]"
            >
              Username
            </label>
            <input
              id="username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(e) => { setUsername(e.target.value); setError(""); }}
              className="rounded-xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)] focus:ring-2 focus:ring-[var(--primary-blue)]/20"
              placeholder="username"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="password"
              className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)]"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => { setPassword(e.target.value); setError(""); }}
              className="rounded-xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)] focus:ring-2 focus:ring-[var(--primary-blue)]/20"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <p role="alert" className="text-sm font-medium text-red-500">
              {error}
            </p>
          )}

          <button
            type="submit"
            className="mt-2 rounded-xl bg-[var(--primary-blue)] px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:opacity-90 active:scale-[0.98]"
          >
            Sign in
          </button>
        </form>
      </div>
    </div>
  );
};
